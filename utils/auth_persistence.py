"""
Persistenza dello stato di autenticazione.
Salva e carica le informazioni di login per mantenere la sessione tra i refresh.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

# Percorso del file autenticazione relativo a .streamlit/
AUTH_FILE = Path(__file__).parent.parent / ".streamlit" / "auth_state.json"

def ensure_auth_file_exists():
    """Crea il file auth_state.json se non esiste."""
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_auth_state() -> dict:
    """
    Carica lo stato di autenticazione salvato.
    Ritorna dict con is_logged_in, user_email, user_role, timestamp.
    Se non esiste o è scaduto, ritorna stato vuoto.
    """
    ensure_auth_file_exists()
    
    if not AUTH_FILE.exists():
        return {
            "is_logged_in": False,
            "user_email": None,
            "user_role": None,
            "timestamp": None
        }
    
    try:
        with open(AUTH_FILE, "r") as f:
            auth_data = json.load(f)
        
        # Verifica se lo stato è scaduto (24 ore)
        if auth_data.get("timestamp"):
            timestamp = datetime.fromisoformat(auth_data["timestamp"])
            if datetime.now() - timestamp > timedelta(hours=24):
                # Stato scaduto, cancella
                clear_auth_state()
                return {
                    "is_logged_in": False,
                    "user_email": None,
                    "user_role": None,
                    "timestamp": None
                }
        
        return auth_data
    except (json.JSONDecodeError, IOError, ValueError):
        return {
            "is_logged_in": False,
            "user_email": None,
            "user_role": None,
            "timestamp": None
        }

def save_auth_state(user_email: str, user_role: str) -> bool:
    """
    Salva lo stato di autenticazione.
    
    Args:
        user_email: Email dell'utente autenticato
        user_role: Ruolo dell'utente
    
    Returns:
        True se salvato con successo, False altrimenti
    """
    try:
        ensure_auth_file_exists()
        
        auth_data = {
            "is_logged_in": True,
            "user_email": user_email,
            "user_role": user_role,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(AUTH_FILE, "w") as f:
            json.dump(auth_data, f, indent=2)
        
        return True
    except IOError as e:
        print(f"Errore nel salvataggio dello stato di autenticazione: {e}")
        return False

def clear_auth_state() -> bool:
    """Cancella lo stato di autenticazione."""
    try:
        if AUTH_FILE.exists():
            AUTH_FILE.unlink()
        return True
    except IOError as e:
        print(f"Errore nella cancellazione dello stato di autenticazione: {e}")
        return False

def is_auth_valid() -> bool:
    """Verifica se lo stato di autenticazione è valido e non scaduto."""
    auth_data = load_auth_state()
    
    if not auth_data.get("is_logged_in"):
        return False
    
    # Verifica timestamp (24 ore)
    if auth_data.get("timestamp"):
        try:
            timestamp = datetime.fromisoformat(auth_data["timestamp"])
            if datetime.now() - timestamp > timedelta(hours=24):
                return False
        except ValueError:
            return False
    
    return True
