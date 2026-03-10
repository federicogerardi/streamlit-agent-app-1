"""
Definizione dei permessi e privilegi per ogni ruolo utente.
"""

# Definizione dei ruoli disponibili
ROLES = {
    "admin": {
        "name": "Amministratore",
        "description": "Accesso completo a tutte le funzionalità",
        "level": 3
    },
    "user": {
        "name": "Utente Standard",
        "description": "Accesso limitato con quote giornaliere",
        "level": 2
    },
    "guest": {
        "name": "Ospite",
        "description": "Accesso limitato alle funzionalità di base",
        "level": 1
    }
}

# Permessi per ogni ruolo
PERMISSIONS = {
    "admin": {
        "access_chat": True,
        "access_config": True,
        "max_messages_per_day": None,  # Nessun limite
        "allowed_models": None,  # Tutti i modelli
        "can_clear_history": True,
        "can_export_chat": False,  # Non ancora implementato
    },
    "user": {
        "access_chat": True,
        "access_config": True,
        "max_messages_per_day": 50,  # 50 messaggi al giorno (user + assistant)
        "allowed_models": [
            "openai/gpt-3.5-turbo",
            "openai/gpt-4o-mini",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3-8b-instruct"
        ],
        "can_clear_history": True,
        "can_export_chat": False,
    },
    "guest": {
        "access_chat": True,
        "access_config": False,  # Non può accedere alla config
        "max_messages_per_day": 10,  # 10 messaggi al giorno
        "allowed_models": [
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku"
        ],
        "can_clear_history": False,
        "can_export_chat": False,
    }
}

def get_role_permissions(role: str) -> dict:
    """Ritorna i permessi per un dato ruolo."""
    return PERMISSIONS.get(role, {})

def check_permission(role: str, permission: str, value=None) -> bool:
    """
    Verifica se un ruolo ha un determinato permesso.
    Se value è fornito, confronta il valore (utile per liste).
    """
    perms = get_role_permissions(role)
    
    if permission not in perms:
        return False
    
    perm_value = perms[permission]
    
    # Se il permesso è una lista (allowed_models), controlla se value è dentro
    if isinstance(perm_value, list):
        return value in perm_value if value else True
    
    # Altrimenti ritorna il valore booleano/numerico
    return perm_value

def can_use_model(role: str, model_id: str) -> bool:
    """Verifica se un ruolo può usare un modello specifico."""
    allowed = PERMISSIONS.get(role, {}).get("allowed_models")
    
    if allowed is None:  # Accesso a tutti i modelli
        return True
    
    return model_id in allowed

def get_daily_limit(role: str) -> int | None:
    """Ritorna il limite di messaggi giornalieri per un ruolo. None = nessun limite."""
    return PERMISSIONS.get(role, {}).get("max_messages_per_day")
