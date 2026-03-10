import streamlit as st
from utils.auth import require_login, logout
from utils.api import get_openrouter_client
from utils.permissions import get_role_permissions, get_daily_limit
from utils.user_management import get_message_count_today
from utils.session_persistence import load_session, save_session

# Configurazione base della pagina
st.set_page_config(
    page_title="AI Chat Hub",
    page_icon="🤖",
    layout="wide"
)

# Gestione Autenticazione (Blocca se non autenticato)
require_login()

# Se siamo qui, l'utente è autenticato.
user_email = st.session_state.get('user_email', 'User')
user_role = st.session_state.get('user_role', 'user')

# Caricamento della sessione persistente
if "session_loaded" not in st.session_state:
    session_data = load_session(user_email)
    st.session_state["messages"] = session_data.get("messages", [])
    st.session_state["active_model"] = session_data.get("active_model", "openai/gpt-3.5-turbo")
    st.session_state["temperature"] = session_data.get("temperature", 0.7)
    st.session_state["session_loaded"] = True

# Sincronizzazione INIZIALE URL -> Session State (sovrascrivi solo se parametri presenti)
qp = st.query_params
if "model" in qp:
    st.session_state["active_model"] = qp.get("model", "openai/gpt-3.5-turbo")
if "temp" in qp:
    try:
        st.session_state["temperature"] = float(qp.get("temp", 0.7))
    except ValueError:
        st.session_state["temperature"] = 0.7

# Sincronizzazione CONTINUA Session State -> URL
st.query_params.update({
    "model": st.session_state.get("active_model", "openai/gpt-3.5-turbo"),
    "temp": str(st.session_state.get("temperature", 0.7))
})

# Mostra info utente nella sidebar
st.sidebar.divider()
st.sidebar.write("#### 👤 Profilo")
st.sidebar.caption(f"**Email:** {user_email}")
st.sidebar.caption(f"**Ruolo:** {user_role.upper()}")

# Mostra limite messaggi giornalieri se presente
daily_limit = get_daily_limit(user_role)
if daily_limit:
    today_count = get_message_count_today(user_email)
    remaining = max(0, daily_limit - today_count)
    st.sidebar.caption(f"📊 Messaggi: {today_count}/{daily_limit} ({remaining} rimanenti)")

if st.sidebar.button("🚪 Logout"):
    logout()
st.sidebar.divider()

# Pulsante per salvare manualmente la sessione (opzionale)
if st.sidebar.button("💾 Salva Sessione"):
    session_data = {
        "messages": st.session_state.get("messages", []),
        "active_model": st.session_state.get("active_model", "openai/gpt-3.5-turbo"),
        "temperature": st.session_state.get("temperature", 0.7)
    }
    if save_session(user_email, session_data):
        st.sidebar.success("✅ Sessione salvata!")
    else:
        st.sidebar.error("❌ Errore nel salvataggio della sessione")

# Inizializziamo il client API in modo che sia disponibile ovunque
if "api_client" not in st.session_state:
    st.session_state["api_client"] = get_openrouter_client()

# Gestione del routing multipagina
pages = {
    "Moduli": [
        st.Page("views/1_Chat.py", title="Chat", default=True),
        st.Page("views/2_Config.py", title="Configurazione")
    ]
}

pg = st.navigation(pages)
pg.run()
