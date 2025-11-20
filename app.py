import os
import streamlit as st
from PIL import Image
import io
import requests
import base64
import json



# Define the base URI of the API
#   - Potential sources are in `.streamlit/secrets.toml` or in the Secrets section
#     on Streamlit Cloud
#   - The source selected is based on the shell variable passend when launching streamlit
#     (shortcuts are included in Makefile). By default it takes the cloud API url
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['cloud_api_uri']
# Add a '/' at the end if it's not there
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
# Define the url to be used by requests.get to get a prediction (adapt if needed)
url = BASE_URI + 'predict'

# Just displaying the source for the API. Remove this in your final version.
#st.markdown(f"Working with {url}")

#st.markdown("Now, the rest is up to you. Start creating your page.")





# -----------------------------
# CONFIG
# -----------------------------

# -------------------------------------------
# CONFIGURATION DE LA PAGE
# -------------------------------------------



import os
import streamlit as st
from PIL import Image
import io
import requests
import base64
import json

# Define the base URI of the API (Keep your existing API logic)
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['cloud_api_uri']
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
url = BASE_URI + 'predict'


# --------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------
st.set_page_config(
    page_title="WasteWise – AI Waste Classification",
    page_icon="♻️",
    layout="wide"
)

# --------------------------------------------------------
# CUSTOM CSS – DARK MODE DESIGN
# --------------------------------------------------------
dark_mode_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* --- Couleurs du Thème Sombre --- */
:root {
    --bg-dark: #1E1E1E; /* Arrière-plan principal très foncé */
    --card-bg: #2C2C2C; /* Fond des cartes (un peu plus clair) */
    --accent-green: #4CAF50; /* Vert vif d'accentuation */
    --text-light: #FAFAFA; /* Texte principal */
    --text-muted: #B0B0B0; /* Texte secondaire */
}

body {
    font-family: 'Poppins', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-light);
}

/* Overrides pour forcer Streamlit en Dark Mode */
.stApp {
    background-color: var(--bg-dark);
}

/* --- Général et Conteneurs --- */
/* Masquer la sidebar par défaut si elle n'est pas utilisée */
/* La navigation API endpoint peut être déplacée vers le footer ou une modal */
.st-emotion-cache-cio0dv.ea3mdgi1, .st-emotion-cache-1na64h {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
.st-emotion-cache-h4xjwx {
    padding-top: 2rem;
}


/* --- Header & Titres --- */
.header-container {
    padding: 10px 0 20px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--card-bg); /* Séparation visuelle */
}

.logo-text {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-light);
    display: flex;
    align-items: center;
}

.logo-text span {
    color: var(--accent-green);
    margin-right: 10px;
    font-size: 32px;
}

h1 {
    font-size: 32px;
    font-weight: 600;
    color: var(--text-light);
    margin-top: 0;
}

h2 {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-light);
    margin-bottom: 15px;
}

p {
    color: var(--text-muted);
}


/* --- Cartes de Contenu (Cards) --- */
.content-card {
    background: var(--card-bg);
    padding: 30px;
    border-radius: 15px; /* Coins arrondis modérés */
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); /* Ombre douce et sombre */
    margin-bottom: 20px;
}


/* --- Navigation Secondaire (Boutons) --- */
.nav-buttons-bar {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
}

