import streamlit as st
import requests
from PIL import Image
import io

# --------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------
st.set_page_config(
    page_title="WasteWise – AI Waste Classification",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_URI = "http://127.0.0.1:8000/"
API_URL = BASE_URI + "detect"      # corrected

# --------------------------------------------------------
# BACKEND FUNCTIONS
# --------------------------------------------------------
def predict_waste(image_file):
    try:
        # Convert image → bytes
        image_bytes = io.BytesIO()
        image_file.save(image_bytes, format=image_file.format)
        image_bytes.seek(0)

        # Request to backend
        response = requests.post(
            API_URL,
            files={"file": image_bytes}
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        st.error(f"Erreur lors de la prédiction: {e}")
        return None


def test_all_api():
    try:
        response = requests.get(TEST_ALL_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors du test_all: {e}")
        return None


# --------------------------------------------------------
# PAGE : Image Upload + Test Backend
# --------------------------------------------------------
def page_upload():
    st.title("📤 Tester une image")

    uploaded_file = st.file_uploader("Sélectionner une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image téléchargée", width=300)

        if st.button("🚀 Lancer la Détection", use_container_width=True):
            with st.spinner("🔍 Détection en cours..."):
                result = predict_waste(image)

            if result:
                st.success("Détection réussie 🎉")
                st.json(result)

    st.markdown("---")
    st.markdown("### 🔍 Tester le dataset complet (Backend)")

    if st.button("🚀 Lancer test_all", use_container_width=True):
        with st.spinner("📡 Récupération des résultats depuis le backend..."):
            result = test_all_api()
        if result:
            st.success("Résultat test_all :")
            st.json(result)


# --------------------------------------------------------
# PAGE : Camera
# --------------------------------------------------------
def page_camera():
    st.title("📷 Détection avec Caméra")

    img_bytes = st.camera_input("Prendre une photo")

    if img_bytes:
        image = Image.open(img_bytes)
        st.image(image, caption="Image capturée")

        if st.button("🚀 Lancer la Détection", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                result = predict_waste(image)

            if result:
                st.success("Détection réussie 🎉")
                st.json(result)


# --------------------------------------------------------
# MAIN NAVIGATION
# --------------------------------------------------------
tabs = st.tabs(["📤 Upload Image", "📷 Camera"])

with tabs[0]:
    page_upload()

with tabs[1]:
    page_camera()
