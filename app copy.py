import base64, io, os, json, hashlib, math
from collections import Counter
from typing import Dict
import requests
import streamlit as st
from PIL import Image

# -------------------- Page & Session State --------------------
st.set_page_config(page_title="WasteWise UI", layout="wide")

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "busy" not in st.session_state:
    st.session_state.busy = False
if "results" not in st.session_state:
    st.session_state.results = []   # [{name, orig_bytes, annotated_b64, counts}]
if "totals" not in st.session_state:
    st.session_state.totals = {}
if "recommendation" not in st.session_state:
    st.session_state.recommendation = ""
if "health" not in st.session_state:
    st.session_state.health = None

def reset_analysis():
    st.session_state.analyzed = False
    st.session_state.results = []
    st.session_state.totals = {}
    st.session_state.recommendation = ""

def norm_base(url: str) -> str:
    # strip spaces and accidental quotes; remove trailing slash
    return (url or "").strip().strip("'\"").rstrip("/")

# -------------------- Header --------------------
st.title("WasteWise - Sustainable Waste Detection")
st.caption("Upload image(s) to detect waste categories, visualize boxes, and get a batch recommendation.")

# -------------------- Sidebar: Settings & Health --------------------
BACKEND_DEFAULT = os.getenv("WW_BACKEND_URL", "http://localhost:8000")

with st.sidebar:
    st.header("Settings")
    raw_backend = st.text_input("Backend URL", BACKEND_DEFAULT)
    backend_url = norm_base(raw_backend)

    conf = st.slider("Confidence threshold", 0.05, 0.95, 0.25, 0.05)
    iou = st.slider("IoU threshold", 0.10, 0.90, 0.45, 0.05)

    st.divider()
    st.subheader("API Health")

    def do_health():
        try:
            st.session_state.health = requests.get(f"{backend_url}/healthz", timeout=10).json()
        except Exception as e:
            st.session_state.health = {"error": str(e)}

    st.button("Check /healthz", on_click=do_health)
    if st.session_state.health:
        st.json(st.session_state.health)

# -------------------- Uploader --------------------
uploaded_files = st.file_uploader(
    "Image(s):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# -------------------- Analysis Runner --------------------
def run_analysis(uploaded, backend_url, conf, iou):
    st.session_state.busy = True
    totals = Counter()
    results = []

    with st.spinner(f"Analyzing {len(uploaded)} image(s)..."):
        for up in uploaded:
            files = {"file": (up.name, up.getvalue(), up.type or "image/jpeg")}
            data = {"conf": str(conf), "iou": str(iou), "llm": "false"}  # skip LLM per image
            r = requests.post(f"{backend_url}/predict", files=files, data=data, timeout=120)
            r.raise_for_status()
            out = r.json()

            counts = {k.upper(): int(v) for k, v in out.get("counts", {}).items()}
            totals.update(counts)

            results.append({
                "name": up.name,
                "orig_bytes": up.getvalue(),
                "annotated_b64": out.get("annotated_image_b64", ""),
                "counts": counts,
            })

    # one LLM call for the entire batch
    try:
        r = requests.post(
            f"{backend_url}/recommend",
            json={"counts": dict(totals), "detections": []},
            timeout=120
        )
        r.raise_for_status()
        rec = r.json().get("recommendation", "") or ""
    except Exception as e:
        rec = f"_No recommendation available: {e}_"

    # persist results & flip flags
    st.session_state.results = results
    st.session_state.totals = dict(totals)
    st.session_state.recommendation = rec
    st.session_state.analyzed = True
    st.session_state.busy = False

    # hide the Analyze button immediately
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

# -------------------- Controls & Rendering --------------------
# Analyze button is visible only before a run
if not st.session_state.analyzed:
    clicked = st.button(
        "Analyze",
        type="primary",
        disabled=(st.session_state.busy or not uploaded_files),
        key="analyze_btn",
    )
    if clicked:
        run_analysis(uploaded_files, backend_url, conf, iou)

# Render persisted results so they survive reruns (e.g., health checks)
if st.session_state.analyzed:
    for res in st.session_state.results:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(res["name"])
            st.image(res["orig_bytes"], use_container_width=True)
        with c2:
            st.subheader("Detections")
            st.image(res["annotated_b64"], use_container_width=True)

    if st.session_state.totals:
        msg = ", ".join(f"{v} {k}" for k, v in Counter(st.session_state.totals).most_common())
        st.success(msg)

    if st.session_state.recommendation:
        st.markdown("### Recommendation")
        st.markdown(st.session_state.recommendation)

    st.button("New analysis", on_click=reset_analysis)
elif not uploaded_files:
    st.info("Upload one or more images to begin.")
