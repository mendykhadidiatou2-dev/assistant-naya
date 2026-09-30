import base64
import sys
from pathlib import Path

import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

RACINE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE))

from src.agent.agent import repondre_agent as repondre
from src.rag.vectorstore import charger_modele

NOM_ASSISTANT = "Naya"
CHEMIN_AVATAR = RACINE / "assets" / "naya.png"

st.set_page_config(
    page_title="Naya - Assistante IA",
    page_icon="\U0001F499",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CHARGEMENT DU MODELE (une seule fois)
# ============================================================

@st.cache_resource
def initialiser_modeles():
    return charger_modele()


initialiser_modeles()


# ============================================================
# AVATAR
# ============================================================

def avatar_base64() -> str:
    if CHEMIN_AVATAR.exists():
        data = CHEMIN_AVATAR.read_bytes()
        return "data:image/png;base64," + base64.b64encode(data).decode()
    return ""


AVATAR_DATA = avatar_base64()
AVATAR_CHAT = str(CHEMIN_AVATAR) if CHEMIN_AVATAR.exists() else "\U0001F499"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(255,210,232,0.45), transparent 30%),
            radial-gradient(circle at 90% 15%, rgba(216,203,255,0.40), transparent 30%),
            radial-gradient(circle at 50% 100%, rgba(255,226,210,0.35), transparent 35%),
            linear-gradient(135deg, #fffafd 0%, #f9f5ff 48%, #fff8f4 100%);
        min-height: 100vh;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container { padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1250px; }

    /* HERO */
    .hero-wrapper { text-align: center; padding: 10px 0 35px 0; position: relative; }
    .hero-glow {
        position: absolute; width: 330px; height: 330px; border-radius: 50%;
        background: radial-gradient(circle, rgba(245,193,221,0.30) 0%, rgba(218,199,255,0.16) 45%, transparent 72%);
        filter: blur(10px); left: 50%; top: -40px; transform: translateX(-50%); pointer-events: none;
    }

    /* AVATAR */
    .avatar-container { position: relative; width: 190px; height: 190px; margin: 0 auto 24px auto; display: flex; justify-content: center; align-items: center; }
    .avatar-ring {
        position: absolute; inset: 0; border-radius: 50%;
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,221,237,0.85), rgba(218,204,255,0.90));
        padding: 5px;
        box-shadow: 0 18px 55px rgba(213,157,192,0.25), 0 0 50px rgba(213,187,255,0.30);
        animation: floatAvatar 4.5s ease-in-out infinite, glowAvatar 3.5s ease-in-out infinite;
    }
    .avatar-ring::before {
        content: ""; position: absolute; inset: -8px; border-radius: 50%;
        border: 1px solid rgba(255,255,255,0.75);
        box-shadow: 0 0 25px rgba(239,181,218,0.35), 0 0 50px rgba(204,185,255,0.20);
        animation: pulseRing 3s ease-in-out infinite;
    }
    .avatar-image {
        width: 100%; height: 100%; border-radius: 50%;
        background-size: cover; background-position: center;
        border: 5px solid rgba(255,255,255,0.95); position: relative; z-index: 2;
    }
    @keyframes floatAvatar { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-11px); } }
    @keyframes glowAvatar {
        0%,100% { box-shadow: 0 18px 55px rgba(213,157,192,0.25), 0 0 40px rgba(213,187,255,0.25); }
        50% { box-shadow: 0 25px 65px rgba(213,157,192,0.35), 0 0 65px rgba(213,187,255,0.40); }
    }
    @keyframes pulseRing { 0%,100% { transform: scale(1); opacity: 0.65; } 50% { transform: scale(1.06); opacity: 0.25; } }

    /* TITRE */
    .hero-title {
        font-size: 36px; font-weight: 600;
        background: linear-gradient(90deg, #a65d87, #8065ad, #a65d87);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 5px 0 5px 0; letter-spacing: -0.7px;
    }
    .hero-role { font-size: 15px; font-weight: 500; color: #8d7194; margin-bottom: 13px; }
    .hero-description { max-width: 670px; margin: 0 auto; color: #766b7b; font-size: 14px; line-height: 1.75; font-weight: 400; }

    /* ONLINE PILL */
    .online-pill {
        display: inline-flex; align-items: center; gap: 7px; margin-top: 17px;
        padding: 7px 14px; border-radius: 50px;
        background: rgba(255,255,255,0.60); border: 1px solid rgba(255,255,255,0.90);
        box-shadow: 0 8px 25px rgba(179,140,174,0.10); backdrop-filter: blur(12px);
        color: #7d6d82; font-size: 11px; font-weight: 500;
    }
    .online-dot { width: 7px; height: 7px; border-radius: 50%; background: #77c99c; box-shadow: 0 0 0 4px rgba(119,201,156,0.13); animation: onlinePulse 2s infinite; }
    @keyframes onlinePulse { 0%,100% { box-shadow: 0 0 0 3px rgba(119,201,156,0.10); } 50% { box-shadow: 0 0 0 7px rgba(119,201,156,0.02); } }

    /* BENTO */
    .bento-title { text-align: center; font-size: 19px; font-weight: 600; color: #735d78; margin: 5px 0 18px 0; }
    .bento-card {
        position: relative; min-height: 185px; padding: 25px; border-radius: 25px;
        background: linear-gradient(145deg, rgba(255,255,255,0.75), rgba(255,248,252,0.48));
        border: 1px solid rgba(255,255,255,0.88);
        box-shadow: 0 14px 40px rgba(190,157,184,0.10);
        backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
        overflow: hidden; transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease;
    }
    .bento-card::before {
        content: ""; position: absolute; width: 120px; height: 120px; border-radius: 50%;
        background: radial-gradient(circle, rgba(242,190,218,0.16), transparent 70%); top: -55px; right: -35px;
    }
    .bento-card:hover {
        transform: translateY(-7px);
        box-shadow: 0 22px 55px rgba(185,137,178,0.18), 0 0 25px rgba(215,188,244,0.12);
        border-color: rgba(255,255,255,1);
    }
    .bento-icon {
        width: 48px; height: 48px; border-radius: 16px;
        display: flex; align-items: center; justify-content: center; font-size: 22px;
        background: linear-gradient(135deg, rgba(255,221,237,0.75), rgba(225,214,255,0.75));
        box-shadow: 0 8px 20px rgba(192,156,190,0.12); margin-bottom: 16px;
    }
    .bento-card h3 { margin: 0 0 8px 0; font-size: 17px; font-weight: 600; color: #765e7b; }
    .bento-card p { margin: 0; font-size: 12.5px; line-height: 1.7; color: #817682; }

    /* BADGES */
    .status-active, .status-soon {
        display: inline-flex; padding: 4px 9px; border-radius: 30px;
        font-size: 9px; font-weight: 600; vertical-align: middle; margin-left: 5px;
    }
    .status-active { color: #538d70; background: rgba(216,243,227,0.72); }
    .status-soon { color: #9274a7; background: rgba(231,220,249,0.72); }

    .soft-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(199,171,198,0.30), transparent); margin: 35px 0 30px 0; }

    .chat-heading { display: flex; align-items: center; gap: 10px; font-size: 21px; font-weight: 600; color: #765e7b; margin-bottom: 3px; }
    .chat-subtitle { font-size: 12px; color: #958895; margin-bottom: 18px; }

    [data-testid="stChatMessage"] {
        border-radius: 22px !important; border: 1px solid rgba(255,255,255,0.80) !important;
        background: rgba(255,255,255,0.52) !important;
        box-shadow: 0 8px 25px rgba(187,156,181,0.07) !important;
        backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
        padding: 14px 17px !important; margin-bottom: 12px;
    }
    [data-testid="stChatMessageContent"] { color: #6e6471; font-size: 13px; line-height: 1.7; }

    [data-testid="stChatInput"] { border-radius: 25px !important; }
    [data-testid="stChatInput"] > div {
        border-radius: 25px !important; background: rgba(255,255,255,0.72) !important;
        border: 1px solid rgba(255,255,255,0.95) !important;
        box-shadow: 0 10px 35px rgba(182,145,178,0.12) !important; backdrop-filter: blur(15px);
    }
    [data-testid="stChatInput"] textarea { font-family: 'Poppins', sans-serif !important; color: #665d68 !important; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,247,252,0.97), rgba(247,242,255,0.97));
        border-right: 1px solid rgba(255,255,255,0.85);
    }
    section[data-testid="stSidebar"] > div { padding-top: 2rem; }
    .sidebar-brand { text-align: center; margin-bottom: 20px; }
    .sidebar-avatar {
        width: 92px; height: 92px; margin: 0 auto 12px auto; border-radius: 50%;
        background-size: cover; background-position: center;
        border: 4px solid rgba(255,255,255,0.95); box-shadow: 0 10px 30px rgba(191,148,184,0.20);
    }
    .sidebar-name { color: #765e7b; font-size: 20px; font-weight: 600; }
    .sidebar-role { color: #958895; font-size: 11px; margin-top: 2px; }
    .sidebar-status { display: flex; align-items: center; justify-content: center; gap: 7px; margin-top: 13px; color: #63836e; font-size: 10px; font-weight: 500; }
    .sidebar-section {
        margin-top: 27px; padding: 17px; border-radius: 20px;
        background: rgba(255,255,255,0.48); border: 1px solid rgba(255,255,255,0.75);
        box-shadow: 0 8px 25px rgba(182,148,180,0.06); backdrop-filter: blur(12px);
    }
    .sidebar-section-title { color: #79627d; font-size: 12px; font-weight: 600; margin-bottom: 12px; }
    .sidebar-item { color: #817681; font-size: 11px; line-height: 1.7; padding: 5px 0; }
    .sidebar-footer { text-align: center; color: #aa9eaa; font-size: 9px; margin-top: 30px; }

    @media (max-width: 768px) {
        .block-container { padding-top: 1.5rem; }
        .hero-title { font-size: 28px; }
        .avatar-container { width: 155px; height: 155px; }
        .hero-description { padding: 0 15px; }
        .bento-card { margin-bottom: 15px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

if AVATAR_DATA:
    st.markdown(
        f"""
        <div class="hero-wrapper">
            <div class="hero-glow"></div>
            <div class="avatar-container">
                <div class="avatar-ring" style="background-image: url('{AVATAR_DATA}'); background-size: cover; background-position: center;">
                    <div class="avatar-image" style="background-image: url('{AVATAR_DATA}');"></div>
                </div>
            </div>
            <div class="hero-title">Bonjour, je suis {NOM_ASSISTANT} \U0001F499</div>
            <div class="hero-role">Ton assistante IA personnelle</div>
            <div class="hero-description">
                Je peux rechercher dans tes documents administratifs, consulter ton agenda
                et reperer tes e-mails importants, en citant toujours mes sources.
            </div>
            <div class="online-pill">
                <span class="online-dot"></span>
                Naya est en ligne
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="hero-title">Bonjour, je suis Naya \U0001F499</div>
            <div class="hero-role">Ton assistante IA personnelle</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BENTO GRID
# ============================================================

st.markdown('<div class="bento-title">\u2728 Ce que Naya peut faire pour toi</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(
        """
        <div class="bento-card">
            <div class="bento-icon">\U0001F4C1</div>
            <h3>Documents <span class="status-active">ACTIF</span></h3>
            <p>Je retrouve les informations importantes dans tes documents administratifs
            et je cite la source utilisee pour repondre.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="bento-card">
            <div class="bento-icon">\U0001F4E7</div>
            <h3>E-mails <span class="status-active">ACTIF</span></h3>
            <p>Je repere tes messages non lus et les mails importants, avec l'expediteur,
            l'objet et un apercu du contenu.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="bento-card">
            <div class="bento-icon">\U0001F5D3</div>
            <h3>Planning <span class="status-active">ACTIF</span></h3>
            <p>Je consulte ton agenda et tes cours a venir. Bientot : un resume
            automatique de ta journee chaque matin a 8 h.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SEPARATEUR
# ============================================================

st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    if CHEMIN_AVATAR.exists():
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-avatar" style="background-image: url('{AVATAR_DATA}');"></div>
                <div class="sidebar-name">Naya \U0001F499</div>
                <div class="sidebar-role">Assistante IA personnelle</div>
                <div class="sidebar-status"><span class="online-dot"></span> En ligne</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-name">Naya \U0001F499</div>
                <div class="sidebar-role">Assistante IA personnelle</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-section-title">\u2728 Ce que je sais faire</div>
            <div class="sidebar-item">\U0001F4C1 Recherche dans tes documents</div>
            <div class="sidebar-item">\U0001F5D3 Consultation de ton agenda</div>
            <div class="sidebar-item">\U0001F4E7 Reperage de tes e-mails</div>
            <div class="sidebar-item">\U0001F916 Reponses basees sur tes sources</div>
            <div class="sidebar-item">\U0001F510 Recherche traitee localement</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-section-title">\U0001F337 Bientot</div>
            <div class="sidebar-item">\u23F0 Resume automatique a 8 h</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-footer">Concu avec amour par Khadija \U0001F495</div>', unsafe_allow_html=True)


# ============================================================
# CHAT
# ============================================================

st.markdown(
    """
    <div class="chat-heading">\U0001F4AC Discute avec Naya</div>
    <div class="chat-subtitle">Pose-moi une question sur tes documents, ton agenda ou tes e-mails.</div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Bonjour Khadija \U0001F337\n\n"
                "Pose-moi une question sur tes documents, ton agenda ou tes e-mails, "
                "et je cherche l'information pour toi."
            ),
        }
    ]

for message in st.session_state.messages:
    avatar = AVATAR_CHAT if message["role"] == "assistant" else "\U0001F9D5\U0001F3FE"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input("Pose une question a Naya... \U0001F4AD")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="\U0001F9D5\U0001F3FE"):
        st.markdown(question)

    with st.chat_message("assistant", avatar=AVATAR_CHAT):
        with st.spinner("Naya reflechit... \u2728"):
            reponse = repondre(question)
        st.markdown(reponse)

    st.session_state.messages.append({"role": "assistant", "content": reponse})
