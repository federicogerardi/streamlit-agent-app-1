import streamlit as st
import httpx
import urllib.parse
from utils.user_management import register_user, get_user
from utils.auth_persistence import load_auth_state, save_auth_state, clear_auth_state, is_auth_valid

def require_login():
    """
    Gestisce il flusso di OAuth2/OIDC con Google, e verifica il dominio autorizzato.
    Interrompe l'esecuzione dell'app se l'utente non è loggato usando st.stop().
    """
    # 1. Verifica se già autenticato in session_state
    if st.session_state.get("is_logged_in"):
        return
    
    # 2. Verifica se autenticazione è salvata in persistenza
    if is_auth_valid():
        auth_data = load_auth_state()
        st.session_state.is_logged_in = True
        st.session_state.user_email = auth_data.get("user_email")
        st.session_state.user_role = auth_data.get("user_role")
        return

    # Recupero credenziali dai secrets
    client_id = st.secrets["auth"]["client_id"]
    client_secret = st.secrets["auth"]["client_secret"]
    redirect_uri = st.secrets["auth"]["redirect_uri"]
    allowed_domain = st.secrets["auth"].get("allowed_domain", "")

    # 1. Gestione della Callback (Ritorno da Google con parametro 'code' nell'URL)
    if "code" in st.query_params:
        code = st.query_params.get("code")
        
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        with st.spinner("Autenticazione in corso, verifica delle credenziali..."):
            try:
                # Scambio del code con l'Access Token (comunicazione server-to-server)
                response = httpx.post(token_url, data=data)
                response.raise_for_status()
                tokens = response.json()
                
                access_token = tokens.get("access_token")
                
                # Lettura delle informazioni utente tramite il token
                userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = httpx.get(userinfo_url, headers=headers)
                userinfo_response.raise_for_status()
                
                userinfo = userinfo_response.json()
                user_email = userinfo.get("email", "")
                
                # Verifica Restrizione Dominio (Backend Security)
                if allowed_domain and not user_email.endswith(allowed_domain):
                    st.error(f"🛑 Accesso negato: L'email '{user_email}' non appartiene all'organizzazione di '{allowed_domain}'.")
                    if st.button("Torna alla Home / Usa un account diverso"):
                        st.query_params.clear()
                        st.rerun()
                    st.stop()
                    
                # Login autorizzato: registra/carica utente dal database
                user_data = register_user(user_email)  # Registra se nuovo, aggiorna se esiste
                
                # Salva le informazioni in sessione
                st.session_state.is_logged_in = True
                st.session_state.user_email = user_email
                st.session_state.user_role = user_data["role"]
                
                # Salva lo stato di autenticazione in persistenza
                save_auth_state(user_email, user_data["role"])
                
                # Pulizia della barra degli indirizzi dal parametro 'code' usabile una sola volta
                st.query_params.clear()
                st.success(f"Benvenuto, {user_email}! (Ruolo: {user_data['role'].upper()})")
                st.rerun()
                
            except httpx.HTTPStatusError as e:
                st.error(f"Errore di comunicazione con Google HTTP {e.response.status_code}: {e.response.text}")
                if st.button("Riprova"):
                    st.query_params.clear()
                    st.rerun()
                st.stop()
            except Exception as e:
                st.error(f"Errore imprevisto durante l'autenticazione: {e}")
                if st.button("Riprova"):
                    st.query_params.clear()
                    st.rerun()
                st.stop()

    # 2. Se non si è autenticati né in fase di callback, mostra il pulsante di Login
    st.warning("🔒 L'accesso è limitato ai membri dell'organizzazione autorizzata. Devi effettuare il login prima di poter usare l'AI Chat Hub.")
    
    # Creazione dell'URL di autorizzazione verso Account Google
    auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account"
    }
    
    auth_url = f"{auth_base_url}?{urllib.parse.urlencode(params)}"
    
    # st.link_button indirizza l'utente alla pagina di Google per approvare l'accesso
    st.link_button("🔑 Accedi con Google Workspace (Single Sign-On)", auth_url, type="primary")
    
    # Ferma l'esecuzione del resto dell'app finché non torna autorizzato
    st.stop()

def logout():
    """
    Effettua il logout forzatamente svuotando lo stato della sessione, l'URL e la persistenza
    """
    st.session_state.is_logged_in = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    # Cancella lo stato di autenticazione salvato
    clear_auth_state()
    st.query_params.clear()
    st.rerun()
