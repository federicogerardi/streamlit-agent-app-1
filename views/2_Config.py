import streamlit as st
from utils.auth import require_login
from utils.api import fetch_available_models
from utils.permissions import get_role_permissions, check_permission, ROLES
from utils.user_management import get_all_users, change_user_role
from utils.session_persistence import save_session_config, clear_session

# Protezione pagina
require_login()

# Verifica permessi di accesso alla configurazione
user_role = st.session_state.get('user_role', 'user')
if not check_permission(user_role, 'access_config'):
    st.error(f"❌ Accesso negato: il ruolo '{user_role}' non ha permesso di accedere alla configurazione.")
    st.info("Contatta un amministratore per richiedere l'accesso.")
    st.stop()

st.title("⚙️ Configurazione")

# Recupera la lista dei modelli
with st.spinner("Caricamento modelli da OpenRouter..."):
    all_available_models = fetch_available_models()

# Filtra i modelli in base al ruolo dell'utente
from utils.permissions import can_use_model
available_models = [m for m in all_available_models if can_use_model(user_role, m)]

if not available_models:
    st.warning(f"Nessun modello disponibile per il ruolo '{user_role}'.")
    available_models = all_available_models  # Fallback ai modelli di default

# Callback per sincronizzare lo stato con i query parameters e salvare in persistenza
def update_query_params():
    st.query_params.update(
        {"model": st.session_state.active_model, "temp": str(st.session_state.temperature)}
    )
    # Salva la configurazione in persistenza
    user_email = st.session_state.get('user_email')
    save_session_config(user_email, st.session_state.active_model, st.session_state.temperature)

# --- Impostazioni Generali ---
st.header("Modello")

# 1. Scelta Modello
# Inizializza active_model se non esiste
if "active_model" not in st.session_state:
    st.session_state.active_model = "openai/gpt-3.5-turbo"

# Se st.session_state.active_model non e' nella lista (improbabile ma possibile), default base
try:
    default_index = available_models.index(st.session_state.active_model)
except ValueError:
    default_index = 0

st.selectbox(
    "Seleziona il Modello LLM",
    options=available_models,
    index=default_index,
    key="active_model",
    on_change=update_query_params
)

# 2. Temperatura
# Inizializza temperature se non esiste
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

st.header("Parametri")
st.slider(
    "Temperatura",
    min_value=0.0,
    max_value=2.0,
    step=0.1,
    key="temperature",
    on_change=update_query_params,
    help="Valori più alti rendono l'output più casuale, mentre valori più bassi lo rendono più deterministico."
)

st.divider()

# 3. Gestione Dati
st.header("Gestione Dati")

col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Cancella Cronologia Chat", type="primary"):
        user_email = st.session_state.get('user_email')
        st.session_state.messages = []
        # Salva la cronologia vuota in persistenza
        from utils.session_persistence import save_session_messages
        save_session_messages(user_email, [])
        st.success("La cronologia della chat è stata eliminata.")

with col2:
    if st.button("🔄 Ripristina Sessione Predefinita", type="secondary"):
        user_email = st.session_state.get('user_email')
        clear_session(user_email)
        st.session_state.messages = []
        st.session_state.active_model = "openai/gpt-3.5-turbo"
        st.session_state.temperature = 0.7
        st.success("Sessione ripristinata ai valori predefiniti.")
        st.rerun()

# Mostra i parametri attuali dell'URL
st.caption("URL per condividere questa configurazione:")
st.code(
    f"http://localhost:8501/?model={st.session_state.active_model}&temp={st.session_state.temperature}"
)

# --- SEZIONE ADMIN ---
if user_role == "admin":
    st.divider()
    st.header("🔐 Gestione Amministrativa")
    
    tab1, tab2 = st.tabs(["Utenti", "Informazioni Sistema"])
    
    with tab1:
        st.subheader("Lista Utenti")
        
        try:
            users = get_all_users()
            
            if not users:
                st.info("Nessun utente registrato.")
            else:
                # Mostra tabella degli utenti
                user_data = []
                for email, info in users.items():
                    user_data.append({
                        "Email": email,
                        "Ruolo": info.get("role", "user").upper(),
                        "Creato": info.get("created_at", "N/A")[:10],
                        "Ultimo Login": info.get("last_login", "N/A")[:10] if info.get("last_login") else "Mai"
                    })
                
                st.dataframe(user_data, width='stretch')
                
                # Cambio ruolo utente
                st.subheader("Cambia Ruolo Utente")
                selected_user = st.selectbox(
                    "Seleziona un utente:",
                    options=list(users.keys())
                )
                
                current_role = users[selected_user]["role"]
                new_role = st.selectbox(
                    f"Nuovo ruolo per {selected_user}:",
                    options=list(ROLES.keys()),
                    index=list(ROLES.keys()).index(current_role)
                )
                
                if st.button("Aggiorna Ruolo", type="primary"):
                    change_user_role(selected_user, new_role)
                    st.success(f"✅ Ruolo di {selected_user} aggiornato a {new_role.upper()}")
                    st.rerun()
        
        except Exception as e:
            st.error(f"Errore nel caricamento degli utenti: {e}")
    
    with tab2:
        st.subheader("Ruoli Disponibili")
        
        for role_key, role_info in ROLES.items():
            with st.expander(f"👤 {role_info['name']} (Livello {role_info['level']})"):
                st.write(role_info['description'])
                
                perms = get_role_permissions(role_key)
                st.write("**Permessi:**")
                for perm_key, perm_value in perms.items():
                    if isinstance(perm_value, bool):
                        status = "✅ Abilitato" if perm_value else "❌ Disabilitato"
                        st.caption(f"{perm_key}: {status}")
                    elif isinstance(perm_value, list):
                        st.caption(f"{perm_key}: {len(perm_value)} modelli")
                    elif perm_value is None:
                        st.caption(f"{perm_key}: Illimitato")
                    else:
                        st.caption(f"{perm_key}: {perm_value}")
