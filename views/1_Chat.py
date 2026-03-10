import streamlit as st
from utils.auth import require_login
from utils.api import get_openrouter_client
from utils.permissions import can_use_model, get_daily_limit
from utils.user_management import get_message_count_today, increment_message_count
from utils.session_persistence import save_session_messages

# Protezione pagina
require_login()

st.title("💬 Chat API Hub")

# Verifiche permessi e limit
user_email = st.session_state.get('user_email')
user_role = st.session_state.get('user_role', 'user')
current_model = st.session_state.get('active_model', 'openai/gpt-3.5-turbo')

# Controlla il limite di messaggi giornalieri
daily_limit = get_daily_limit(user_role)
if daily_limit:
    today_count = get_message_count_today(user_email)
    
    if today_count >= daily_limit:
        st.error(f"❌ Limite raggiunto: hai raggiunto il massimo di {daily_limit} messaggi per oggi.")
        st.info("Torna domani per continuare.")
        st.stop()
    elif today_count > daily_limit * 0.8:  # 80% del limite
        remaining = daily_limit - today_count
        st.warning(f"⚠️ Stai per raggiungere il limite quotidiano: {remaining} messaggi rimasti.")

# Controlla che il modello sia autorizzato per il ruolo
if not can_use_model(user_role, current_model):
    st.error(f"❌ Il ruolo '{user_role}' non ha accesso al modello '{current_model}'.")
    st.info("Vai alla pagina Configurazione per scegliere un modello autorizzato.")
    st.stop()

# Mostra il modello attivo
st.caption(f"🤖 Modello Attivo: {current_model} | 🌡️ Temp: {st.session_state.get('temperature', 0.7)}")

# Visualizza i messaggi precedenti
for message in st.session_state.get("messages", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Il fragment garantisce che solo la parte di generazione del testo 
# venga ri-eseguita, mantendo fluido il resto dell'app
@st.fragment
def stream_llm_response(prompt: str):
    """Gestisce la chiamata all'API di OpenRouter con streaming e salva la risposta."""
    try:
        client = get_openrouter_client()
        
        # Prepara la lista messaggi con l'input corrente
        messages_to_send = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        messages_to_send.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            # Generazione stream
            stream = client.chat.completions.create(
                model=st.session_state.active_model,
                messages=messages_to_send,
                temperature=st.session_state.temperature,
                stream=True,
            )
            
            # Scrittura in streaming sulla UI
            full_response = st.write_stream(stream)
            
            # Aggiorna lo stato della sessione solo dopo aver completato lo streaming
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Salva i messaggi in persistenza
            save_session_messages(user_email, st.session_state.messages)
            
    except Exception as e:
        status_code = getattr(e, "status_code", None)
        if status_code == 401:
            st.error("Errore di Autenticazione API. Verifica le chiavi nel file secrets.toml.")
        else:
            st.error(f"Errore durante la connessione a OpenRouter: {e}")

# Input chat (disabilitato per sicurezza se per caso l'auth fallisse implicitamente)
if prompt := st.chat_input("Scrivi qui il tuo messaggio...", disabled=not st.session_state.get('is_logged_in', False)):
    
    # 1. Salva l'input e mostralo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Incrementa il contatore di messaggi (conta sia user che assistant)
    new_count = increment_message_count(user_email)

    # 3. Genera la risposta dell'LLM (dentro il frammento)
    stream_llm_response(prompt)
