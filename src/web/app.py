import base64
import sys
from pathlib import Path

import streamlit as st

# ---------------- CONFIG ----------------
RACINE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE))

from src.rag.repondre import repondre
from src.rag.vectorstore import charger_modele

@st.cache_resource
def initialiser_modeles():
    """Charge le modèle d'embedding une seule fois, gardé en mémoire par Streamlit."""
    return charger_modele()

# On force le chargement au démarrage (une seule fois grâce au cache)
initialiser_modeles()

NOM_ASSISTANT = "Naya"
CHEMIN_AVATAR = RACINE / "assets" / "naya.png"

st.set_page_config(
    page_title="Naya - Assistante IA",
    page_icon="\U0001F499",
    layout="wide",
)


# ---------------- AVATAR EN BASE64 ----------------
def avatar_base64() -> str:
    if CHEMIN_AVATAR.exists():
        data = CHEMIN_AVATAR.read_bytes()
        return "data:image/png;base64," + base64.b64encode(data).decode()
    return ""


AVATAR_DATA = avatar_base64()
AVATAR_CHAT = str(CHEMIN_AVATAR) if CHEMIN_AVATAR.exists() else "\U0001F499"

# ---------------- STYLE ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{ font-family:'Poppins', sans-serif; }

.stApp{ background: linear-gradient(135deg,#F7FAFF,#EEF4FF); }

#MainMenu, footer, header{ visibility:hidden; }

.hero-centre{ text-align:center; padding:20px 0 10px 0; }

.avatar-cercle{
    width:170px; height:170px; border-radius:50%; margin:0 auto;
    background-size:cover; background-position:center;
    border:6px solid white;
    box-shadow:0 10px 40px rgba(91,145,255,.45);
    animation: levitation 4s ease-in-out infinite, glow 3s ease-in-out infinite;
}
@keyframes levitation{ 0%,100%{ transform:translateY(0); } 50%{ transform:translateY(-12px); } }
@keyframes glow{
    0%,100%{ box-shadow:0 10px 30px rgba(91,145,255,.35); }
    50%    { box-shadow:0 15px 50px rgba(125,168,255,.65); }
}

.hero-nom{ font-size:34px; font-weight:600; color:#244C9A; margin-top:18px; }
.hero-role{ font-size:15px; color:#5B7BB4; margin-top:2px; }
.hero-desc{ max-width:620px; margin:14px auto 0 auto; color:#5B6B8C; font-size:15px; line-height:1.6; }

.info{
    background:white; border-radius:18px; padding:22px;
    box-shadow:0 8px 30px rgba(0,0,0,.05); border:1px solid #EDF2FF; height:100%;
    transition: transform .25s ease, box-shadow .25s ease;
}
.info:hover{ transform: translateY(-6px) scale(1.02); box-shadow:0 18px 45px rgba(91,145,255,.22); }
.info h3{ color:#244C9A; margin-top:0; }

.badge-actif{ font-size:11px; color:#1E8E5A; background:#E4F7EE; padding:2px 10px; border-radius:12px; }
.badge-bientot{ font-size:11px; color:#7DA8FF; background:#EEF4FF; padding:2px 10px; border-radius:12px; }

h2,h3{ color:#244C9A; }
</style>
""", unsafe_allow_html=True)

# ---------------- HERO CENTRE ----------------
st.markdown(f"""
<div class="hero-centre">
    <div class="avatar-cercle" style="background-image:url('{AVATAR_DATA}');"></div>
    <div class="hero-nom">Bonjour, je suis {NOM_ASSISTANT} \U0001F499</div>
    <div class="hero-role">Ton assistante IA personnelle</div>
    <div class="hero-desc">
        Aujourd'hui, je sais retrouver n'importe quelle information dans tes documents
        administratifs, en citant toujours ma source. Bientot, je gererai aussi tes
        e-mails et ton planning quotidien.
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- CARTES ----------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="info">
        <h3>\U0001F4C1 Documents <span class="badge-actif">actif</span></h3>
        <p>Je retrouve tes papiers administratifs et je reponds a tes questions,
        en citant toujours ma source.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="info">
        <h3>\U0001F4E7 E-mails <span class="badge-bientot">bientot</span></h3>
        <p>Bientot : lire mes messages non lus et reperer les mails importants
        auxquels je n'ai pas repondu.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="info">
        <h3>\U0001F5D3 Planning <span class="badge-bientot">bientot</span></h3>
        <p>Bientot : mon emploi du temps consultable, et un resume de ma journee
        envoye chaque matin.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    if CHEMIN_AVATAR.exists():
        st.image(str(CHEMIN_AVATAR), width=140)
    st.markdown("## Naya")
    st.caption("Assistante IA personnelle")
    st.success("\U0001F7E2 En ligne")

    st.markdown("---")
    st.markdown("### Ce que je sais faire")
    st.markdown("""
- \U0001F4C1 Chercher dans tes documents
- \U0001F916 Repondre en citant ma source
- \U0001F512 Tout en local, tes donnees restent chez toi
""")

    st.markdown("### Bientot")
    st.markdown("""
- \U0001F4E7 Lire tes e-mails
- \U0001F5D3 Ton planning du jour
""")

    st.markdown("---")
    st.caption("Concu avec amour par Khadija")

# ---------------- CHAT ----------------
st.subheader("\U0001F4AC Discute avec Naya")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour Khadija \U0001F338 Pose-moi une question sur tes documents "
                       "administratifs, et je retrouve l'information pour toi.",
        }
    ]

for message in st.session_state.messages:
    avatar = AVATAR_CHAT if message["role"] == "assistant" else "\U0001F9D1\U0001F3FE"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input("Pose une question a Naya...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="\U0001F9D1\U0001F3FE"):
        st.markdown(question)

    with st.chat_message("assistant", avatar=AVATAR_CHAT):
        with st.spinner("Naya cherche dans tes documents..."):
            reponse = repondre(question)
        st.markdown(reponse)

    st.session_state.messages.append({"role": "assistant", "content": reponse})