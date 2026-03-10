"""
Gestione degli utenti: persistenza, inizializzazione, statistiche d'uso.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Percorso del file utenti relativo a .streamlit/
USERS_FILE = Path(__file__).parent.parent / ".streamlit" / "users.json"

def ensure_users_file_exists():
    """Crea il file users.json se non esiste."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if not USERS_FILE.exists():
        default_users = {
            "admin@example.com": {
                "email": "admin@example.com",
                "role": "admin",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "message_count_today": 0,
                "last_message_reset": datetime.now().isoformat()
            }
        }
        with open(USERS_FILE, "w") as f:
            json.dump(default_users, f, indent=2)

def load_users() -> dict:
    """Carica il database degli utenti dal file JSON."""
    ensure_users_file_exists()
    
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users: dict):
    """Salva il database degli utenti nel file JSON."""
    ensure_users_file_exists()
    
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_user(email: str) -> Optional[dict]:
    """Recupera i dati di un utente specifico."""
    users = load_users()
    return users.get(email)

def user_exists(email: str) -> bool:
    """Verifica se un utente è già registrato."""
    return email in load_users()

def register_user(email: str, role: str = "user") -> dict:
    """
    Registra un nuovo utente nel sistema.
    Se l'utente esiste già, aggiorna solo il last_login.
    """
    users = load_users()
    now = datetime.now().isoformat()
    
    if email in users:
        # L'utente esiste, aggiorna il login
        users[email]["last_login"] = now
        users[email] = reset_daily_count_if_needed(users[email])
    else:
        # Nuovo utente
        users[email] = {
            "email": email,
            "role": role,
            "created_at": now,
            "last_login": now,
            "message_count_today": 0,
            "last_message_reset": now
        }
    
    save_users(users)
    return users[email]

def reset_daily_count_if_needed(user_data: dict) -> dict:
    """
    Resetta il conteggio messaggi giornalieri se è un nuovo giorno.
    Ritorna il user_data aggiornato.
    """
    last_reset = datetime.fromisoformat(user_data["last_message_reset"])
    now = datetime.now()
    
    # Se è passato più di un giorno, resetta il contatore
    if (now - last_reset).days >= 1:
        user_data["message_count_today"] = 0
        user_data["last_message_reset"] = now.isoformat()
    
    return user_data

def increment_message_count(email: str) -> int:
    """
    Incrementa il conteggio di messaggi dell'utente per il giorno.
    Ritorna il nuovo conteggio.
    """
    users = load_users()
    
    if email not in users:
        return 0
    
    users[email] = reset_daily_count_if_needed(users[email])
    users[email]["message_count_today"] += 1
    
    save_users(users)
    return users[email]["message_count_today"]

def get_message_count_today(email: str) -> int:
    """Ritorna il numero di messaggi inviati oggi dall'utente."""
    user = get_user(email)
    if not user:
        return 0
    
    user = reset_daily_count_if_needed(user)
    return user["message_count_today"]

def change_user_role(email: str, new_role: str):
    """Cambia il ruolo di un utente (solo per admin)."""
    users = load_users()
    
    if email not in users:
        raise ValueError(f"Utente {email} non trovato.")
    
    users[email]["role"] = new_role
    save_users(users)

def get_all_users() -> dict:
    """Ritorna tutti gli utenti (per admin)."""
    return load_users()

def delete_user(email: str):
    """Cancella un utente dal sistema (solo per admin)."""
    users = load_users()
    
    if email in users:
        del users[email]
        save_users(users)
