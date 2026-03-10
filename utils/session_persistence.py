"""
Gestione della persistenza della sessione utente.
Salva e carica la cronologia chat, configurazioni e stato della sessione.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Percorso della directory sessioni relativo a .streamlit/
SESSIONS_DIR = Path(__file__).parent.parent / ".streamlit" / "sessions"

def ensure_sessions_dir_exists():
    """Crea la directory sessions se non esiste."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_session_file(user_email: str) -> Path:
    """Ritorna il percorso del file sessione per un utente."""
    ensure_sessions_dir_exists()
    # Sanitizza l'email per usarla come nome file
    safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
    return SESSIONS_DIR / f"{safe_email}_session.json"

def load_session(user_email: str) -> Dict:
    """
    Carica la sessione salvata di un utente.
    Ritorna un dict con messages, active_model, temperature.
    Se non esiste, ritorna un dict vuoto.
    """
    session_file = get_session_file(user_email)
    
    if not session_file.exists():
        return {
            "messages": [],
            "active_model": "openai/gpt-3.5-turbo",
            "temperature": 0.7,
            "last_updated": datetime.now().isoformat()
        }
    
    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
        return session_data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Errore nel caricamento della sessione per {user_email}: {e}")
        return {
            "messages": [],
            "active_model": "openai/gpt-3.5-turbo",
            "temperature": 0.7,
            "last_updated": datetime.now().isoformat()
        }

def save_session(user_email: str, session_data: Dict) -> bool:
    """
    Salva la sessione di un utente.
    
    Args:
        user_email: Email dell'utente
        session_data: Dict con messages, active_model, temperature
    
    Returns:
        True se salvato con successo, False altrimenti
    """
    session_file = get_session_file(user_email)
    
    try:
        ensure_sessions_dir_exists()
        
        # Aggiungi timestamp di ultimo aggiornamento
        session_data["last_updated"] = datetime.now().isoformat()
        
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
        
        return True
    except IOError as e:
        print(f"Errore nel salvataggio della sessione per {user_email}: {e}")
        return False

def get_session_messages(user_email: str) -> List[Dict]:
    """Ritorna la lista dei messaggi salvati per un utente."""
    session_data = load_session(user_email)
    return session_data.get("messages", [])

def save_session_messages(user_email: str, messages: List[Dict]) -> bool:
    """Salva la lista dei messaggi per un utente."""
    session_data = load_session(user_email)
    session_data["messages"] = messages
    return save_session(user_email, session_data)

def get_session_config(user_email: str) -> Dict:
    """Ritorna la configurazione salvata (model, temperature) per un utente."""
    session_data = load_session(user_email)
    return {
        "active_model": session_data.get("active_model", "openai/gpt-3.5-turbo"),
        "temperature": session_data.get("temperature", 0.7)
    }

def save_session_config(user_email: str, active_model: str, temperature: float) -> bool:
    """Salva la configurazione (model, temperature) per un utente."""
    session_data = load_session(user_email)
    session_data["active_model"] = active_model
    session_data["temperature"] = temperature
    return save_session(user_email, session_data)

def clear_session(user_email: str) -> bool:
    """Cancella la sessione di un utente."""
    session_file = get_session_file(user_email)
    
    try:
        if session_file.exists():
            session_file.unlink()
        return True
    except IOError as e:
        print(f"Errore nella cancellazione della sessione per {user_email}: {e}")
        return False

def get_session_last_updated(user_email: str) -> Optional[str]:
    """Ritorna il timestamp dell'ultimo aggiornamento della sessione."""
    session_data = load_session(user_email)
    return session_data.get("last_updated")

def cleanup_old_sessions(days: int = 30) -> int:
    """
    Cancella le sessioni non aggiornate da più di N giorni.
    Ritorna il numero di sessioni cancellate.
    """
    ensure_sessions_dir_exists()
    
    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for session_file in SESSIONS_DIR.glob("*_session.json"):
        try:
            with open(session_file, "r") as f:
                session_data = json.load(f)
            
            last_updated_str = session_data.get("last_updated")
            if last_updated_str:
                last_updated = datetime.fromisoformat(last_updated_str)
                
                if last_updated < cutoff_date:
                    session_file.unlink()
                    deleted_count += 1
        except (json.JSONDecodeError, IOError, ValueError):
            # Se il file è corrotto, cancellalo
            try:
                session_file.unlink()
                deleted_count += 1
            except IOError:
                pass
    
    return deleted_count
