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
    BASE_URI = st.secrets.get(os.environ.get('API_URI'), 'http://localhost:8000')
else:
    BASE_URI = st.secrets.get('cloud_api_uri', 'http://localhost:8000')
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
API_URL = BASE_URI + 'predict'

# --------------------------------------------------------
# CUSTOM CSS - DESIGN MODERNE INSPIRÉ DE L'IMAGE
# --------------------------------------------------------
modern_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Masquer éléments par défaut */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Background principal */
.stApp {
    background: linear-gradient(135deg, #1e3a34 0%, #2d5548 50%, #3d6b5c 100%);
    min-height: 100vh;
}

section.main > div {
    padding-top: 0rem;
}

/* Header moderne */
.modern-header {
    background: rgba(30, 58, 52, 0.95);
    backdrop-filter: blur(10px);
    padding: 20px 40px;
    border-radius: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    border-bottom: 2px solid rgba(76, 175, 80, 0.3);
}

.modern-header .logo {
    display: flex;
    align-items: center;
    color: white;
    font-size: 28px;
    font-weight: 700;
    gap: 12px;
    justify-content: center;
    margin-bottom: 20px;
}

.modern-header .logo-icon {
    font-size: 40px;
    filter: drop-shadow(0 2px 8px rgba(76, 175, 80, 0.5));
}

/* Container principal */
.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 40px 60px;
}

/* Titre de page */
.page-title {
    color: white;
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 10px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 16px;
    margin-bottom: 40px;
    font-weight: 400;
}

/* Cartes modernes */
.modern-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Zone de capture/upload */
.capture-zone {
    background: linear-gradient(135deg, #f8faf9 0%, #e8f5e9 100%);
    border: 3px dashed #4CAF50;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    min-height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: all 0.3s ease;
}

.capture-zone:hover {
    border-color: #2E7D32;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(76, 175, 80, 0.2);
}

/* Zone de résultats */
.results-container {
    background: transparent;
    border-radius: 16px;
    padding: 0px;
    min-height: 400px;
}

.prediction-card {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
    border-left: 5px solid #4CAF50;
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
}

.prediction-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
confidence-display
.prediction-value {
    font-size: 32px;
    font-weight: 800;
    color: #2E7D32;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.confidence-display {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 20px 0;
}

.confidence-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}

.confidence-value {
    font-size: 24px;
    font-weight: 700;
    color: #4CAF50;
}

.info-box {
    background: rgba(76, 175, 80, 0.1);
    border-left: 4px solid #4CAF50;
    padding: 16px;
    border-radius: 8px;
    margin: 16px 0;
    color: #2E7D32;
    font-size: 14px;
    line-height: 1.6;
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
}

.empty-state-icon {
    font-size: 64px;
    margin-bottom: 20px;
    opacity: 0.3;
}

.empty-state-text {
    font-size: 16px;
    color: #666;
    margin-bottom: 30px;
}

/* Boutons personnalisés */
.stButton button {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
    padding: 14px 32px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
    width: 100%;
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.3);
    text-transform: none;
}

.stButton button:hover {
    background: linear-gradient(135deg, #388E3C 0%, #2E7D32 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.stButton button:active {
    transform: translateY(0px);
}

/* Barre de progression */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4CAF50 0%, #66BB6A 100%);
    border-radius: 10px;
}

.stProgress > div > div > div {
    background-color: rgba(76, 175, 80, 0.1);
    border-radius: 10px;
    height: 12px;
}

/* Images */
.stImage > img {
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* Tips card */
.tips-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 24px;
    border-radius: 16px;
    margin-top: 20px;
}

.tips-title {
    color: #4CAF50;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.tips-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
    color: #555;
}

.tips-card li {
    padding: 8px 0;
    padding-left: 24px;
    position: relative;
    font-size: 14px;
    line-height: 1.6;
}

.tips-card li:before {
    content: "✓";
    position: absolute;
    left: 0;
    color: #4CAF50;
    font-weight: bold;
}

/* Stats card pour About */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 30px 0;
}

.stat-card {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    padding: 24px;
    border-radius: 16px;
    text-align: center;
    border: 1px solid rgba(76, 175, 80, 0.2);
}

.stat-value {
    font-size: 40px;
    font-weight: 800;
    color: #2E7D32;
    margin-bottom: 8px;
}