.stButton button {
    /* Style par défaut des boutons Streamlit (pour la nav et le corps) */
    background: var(--card-bg);
    color: var(--text-muted);
    border: 1px solid var(--text-muted);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton button:hover {
    color: var(--text-light);
    border-color: var(--accent-green);
}

.active-nav-button button {
    /* Bouton actif (vert) */
    background-color: var(--accent-green) !important;
    color: var(--text-light) !important;
    border-color: var(--accent-green) !important;
    font-weight: 600 !important;
}


/* --- Zone d'Input/Image --- */
.image-input-area {
    border: 2px dashed var(--text-muted); /* Bordure pointillée comme dans l'image */
    border-radius: 15px;
    padding: 40px;
    min-height: 350px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.image-preview img {
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}


/* --- Résultats --- */
.result-value {
    font-size: 36px;
    font-weight: 700;
    color: var(--accent-green);
    display: flex;
    align-items: center;
}

.result-confidence {
    font-size: 32px;
    font-weight: 700;
    color: var(--accent-green);
}

/* Barre de progression */
.stProgress > div > div > div > div {
    background-color: var(--accent-green); /* Vert d'accentuation */
    border-radius: 5px;
    height: 10px;
}
.stProgress > div > div > div {
    background-color: #404040; /* Gris foncé pour le fond de la barre */
    border-radius: 5px;
    height: 10px;
}

/* --- Bouton Flottant (Simulé) --- */
.floating-button-wrapper {
    text-align: center;
    margin-top: 20px;
}

.floating-button {
    background-color: var(--accent-green);
    color: white;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    cursor: pointer;
    transition: all 0.3s ease;
}
.floating-button:hover {
    background-color: #388E3C;
}

</style>
"""
st.markdown(dark_mode_css, unsafe_allow_html=True)

# --------------------------------------------------------
# HEADER ET NAVIGATION (Adaptés au Dark Mode)
# --------------------------------------------------------

# Utilisation d'un conteneur pour le header pour un meilleur contrôle
with st.container():
    st.markdown("<div class='header-container'>", unsafe_allow_html=True)

    # Logo et titre
    st.markdown("<div class='logo-text'><span>♻️</span> WasteWise</div>", unsafe_allow_html=True)

    # Titre principal (comme dans l'image)
    st.markdown("<h1>Détection de Déchets</h1>", unsafe_allow_html=True)
    st.markdown("<p>Placez votre déchet devant votre caméra.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation Secondaire
nav_col1, nav_col2, nav_col3 = st.columns([0.4, 0.4, 0.4])
with st.container():
    with nav_col1:
        # Le bouton actif est simulé ici avec la classe 'active-nav-button'
        st.markdown("<div class='active-nav-button'>", unsafe_allow_html=True)
        st.button("📸 Détection en Direct", use_container_width=True, key="nav_live")
        st.markdown("</div>", unsafe_allow_html=True)
    with nav_col2:
        st.button("🖼️ Analyser une Image", use_container_width=True, key="nav_upload")
    with nav_col3:
        st.button("💡 À Propos", use_container_width=True, key="nav_about")

st.markdown("---") # Séparation visuelle (style minimaliste)

# --------------------------------------------------------
# MAIN CONTENT (Colonnes de Contenu)
# --------------------------------------------------------
col_result, col_input = st.columns(2)

# --- COLONNE DE GAUCHE : RÉSULTATS ---
with col_result:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<h2>Résultats</h2>", unsafe_allow_html=True)

    # Simulation des données de résultat
    st.markdown("<p>Prédiction</p>", unsafe_allow_html=True)
    st.markdown("<div class='result-value'>🗑️ PLASTIQUE</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<p>Confiance</p>", unsafe_allow_html=True)
    st.markdown("<div class='result-confidence'>98.27%</div>", unsafe_allow_html=True)
    st.progress(0.9827)

    # L'appel à l'API serait ici
    # st.markdown(f"🗑 **Catégorie détectée :** {result.get('category', 'Non analysé')}")
    # st.progress(float(result.get("confidence", 0.0)))

    st.markdown("</div>", unsafe_allow_html=True)


# --- COLONNE DE DROITE : INPUT IMAGE ---
with col_input:
    # La zone d'input avec la bordure pointillée
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='image-input-area'>", unsafe_allow_html=True)

    img_bytes = None

    # Utilisation de st.file_uploader pour la zone d'upload/caméra
    uploaded = st.file_uploader("Importer une image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if uploaded:
        img_bytes = uploaded.read()
        st.image(img_bytes, use_container_width=True, caption="Image à analyser", output_format="JPEG")
    else:
        st.markdown("<p>Cliquez ici pour téléverser ou utilisez la caméra.</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Bouton Flottant (simulé en dessous pour rester dans la colonne)
    st.markdown("""
        <div class="floating-button-wrapper">
            <div class="floating-button">
                🚀
            </div>
            <p style="font-size: 14px; color: var(--text-muted);">Lancer l'Analyse</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------
# LOGIQUE DE PRÉDICTION (Réutilisation de votre logique)
# --------------------------------------------------------
if st.button("Lancer la Prédiction Réelle", key="predict_main_button", use_container_width=True):
    if img_bytes:
        with st.spinner("Processing…"):
            try:
                response = requests.post(
                    url, # Utilise votre URL définie en haut
                    files={"file": ("image.jpg", img_bytes)}
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("Prédiction reçue 🎉")
                    st.markdown(f"🗑 **Catégorie détectée :** {result.get('category', 'N/A')}")
                    if "description" in result:
                        st.info(result["description"])
                else:
                    st.error("Erreur API : " + response.text)

            except Exception as e:
                st.error(f"Erreur de communication : {e}")

    else:
        st.warning("Veuillez d'abord importer ou capturer une image.")
