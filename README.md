# 🤖 AI Chat Hub

Un'applicazione web moderna per interagire con modelli LLM tramite OpenRouter, con autenticazione OAuth2 Google e gestione avanzata delle sessioni.

## 🎯 Caratteristiche Principali

- **Chat Multimodello:** Accesso a decine di modelli LLM (GPT, Claude, Llama, etc.) tramite OpenRouter
- **Autenticazione Sicura:** OAuth2 Google con verifica dominio autorizzato
- **Persistenza Sessione:** Cronologia chat e configurazioni salvate automaticamente
- **Controllo Accesso:** Sistema di ruoli (admin/user/guest) con permessi granulari
- **Limiti Giornalieri:** Quote messaggi per ruolo per gestire i costi API
- **Streaming in Tempo Reale:** Risposta dell'LLM renderizzata token-by-token
- **Deep Linking:** Condivisione configurazione via URL

## 🚀 Quick Start

### Prerequisiti

- Python 3.9+
- Account Google (per OAuth2)
- API Key OpenRouter

### Installazione

1. **Clona il repository**
   ```bash
   git clone <repository-url>
   cd streamlit-agent-app-1
   ```

2. **Crea ambiente virtuale**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # su Windows: .venv\Scripts\activate
   ```

3. **Installa dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura secrets**
   ```bash
   mkdir -p .streamlit
   cat > .streamlit/secrets.toml << 'EOF'
   [auth]
   client_id = "tuo-client-id-google"
   client_secret = "tuo-client-secret-google"
   redirect_uri = "http://localhost:8501"
   allowed_domain = "@example.com"

   [openrouter]
   api_key = "sk-or-..."
   EOF
   ```

   **Nota:** Non committare `secrets.toml` - aggiungi a `.gitignore`

5. **Avvia l'app**
   ```bash
   streamlit run streamlit_app.py
   ```

   L'app sarà disponibile su `http://localhost:8501`

## 📋 Configurazione

### Google OAuth2

1. Vai a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto
3. Abilita "Google+ API"
4. Crea credenziali OAuth2 (tipo: Web application)
5. Aggiungi `http://localhost:8501` come authorized redirect URI
6. Copia `client_id` e `client_secret` in `secrets.toml`

### OpenRouter API

1. Registrati su [OpenRouter](https://openrouter.ai/)
2. Genera una API key
3. Copia in `secrets.toml` sotto `[openrouter]`

## 📁 Struttura Progetto

```
streamlit-agent-app-1/
├── streamlit_app.py           # Entry point
├── views/
│   ├── 1_Chat.py              # Pagina chat
│   └── 2_Config.py            # Pagina configurazione
├── utils/
│   ├── auth.py                # Autenticazione OAuth2
│   ├── auth_persistence.py    # Persistenza login
│   ├── api.py                 # Client OpenRouter
│   ├── permissions.py         # Sistema RBAC
│   ├── user_management.py     # Gestione utenti
│   └── session_persistence.py # Persistenza sessione
├── .streamlit/
│   ├── config.toml            # Configurazione Streamlit
│   └── secrets.toml           # Secrets (non committare)
├── docs/
│   └── dev_specs_v2.md        # Specifica tecnica
└── README.md                  # Questo file
```

## 🔐 Sicurezza

- **OAuth2 Google:** Autenticazione standard industry
- **Verifica Dominio:** Solo email autorizzate possono accedere
- **Persistenza Sicura:** Stato login con scadenza 24 ore
- **Isolamento Utente:** Ogni utente ha sessione isolata
- **Secrets Management:** Credenziali in `secrets.toml` (non committare)

## 👥 Ruoli e Permessi

| Ruolo | Chat | Config | Modelli | Msg/Giorno |
|-------|------|--------|---------|------------|
| Admin | ✅ | ✅ | Tutti | Illimitati |
| User | ✅ | ✅ | 4 modelli | 50 |
| Guest | ✅ | ❌ | 2 modelli | 10 |

## 📊 Dati Persistenti

L'app salva automaticamente:
- **Cronologia chat** - Messaggi per utente
- **Configurazione** - Modello e temperatura selezionati
- **Stato login** - Autenticazione con scadenza 24 ore
- **Statistiche utente** - Conteggio messaggi giornalieri

Tutti i dati sono salvati localmente in `.streamlit/`:
- `users.json` - Database utenti
- `auth_state.json` - Stato autenticazione
- `sessions/` - Cronologie chat per utente

## 🧪 Testing

```bash
# Testare persistenza sessione
python test_persistence.py

# Pulire sessioni vecchie (>30 giorni)
python -c "from utils.session_persistence import cleanup_old_sessions; cleanup_old_sessions(days=30)"
```

## 📚 Documentazione

- **`docs/dev_specs_v2.md`** - Specifica tecnica completa per sviluppatori
- **`PERSISTENCE.md`** - Documentazione persistenza sessione (se presente)
- **`PERSISTENCE_USAGE.md`** - Guida utente persistenza (se presente)

## 🛠️ Sviluppo

### Aggiungere un Nuovo Modello

1. Modifica `utils/permissions.py` - Aggiungi modello alla lista autorizzata
2. Il modello sarà disponibile in configurazione

### Aggiungere un Nuovo Ruolo

1. Modifica `utils/permissions.py` - Aggiungi ruolo in `ROLES` e `PERMISSIONS`
2. Modifica `utils/user_management.py` - Aggiorna logica se necessario

### Modificare Limiti Giornalieri

1. Modifica `utils/permissions.py` - Cambia `max_messages_per_day` per ruolo

## 🐛 Troubleshooting

### "Accesso negato: L'email non appartiene all'organizzazione"

- Verifica che l'email sia nel dominio autorizzato (`allowed_domain` in secrets.toml)
- Usa un account Google del dominio corretto

### "Errore di Autenticazione API"

- Verifica che la API key OpenRouter sia corretta in `secrets.toml`
- Controlla che l'account OpenRouter abbia credito disponibile

### "Sessione persa dopo refresh"

- Verifica che `.streamlit/auth_state.json` esista e sia leggibile
- Controlla i permessi della directory `.streamlit/`

## 📝 Variabili d'Ambiente

Tutte le configurazioni sensibili vanno in `.streamlit/secrets.toml`:

```toml
[auth]
client_id = "..."           # Google OAuth2 Client ID
client_secret = "..."       # Google OAuth2 Client Secret
redirect_uri = "..."        # URL callback (es. http://localhost:8501)
allowed_domain = "..."      # Dominio autorizzato (es. @example.com)

[openrouter]
api_key = "..."             # OpenRouter API Key
```

## 🚀 Deploy in Produzione

Per deploy su Streamlit Cloud:

1. Crea repository GitHub
2. Connetti a [Streamlit Cloud](https://streamlit.io/cloud)
3. Configura secrets in Streamlit Cloud dashboard
4. Deploy automatico da GitHub

**Nota:** Aggiorna `redirect_uri` in Google OAuth2 e `secrets.toml` con URL di produzione.



---

**Versione:** 1.0  
**Data:** 10 Marzo 2026  
**Framework:** Streamlit v1.55.0