.stat-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
    .modern-header {
        flex-direction: column;
        gap: 20px;
        padding: 20px;
    }

    .modern-header .nav-buttons {
        flex-direction: column;
        width: 100%;
    }

    .nav-btn {
        width: 100%;
    }

    .main-container {
        padding: 20px;
    }

    .page-title {
        font-size: 28px;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }
}

/* Animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}
</style>
"""

st.markdown(modern_css, unsafe_allow_html=True)

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
    """Affiche le header moderne avec navigation"""
    st.markdown(f"""
    <div class="modern-header">
        <div class="logo">
            <span class="logo-icon">♻️</span>
            <div>WasteWise</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------
# COMPOSANT: ZONE DE RÉSULTATS
# --------------------------------------------------------
def render_results_panel():
    """Affiche les résultats de prédiction"""
    if st.session_state.prediction_result:
        result = st.session_state.prediction_result
        category = result.get('category', 'Inconnu')
        confidence = float(result.get('confidence', 0))

        st.markdown(f"""
        <div class="prediction-card fade-in">
            <div class="prediction-label">Prédiction</div>
            <div class="prediction-value">
                ♻️ {category.upper()}
            </div>

            <div class="confidence-display">
                <span class="confidence-label">Niveau de confiance</span>
                <span class="confidence-value">{confidence*100:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(confidence)

        if 'description' in result:
            st.markdown(f"""
            <div class="info-box">
                <strong>ℹ️ Description:</strong> {result['description']}
            </div>
            """, unsafe_allow_html=True)

        if 'recycling_tips' in result:
            st.markdown(f"""
            <div class="info-box">
                <strong>♻️ Conseil de tri:</strong> {result['recycling_tips']}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Nouvelle analyse", use_container_width=True):
            st.session_state.prediction_result = None
            st.rerun()
    else:
        # Ne rien afficher si pas de résultat
        pass

# --------------------------------------------------------
# PAGE: DÉTECTION EN DIRECT
# --------------------------------------------------------
def page_detection():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 class='page-title fade-in'>Détection de Déchet en Direct</h1>
    <p class='page-subtitle'>Placez votre déchet devant votre caméra</p>
    """, unsafe_allow_html=True)

    if st.session_state.prediction_result:
        col1, col2 = st.columns([1.3, 1], gap="large")
    else:
        col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)

        camera_photo = st.camera_input("📷 Capturer une image", key="camera_detection", label_visibility="collapsed")

        if camera_photo:
            image_bytes = camera_photo.getvalue()
            st.image(image_bytes, use_container_width=True)

            if st.button("🔍 Analyser cette image", use_container_width=True):
                with st.spinner("🔄 Analyse en cours..."):
                    result = predict_waste(image_bytes)
                    if result:
                        st.session_state.prediction_result = result
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.prediction_result:
        with col2:
            st.markdown("<div class='results-container'>", unsafe_allow_html=True)
            render_results_panel()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE: UPLOAD IMAGE
# --------------------------------------------------------
def page_upload():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 class='page-title fade-in'>Analyser une Image</h1>
    <p class='page-subtitle'>Téléversez une image pour obtenir une analyse du déchet</p>
    """, unsafe_allow_html=True)

    if st.session_state.prediction_result:
        col1, col2 = st.columns([1.3, 1], gap="large")
    else:
        col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)

        uploaded_image = st.file_uploader(
            "📤 Importer une image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_image:
            image_bytes = uploaded_image.read()
            st.image(image_bytes, use_container_width=True)

            if st.button("🔍 Analyser cette image", use_container_width=True):
                with st.spinner("🔄 Analyse en cours..."):
                    result = predict_waste(image_bytes)
                    if result:
                        st.session_state.prediction_result = result
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.prediction_result:
        with col2:
            st.markdown("<div class='results-container'>", unsafe_allow_html=True)
            render_results_panel()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE: À PROPOS
# --------------------------------------------------------
def page_about():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 class='page-title fade-in'>À Propos de WasteWise</h1>
    <p class='page-subtitle'>Intelligence artificielle au service de l'environnement</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 style='color: #2E7D32; margin-bottom: 16px;'>🎯 Notre Mission</h3>
        <p style='color: #555; line-height: 1.8;'>
        WasteWise est une solution innovante qui utilise l'intelligence artificielle pour faciliter
        le tri des déchets et promouvoir le recyclage. Notre mission est de rendre le geste de tri
        accessible à tous grâce à la technologie de vision par ordinateur.
        </p>
        <p style='color: #555; line-height: 1.8; margin-top: 16px;'>
        En utilisant des algorithmes d'apprentissage profond, nous pouvons identifier et classifier
        automatiquement différents types de déchets en temps réel, aidant ainsi les utilisateurs à
        faire les bons choix de tri.
        </p>

        <h3 style='color: #2E7D32; margin-top: 30px; margin-bottom: 16px;'>🤖 La Technologie</h3>
        <p style='color: #555; line-height: 1.8;'>
        Notre modèle d'IA est entraîné sur des milliers d'images de déchets pour classifier avec précision
        les catégories suivantes:
        </p>
        <ul style='color: #555; line-height: 2; margin-left: 20px; margin-top: 12px;'>
            <li>♻️ <strong>Plastique</strong> - Bouteilles, emballages, contenants</li>
            <li>📄 <strong>Papier et carton</strong> - Journaux, boîtes, documents</li>
            <li>🥫 <strong>Métaux</strong> - Canettes, conserves, aluminium</li>
            <li>🍶 <strong>Verre</strong> - Bouteilles, pots, contenants</li>
            <li>🗑️ <strong>Déchets organiques</strong> - Restes alimentaires, déchets verts</li>
        </ul>
        <p style='color: #555; line-height: 1.8; margin-top: 16px;'>
        Le système analyse l'image en quelques secondes et fournit une prédiction avec un niveau de
        confiance, accompagnée de conseils de tri personnalisés.
        </p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 style='color: #2E7D32; margin-bottom: 24px;'>📈 Impact Environnemental</h3>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">10K+</div>
                <div class="stat-label">Images analysées</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">95%</div>
                <div class="stat-label">Précision moyenne</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">5</div>
                <div class="stat-label">Catégories détectées</div>
            </div>
        </div>

        <h3 style='color: #2E7D32; margin-top: 30px; margin-bottom: 16px;'>🌍 Pourquoi c'est Important</h3>
        <p style='color: #555; line-height: 1.8;'>
        Le tri correct des déchets est essentiel pour:
        </p>
        <ul style='color: #555; line-height: 2; margin-left: 20px; margin-top: 12px;'>
            <li>Réduire la pollution environnementale</li>
            <li>Économiser les ressources naturelles</li>
            <li>Diminuer les émissions de gaz à effet de serre</li>
            <li>Favoriser l'économie circulaire</li>
            <li>Protéger les écosystèmes et la biodiversité</li>
        </ul>

        <h3 style='color: #2E7D32; margin-top: 30px; margin-bottom: 16px;'>💚 Contribuez au Changement</h3>
        <p style='color: #555; line-height: 1.8;'>
        Chaque déchet correctement trié contribue à un avenir plus durable. En utilisant WasteWise,
        vous devenez un acteur du changement écologique. Ensemble, nous pouvons faire la différence
        pour notre planète.
        </p>
        <p style='color: #555; line-height: 1.8; margin-top: 16px;'>
        <strong>Commencez dès maintenant:</strong> Utilisez la fonction de détection en direct ou
        téléversez une image pour découvrir comment trier correctement vos déchets!
        </p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------
# NAVIGATION
# --------------------------------------------------------
def handle_navigation():
    """Gestion de la navigation entre les pages via boutons"""
    # Navigation par boutons dans le header
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

    with col1:
        if st.button("📸 Détection en Direct", use_container_width=True, key="btn_detection"):
            st.session_state.current_page = 'detection'
            st.session_state.prediction_result = None
            st.rerun()

    with col2:
        if st.button("🖼️ Analyser une Image", use_container_width=True, key="btn_upload"):
            st.session_state.current_page = 'upload'
            st.session_state.prediction_result = None
            st.rerun()

    with col3:
        if st.button("ℹ️ À Propos", use_container_width=True, key="btn_about"):
            st.session_state.current_page = 'about'
            st.rerun()

# --------------------------------------------------------
# MAIN APP
# --------------------------------------------------------
def main():
    render_header()
    handle_navigation()

    if st.session_state.current_page == 'detection':
        page_detection()
    elif st.session_state.current_page == 'upload':
        page_upload()
    elif st.session_state.current_page == 'about':
        page_about()

if __name__ == "__main__":
    main()
