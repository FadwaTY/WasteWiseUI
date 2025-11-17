# WasteWiseUI/app.py

import os
import requests
from collections import Counter
import streamlit as st
import base64

# -------------------- Page & Session State --------------------
st.set_page_config(page_title="WasteWise UI", layout="wide")

# --- DESIGN TOKENS & GLOBAL STYLES (theme-aware) ---
brand = "#16A34A"
brand700 = "#15803D"

bg = st.get_option("theme.backgroundColor") or "#F8FAFC"
surface = st.get_option("theme.secondaryBackgroundColor") or "#FFFFFF"
text = st.get_option("theme.textColor") or "#0F172A"
primary = st.get_option("theme.primaryColor") or brand

st.markdown(f"""
<style>
/* ---------- Theme ↔ CSS variables ---------- */
:root {{
  --brand:{primary};
  --brand-700:{brand700};
  --bg:{bg};
  --surface:{surface};
  --text:{text};
  /* Health vars default (overridden by _apply_health_theme) */
  --health-bg:#64748B; --health-border:#475569; --health-text:#FFFFFF;
}}

/* App background & base text */
html, body, [data-testid="stAppViewContainer"], .block-container {{
  background: var(--bg) !important;
  color: var(--text);
}}

/* ---------- Buttons ---------- */
.stButton > button {{
  border-radius: 10px !important;
}}

/* Primary */
.stButton > button[data-testid="baseButton-primary"] {{
  background: var(--brand) !important;
  border: 1px solid var(--brand-700) !important;
  color: #fff !important;
}}
.stButton > button[data-testid="baseButton-primary"]:hover:not(:disabled) {{
  filter: brightness(0.95);
}}
.stButton > button[data-testid="baseButton-primary"]:active:not(:disabled) {{
  transform: translateY(0.5px);
}}

/* Secondary (outlined) */
.stButton > button[data-testid="baseButton-secondary"] {{
  background: var(--surface) !important;
  border: 1px solid var(--brand) !important;
  color: var(--brand-700) !important;
}}
.stButton > button[data-testid="baseButton-secondary"]:hover:not(:disabled) {{
  background: rgba(22, 163, 74, 0.06) !important;
}}

/* Sidebar health button (overrides primary/secondary inside sidebar) */
[data-testid="stSidebar"] .stButton > button {{
  background: var(--health-bg) !important;
  border: 1px solid var(--health-border) !important;
  color: var(--health-text) !important;
  border-radius: 10px !important;
}}

/* Sidebar surface to match theme */
[data-testid="stSidebar"] {{
  background: var(--surface) !important;
}}

/* ---------- Card look for containers ---------- */
/* Safe fallback for all bordered containers */
.stContainer {{
  background: var(--surface) !important;
  border-radius: 12px !important;
  padding: 1rem !important;
  border: 1px solid rgba(15, 23, 42, 0.10) !important; /* fallback border */
}}

/* Prefer narrower targeting if :has() is supported */
@supports(selector(:has(*))) {{
  .stContainer:has(> .stMarkdown, > .stFileUploader, > .stColumns, > .stJson, > .stImage) {{
    background: var(--surface) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    border: 1px solid rgba(15, 23, 42, 0.10) !important;
  }}
}}

/* Upgrade borders if color-mix is supported */
@supports (color: color-mix(in srgb, white, black)) {{
  .stContainer,
  .stContainer:has(*) {{
    border: 1px solid color-mix(in srgb, var(--text) 10%, transparent) !important;
  }}
}}

/* ---------- Inputs & feedback polish ---------- */
/* File uploader highlight */
[data-testid="stFileUploaderDropzone"] {{
  border-color: var(--brand) !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
  background: rgba(22, 163, 74, 0.04) !important;
}}

/* Slider thumb + track (uses stable attributes) */
[data-testid="stSlider"] [role="slider"] {{
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.18) !important;
}}
[data-baseweb="slider"] .progress-bar {{
  background: var(--brand) !important;
}}

/* ---------- Alerts ---------- */
[data-testid="stAlert"] {{
  border-radius: 10px !important;
  background: var(--brand) !important;
  border: 1px solid var(--brand-700) !important;
}}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] a {{
  color: #111827 !important;
}}

[data-testid="stAlert"] svg {{
  color:#111827 !important;
  fill: #ffffff !important;
}}

/* Force readable light text inside ALL alert variants */
[data-testid="stAlert"] * {{
  color: #111827 !important;
  fill: #ffffff !important;
}}

</style>
""", unsafe_allow_html=True)

# helper for health coloring (green/amber/red)
# replace your current _apply_health_theme with this:
def _apply_health_theme(status: str):
    palette = {
        "ok":      ("#16A34A", "#15803D", "#FFFFFF"),
        "partial": ("#F59E0B", "#D97706", "#111827"),
        "bad":     ("#DC2626", "#B91C1C", "#FFFFFF"),
        "default": ("#64748B", "#475569", "#FFFFFF"),
    }
    bg, bd, tx = palette.get(status, palette["default"])
    # Scope to the sidebar so the button inside always inherits the latest values
    st.markdown(
        f"<style>[data-testid='stSidebar']{{--health-bg:{bg};--health-border:{bd};--health-text:{tx};}}</style>",
        unsafe_allow_html=True
    )

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
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def reset_analysis():
    st.session_state.analyzed = False
    st.session_state.results = []
    st.session_state.totals = {}
    st.session_state.recommendation = ""
    st.session_state.uploader_key += 1

