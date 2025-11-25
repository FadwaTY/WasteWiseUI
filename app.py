import os
import streamlit as st
from PIL import Image
import io
import requests
import base64
import json


# --------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------
st.set_page_config(
    page_title="WasteWise – AI Waste Classification",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------
# INITIALISATION DES VARIABLES DE SESSION
# --------------------------------------------------------
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'detection'
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# --------------------------------------------------------
# CONFIGURATION API
# --------------------------------------------------------
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['cloud_api_uri']
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
API_URL = BASE_URI + 'detect'

# --------------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------------
premium_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

body {
    background-color: #E8F5E9;
}

.stApp {
    background-color: #E8F5E9;
}

/* Masquer les éléments Streamlit par défaut */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

section.main > div {
    padding-top: 0rem;
}

/* Header personnalisé */
.custom-header {
    background: linear-gradient(135deg, #2E7D32 0%, #388E3C 100%);
    padding: 15px 50px;
    border-radius: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 20px 50px 40px 50px;
    box-shadow: 0 8px 25px rgba(46, 125, 50, 0.2);
}

.custom-header .logo {
    display: flex;
    align-items: center;
    color: white;
    font-size: 28px;
    font-weight: 700;
    gap: 12px;
}

.custom-header .logo span {
    font-size: 32px;
}

.custom-header .nav-buttons {
    display: flex;
    gap: 10px;
}

.nav-btn {
    background-color: rgba(255, 255, 255, 0.1);
    color: #B2DFDB;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
}

.nav-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    transform: translateY(-2px);
}

.nav-btn.active {
    background-color: #4CAF50;
    color: white;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

/* Cartes de contenu */
.glass-card {
    background: white;
    padding: 35px;
    border-radius: 25px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    margin-bottom: 25px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.12);
}

/* Titres */
h1 {
    font-size: 42px;
    color: #2E7D32;
    font-weight: 700;
    margin-bottom: 15px;
}

h2 {
    font-size: 32px;
    color: #388E3C;
    font-weight: 600;
    margin-bottom: 20px;
}

h3 {
    font-size: 26px;
    color: #4CAF50;
    font-weight: 600;
    margin-bottom: 15px;
}

p {
    color: #555;
    font-size: 16px;
    line-height: 1.6;
}

.subheader-text {
    font-size: 19px;
    color: #757575;
    margin-bottom: 35px;
    font-weight: 400;
}

/* Zone d'upload */
.upload-zone {
    border: 3px dashed #4CAF50;
    padding: 40px;
    border-radius: 25px;
    background: linear-gradient(135deg, #FFFFFF 0%, #F1F8F4 100%);
    text-align: center;
    transition: all 0.4s ease;
    cursor: pointer;
    min-height: 350px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.upload-zone:hover {
    border-color: #2E7D32;
    background: linear-gradient(135deg, #F1F8F4 0%, #E8F5E9 100%);
    transform: scale(1.02);
}

/* Boutons */
.stButton button {
    background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
    color: white;
    padding: 14px 28px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
    width: 100%;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.stButton button:hover {
    background: linear-gradient(135deg, #388E3C 0%, #2E7D32 100%);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.stButton button:active {
    transform: translateY(-1px);
}

/* Barre de progression */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4CAF50 0%, #66BB6A 100%);
    border-radius: 10px;
}

.stProgress > div > div > div {
    background-color: #E0F2F1;
    border-radius: 10px;
    height: 20px;
}

/* Carte de résultat */
.result-card {
    background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
    padding: 30px;
    border-radius: 20px;
    border-left: 6px solid #4CAF50;
    margin: 20px 0;
}

.confidence-badge {
    display: inline-block;
    background: #4CAF50;
    color: white;
    padding: 8px 20px;
    border-radius: 25px;
    font-weight: 600;
    font-size: 18px;
    margin: 10px 0;
}

/* Images */
.stImage > img {
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

/* Alertes personnalisées */
.stAlert {
    border-radius: 15px;
    padding: 18px;
    margin: 15px 0;
    border-left: 5px solid;
}

/* Footer */
.custom-footer {
    text-align: center;
    color: #757575;
    padding: 40px;
    font-size: 14px;
    margin-top: 60px;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.6s ease-out;
}

/* Responsive */
@media (max-width: 768px) {
    .custom-header {
        flex-direction: column;
        gap: 20px;
        margin: 10px 20px 30px 20px;
        padding: 20px;
    }

    .custom-header .nav-buttons {
        flex-direction: column;
        width: 100%;
    }

    .nav-btn {
        width: 100%;
    }

    h1 {
        font-size: 32px;
    }
}
</style>
"""

st.markdown(premium_css, unsafe_allow_html=True)

# --------------------------------------------------------
# FONCTION: APPEL API
# --------------------------------------------------------
def predict_waste(image_bytes):
    try:
        response = requests.post(
            "http://localhost:8000/detect",
            files={"file": image_bytes}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la prédiction: {e}")
        return None


# --------------------------------------------------------
# FONCTION: HEADER
# --------------------------------------------------------
def render_header():
    """Affiche le header avec navigation"""
    pages = {
        'detection': ('📸', 'Détection en Direct'),
        'upload': ('🖼️', 'Analyser une Image'),
        'about': ('💡', 'À Propos')
    }

    active_btns = []
    for page_key, (icon, label) in pages.items():
        active_class = 'active' if st.session_state.current_page == page_key else ''
        active_btns.append(f'<button class="nav-btn {active_class}" onclick="changePage(\'{page_key}\')">{icon} {label}</button>')

    st.markdown(f"""
    <div class="custom-header">
        <div class="logo">
            <span>♻️</span>
            <div>WasteWise</div>
        </div>
        <div class="nav-buttons">
            {''.join(active_btns)}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE: DÉTECTION EN DIRECT
# --------------------------------------------------------
def page_detection():
    st.markdown("<div style='margin: 0 50px;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='fade-in'>📸 Détection en Direct</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Utilisez votre caméra pour classifier vos déchets instantanément</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        # Capture caméra
        camera_photo = st.camera_input("📷 Prendre une photo", key="camera_detection")

        if camera_photo:
            image_bytes = camera_photo.getvalue()
            st.image(image_bytes, use_container_width=True, caption="Photo capturée")

            if st.button("🔍 Analyser cette image", use_container_width=True):
                with st.spinner("🔄 Analyse en cours..."):
                    result = predict_waste(image_bytes)
                    if result:
                        st.session_state.prediction_result = result
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        if st.session_state.prediction_result:
            result = st.session_state.prediction_result

            st.markdown("<h3>✅ Résultat de l'analyse</h3>", unsafe_allow_html=True)

            category = result.get('category', 'Inconnu')
            confidence = float(result.get('confidence', 0))

            st.markdown(f"<h2>{category.upper()} ♻️</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='confidence-badge'>{confidence*100:.2f}%</div>", unsafe_allow_html=True)

            st.progress(confidence)
            st.caption("Niveau de confiance")

            if 'description' in result:
                st.info(f"ℹ️ {result['description']}")

            if 'recycling_tips' in result:
                st.success(f"♻️ **Conseil de tri:** {result['recycling_tips']}")

            if st.button("🔄 Nouvelle analyse", use_container_width=True):
                st.session_state.prediction_result = None
                st.rerun()
        else:
            st.info("👆 Prenez une photo pour commencer l'analyse")
            st.markdown("""
            <div style='padding: 20px; background: #F1F8F4; border-radius: 15px; margin-top: 20px;'>
                <h4 style='color: #2E7D32; margin-bottom: 10px;'>💡 Conseils pour de meilleurs résultats:</h4>
                <ul style='color: #555;'>
                    <li>Assurez un bon éclairage</li>
                    <li>Centrez le déchet dans le cadre</li>
                    <li>Évitez les reflets et ombres</li>
                    <li>Photographiez un seul objet à la fois</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE: UPLOAD IMAGE
# --------------------------------------------------------
# --------------------------------------------------------
# PAGE: UPLOAD IMAGE
# --------------------------------------------------------
def page_upload():
    st.markdown("<div style='margin: 0 50px;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='fade-in'>🖼️ Analyser une Image</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Téléversez une image pour obtenir une analyse du déchet</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1], gap="large")

    # --- LEFT SIDE : UPLOAD IMAGE ---
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        uploaded_image = st.file_uploader("📤 Importer une image", type=["jpg", "jpeg", "png"])

        if uploaded_image:
            image_bytes = uploaded_image.read()
            st.image(image_bytes, use_container_width=True, caption="Image importée")

            if st.button("🔍 Analyser cette image", use_container_width=True):
                with st.spinner("🔄 Analyse en cours..."):
                    result = predict_waste(image_bytes)
                    if result:
                        st.session_state.prediction_result = result
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # --- RIGHT SIDE : RESULTS ---
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        if st.session_state.prediction_result:
            result = st.session_state.prediction_result

            st.markdown("<h3>✅ Résultat de l'analyse</h3>", unsafe_allow_html=True)

            category = result.get('category', 'Inconnu')
            confidence = float(result.get('confidence', 0))

            st.markdown(f"<h2>{category.upper()} ♻️</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='confidence-badge'>{confidence*100:.2f}%</div>", unsafe_allow_html=True)

            st.progress(confidence)

            if 'description' in result:
                st.info(f"ℹ️ {result['description']}")

            if 'recycling_tips' in result:
                st.success(f"♻️ Conseil: {result['recycling_tips']}")

            if st.button("🔄 Nouvelle image", use_container_width=True):
                st.session_state.prediction_result = None
                st.rerun()

        else:
            st.info("📥 Importez une image pour commencer.")

        # --------------------------------------------------
        # ⭐ NEW: test_all section
        # --------------------------------------------------
        st.markdown("### 🔍 Tester le dataset complet (Backend)")

        if st.button("🚀 Lancer test_all", use_container_width=True):
            with st.spinner("📡 Récupération des résultats depuis le backend..."):
                result = test_all_api()
                if result:
                    st.success("Test dataset récupéré !")
                    st.json(result)

        # --------------------------------------------------

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------
# PAGE: À PROPOS
# --------------------------------------------------------
def page_about():
    st.markdown("<div style='margin: 0 50px;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='fade-in'>💡 À Propos de WasteWise</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Intelligence artificielle au service de l'environnement</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3>🎯 Notre Mission</h3>
        <p>WasteWise utilise l'intelligence artificielle pour faciliter le tri des déchets et promouvoir le recyclage.
        Notre objectif est de rendre le geste de tri accessible à tous grâce à la technologie.</p>

        <h3 style='margin-top: 30px;'>🤖 La Technologie</h3>
        <p>Notre modèle d'IA est entraîné sur des milliers d'images de déchets pour classifier avec précision:</p>
        <ul>
            <li>♻️ Plastique</li>
            <li>📄 Papier et carton</li>
            <li>🥫 Métaux</li>
            <li>🍶 Verre</li>
            <li>🗑️ Déchets organiques</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3>📈 Impact Environnemental</h3>
        <div style='background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 20px; border-radius: 15px; margin: 20px 0;'>
            <div style='text-align: center; margin: 15px 0;'>
                <div style='font-size: 36px; font-weight: 700; color: #2E7D32;'>10,000+</div>
                <div style='color: #555;'>Images analysées</div>
            </div>
            <div style='text-align: center; margin: 15px 0;'>
                <div style='font-size: 36px; font-weight: 700; color: #2E7D32;'>95%</div>
                <div style='color: #555;'>Précision moyenne</div>
            </div>
            <div style='text-align: center; margin: 15px 0;'>
                <div style='font-size: 36px; font-weight: 700; color: #2E7D32;'>5</div>
                <div style='color: #555;'>Catégories de déchets</div>
            </div>
        </div>

        <h3>🌍 Contribuez au Changement</h3>
        <p>Chaque déchet correctement trié contribue à un avenir plus durable.
        Utilisez WasteWise pour devenir un acteur du changement!</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------
# FOOTER
# --------------------------------------------------------
def render_footer():
    st.markdown("""
    <div class="custom-footer">
        <div style='margin-bottom: 15px;'>
            <span style='font-size: 32px;'>♻️</span>
        </div>
        <div style='font-size: 16px; font-weight: 500; color: #2E7D32; margin-bottom: 10px;'>
            WasteWise - Tri Intelligent par IA
        </div>
        <div>
            © 2024 WasteWise. Tous droits réservés.
        </div>
        <div style='margin-top: 10px; color: #999;'>
            Fait avec 💚 pour la planète
        </div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------
# NAVIGATION
# --------------------------------------------------------
def handle_navigation():
    """Gestion de la navigation entre les pages"""
    # Boutons de navigation (simulés via query params dans Streamlit)
    query_params = st.query_params

    if 'page' in query_params:
        st.session_state.current_page = query_params['page']

# --------------------------------------------------------
# MAIN APP
# --------------------------------------------------------
def main():
    # Header
    render_header()

    # Gestion de la navigation
    handle_navigation()

    # Routing des pages
    if st.session_state.current_page == 'detection':
        page_detection()
    elif st.session_state.current_page == 'upload':
        page_upload()
    elif st.session_state.current_page == 'about':
        page_about()

    # Footer
    render_footer()

if __name__ == "__main__":
    main()