def norm_base(url: str) -> str:
    # strip spaces/quotes; remove trailing slash
    return (url or "").strip().strip("'\"").rstrip("/")

# -------------------- Header --------------------
st.title("WasteWise - Sustainable Waste Detection")
st.caption("Upload image(s) to detect waste categories, and generate a batch recommendation.")

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
    # placeholder that we update each run
    health_css = st.empty()

    def do_health():
        try:
            st.session_state.health = requests.get(f"{backend_url}/healthz", timeout=10).json()
        except Exception as e:
            st.session_state.health = {"error": str(e)}

    # derive status from last result
    h = st.session_state.health
    status = "default"
    if isinstance(h, dict):
        if h.get("error"):
            status = "bad"
        elif h.get("status") in ("ok", True) or h.get("ok") is True:
            status = "ok"
        elif h.get("status") in ("partial", "degraded", "warn"):
            status = "partial"
        else:
            status = "bad"

    # apply scoped vars via the placeholder so it overwrites each rerun
    palette = {
        "ok":      ("#16A34A", "#15803D", "#FFFFFF"),
        "partial": ("#F59E0B", "#D97706", "#111827"),
        "bad":     ("#DC2626", "#B91C1C", "#FFFFFF"),
        "default": ("#64748B", "#475569", "#FFFFFF"),
    }
    bg, bd, tx = palette.get(status, palette["default"])
    health_css.markdown(
        f"<style>[data-testid='stSidebar']{{--health-bg:{bg};--health-border:{bd};--health-text:{tx};}}</style>",
        unsafe_allow_html=True
    )

    st.button("Check /healthz", type="primary", key="health_btn", on_click=do_health)

    if st.session_state.health:
        st.json(st.session_state.health)


# -------------------- Uploader --------------------
# --- Load files (card) ---
with st.container(border=True):
    st.subheader("Load files")
    uploaded_files = st.file_uploader(
        "Image(s):",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}" if "uploader_key" in st.session_state else None
    )

# -------------------- Analysis (detections only) --------------------
def run_analysis(uploaded, backend_url, conf, iou):
    st.session_state.busy = True
    totals = Counter()
    results = []

    # live containers to render as we go
    holders = [st.container() for _ in uploaded]

    for idx, up in enumerate(uploaded):
        with holders[idx]:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(up.name)
                st.image(up, use_container_width=True)
            with c2:
                st.info("Detecting...")

        files = {"file": (up.name, up.getvalue(), up.type or "image/jpeg")}
        data = {"conf": str(conf), "iou": str(iou), "llm": "false"}  # <-- LLM OFF here
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

        # update the right column with the annotated image immediately
        with holders[idx]:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(up.name)
                st.image(up, use_container_width=True)
            with c2:
                st.subheader("Detections")
                st.image(out.get("annotated_image_b64", ""), use_container_width=True)

    # persist results & flip flags
    st.session_state.results = results
    st.session_state.totals = dict(totals)
    st.session_state.analyzed = True
    st.session_state.busy = False

    # do NOT call the LLM here; recommendation happens via its own button
    # optional: trigger a light rerun to hide the Analyze button
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

# -------------------- Controls & Rendering --------------------
# Analyze button (visible only before a run)
if not st.session_state.analyzed:
    clicked = st.button(
        "Analyze",
        type="primary",
        disabled=(st.session_state.busy or not uploaded_files),
        key="analyze_btn",
    )
    if clicked:
        run_analysis(uploaded_files, backend_url, conf, iou)

# --- Images (cards) ---
if st.session_state.analyzed:
    for res in st.session_state.results:
        with st.container(border=True):
            st.subheader("Image")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Original**")
                st.image(res["orig_bytes"], use_container_width=True)
            with c2:
                st.markdown("**Detections**")
                st.image(res["annotated_b64"], use_container_width=True)

    # --- Detection summary (card) ---
    if st.session_state.totals:
        msg = ", ".join(f"{v} {k}" for k, v in Counter(st.session_state.totals).most_common())
        with st.container(border=True):
            st.subheader("Detection summary")
            st.success(f"- Detection: {msg}")

    # --- Recommendations (card) ---
    with st.container(border=True):
        st.subheader("Recommendations")

        if st.session_state.analyzed:
            if st.session_state.recommendation:
                st.markdown(st.session_state.recommendation)
            else:
                if st.button("Generate recommendation", type="primary", key="gen_reco_btn"):
                    with st.spinner("Generating recommendation..."):
                        try:
                            r = requests.post(
                                f"{backend_url}/recommend",
                                json={"counts": st.session_state.totals, "detections": []},
                                timeout=120
                            )
                            r.raise_for_status()
                            st.session_state.recommendation = r.json().get("recommendation", "") or "_No recommendation returned_"
                            try:
                                st.rerun()
                            except Exception:
                                st.experimental_rerun()
                        except Exception as e:
                            st.warning(f"Could not generate recommendation: {e}")
        else:
            st.info("Run Analyze first to enable recommendations.")

    st.button("New analysis", type="secondary", on_click=reset_analysis)

elif not uploaded_files:
    st.info("Upload one or more images to begin.")
