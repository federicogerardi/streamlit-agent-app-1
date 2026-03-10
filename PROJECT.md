# 🤖 AI Chat Hub - Specifiche Tecniche

**Data Creazione**: 10 Marzo 2026  
**Ultimo Aggiornamento**: 10 Marzo 2026  
**Stato**: ✅ Analisi funzionale completata

---

## Stack Tecnologico

### Framework & Runtime
- **Streamlit**: v1.55.0 (framework principale)
- **Python**: 3.9+
- **Architettura**: Multipage app con `st.navigation` e `st.Page`

### Dipendenze Principali
- `openai==2.26.0` - Client OpenAI/OpenRouter
- `httpx==0.28.1` - HTTP client asincrono
- `python-dotenv==1.2.2` - Gestione variabili ambiente

### Autenticazione & Sicurezza
- **OAuth2 Google**: Autenticazione utenti con verifica dominio
- **RBAC**: Sistema ruoli (admin/user/guest) con permessi granulari
- **Secrets Management**: Credenziali via `st.secrets` (non committare)

### Persistenza & Storage
- **Session State**: `st.session_state` per stato locale
- **Cronologia Chat**: Salvataggio automatico sessioni
- **Configurazioni Utente**: Deep linking via `st.query_params`

---

## Architettura Applicativa

### Entry Point
- `streamlit_app.py` - Script principale (multipage navigation)

### Struttura Moduli

#### Views (Pagine)
- `views/1_Chat.py` - Interfaccia chat con streaming LLM
- `views/2_Config.py` - Configurazione modelli e parametri

#### Utils (Business Logic)
- `utils/auth.py` - OAuth2 Google flow
- `utils/auth_persistence.py` - Persistenza login
- `utils/api.py` - Client OpenRouter (streaming)
- `utils/permissions.py` - RBAC e controllo accesso
- `utils/user_management.py` - Gestione utenti e quote
- `utils/session_persistence.py` - Salvataggio cronologia

### Configurazione
- `.streamlit/config.toml` - Impostazioni Streamlit
- `.streamlit/secrets.toml` - Credenziali (gitignored)

---

## Funzionalità Chiave

### 1. Chat Multimodello
- Accesso a decine di modelli LLM via OpenRouter
- Streaming token-by-token in tempo reale
- Gestione contesto conversazione

### 2. Autenticazione Sicura
- OAuth2 Google con verifica dominio autorizzato
- Persistenza sessione tra riavvii
- Logout e gestione token

### 3. Controllo Accesso
- Ruoli: admin, user, guest
- Quote messaggi giornaliere per ruolo
- Permessi granulari per feature

### 4. Deep Linking
- Condivisione configurazione via URL
- Sincronizzazione stato con `st.query_params`

---

## Convenzioni di Codice

- **Linguaggio Commenti**: Italiano
- **Style Guide**: PEP8
- **Type Hints**: Obbligatori
- **Caching**: `@st.cache_data` (dati), `@st.cache_resource` (risorse globali)
- **Fragments**: `@st.fragment` per UI locali (form, contatori)
- **State Management**: Inizializzazione esplicita in `st.session_state`

---

## 📊 ANALISI FUNZIONALE DETTAGLIATA

### 1. FLUSSO AUTENTICAZIONE

#### OAuth2 Google Flow (auth.py)
```
1. Check session_state.is_logged_in
2. Check auth_persistence (24h TTL)
3. Se non autenticato → Mostra login button
4. Callback da Google con 'code' in query_params
5. Exchange code → access_token (server-to-server)
6. Fetch userinfo con token
7. Verifica dominio autorizzato (allowed_domain)
8. Register/Update user in users.json
9. Save auth_state.json (24h TTL)
10. Clear query_params, rerun
```

#### Persistenza Autenticazione (auth_persistence.py)
- **File**: `.streamlit/auth_state.json`
- **TTL**: 24 ore
- **Contenuto**: is_logged_in, user_email, user_role, timestamp
- **Logica**: Carica automaticamente se valida, scade dopo 24h

---

### 2. SISTEMA RBAC (Role-Based Access Control)

#### Ruoli Definiti (permissions.py)
| Ruolo | Level | Chat | Config | Modelli | Msg/Giorno | Descrizione |
|-------|-------|------|--------|---------|------------|------------|
| admin | 3 | ✅ | ✅ | Tutti | ∞ | Accesso completo |
| user | 2 | ✅ | ✅ | 4 modelli | 50 | Accesso limitato |
| guest | 1 | ✅ | ❌ | 2 modelli | 10 | Accesso base |

#### Permessi Granulari
- `access_chat`: Boolean
- `access_config`: Boolean
- `max_messages_per_day`: Int | None
- `allowed_models`: List | None
- `can_clear_history`: Boolean
- `can_export_chat`: Boolean (non implementato)

#### Funzioni Chiave
- `get_role_permissions(role)` - Ritorna dict permessi
- `check_permission(role, permission, value)` - Verifica permesso
- `can_use_model(role, model_id)` - Verifica accesso modello
- `get_daily_limit(role)` - Ritorna limite messaggi

---

### 3. GESTIONE UTENTI (user_management.py)

#### Database Utenti
- **File**: `.streamlit/users.json`
- **Struttura**:
  ```json
  {
    "email@example.com": {
      "email": "email@example.com",
      "role": "user",
      "created_at": "ISO timestamp",
      "last_login": "ISO timestamp",
      "message_count_today": 0,
      "last_message_reset": "ISO timestamp"
    }
  }
  ```

#### Funzioni Principali
- `register_user(email, role)` - Registra/aggiorna utente
- `get_user(email)` - Recupera dati utente
- `increment_message_count(email)` - Incrementa contatore giornaliero
- `get_message_count_today(email)` - Ritorna conteggio odierno
- `reset_daily_count_if_needed(user_data)` - Reset automatico ogni 24h
- `change_user_role(email, new_role)` - Cambio ruolo (admin only)
- `get_all_users()` - Lista tutti utenti (admin only)
- `delete_user(email)` - Cancella utente (admin only)

---

### 4. PERSISTENZA SESSIONE (session_persistence.py)

#### Database Sessioni
- **Directory**: `.streamlit/sessions/`
- **Naming**: `{email_sanitized}_session.json`
- **Struttura**:
  ```json
  {
    "messages": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ],
    "active_model": "openai/gpt-3.5-turbo",
    "temperature": 0.7,
    "last_updated": "ISO timestamp"
  }
  ```

#### Funzioni Principali
- `load_session(user_email)` - Carica sessione
- `save_session(user_email, session_data)` - Salva sessione
- `get_session_messages(user_email)` - Ritorna messaggi
- `save_session_messages(user_email, messages)` - Salva messaggi
- `get_session_config(user_email)` - Ritorna model + temperature
- `save_session_config(user_email, model, temp)` - Salva config
- `clear_session(user_email)` - Cancella sessione
- `cleanup_old_sessions(days)` - Pulizia sessioni vecchie (>30 giorni)

---

### 5. CLIENT API (api.py)

#### OpenRouter Integration
- **Base URL**: `https://openrouter.ai/api/v1`
- **Auth**: API key da `st.secrets["openrouter"]["api_key"]`
- **Client**: OpenAI SDK (compatibile con OpenRouter)

#### Caching
- `@st.cache_resource` - `get_openrouter_client()` (globale, riutilizzabile)
- `@st.cache_data(ttl=3600)` - `fetch_available_models()` (1h TTL)

#### Fallback Modelli
Se fetch fallisce, ritorna lista default:
- `anthropic/claude-3-opus`
- `openai/gpt-4o`
- `meta-llama/llama-3-8b-instruct`

---

### 6. PAGINA CHAT (views/1_Chat.py)

#### Flusso Principale
1. **Protezione**: `require_login()` - Blocca se non autenticato
2. **Verifiche Permessi**:
   - Controlla limite messaggi giornalieri
   - Verifica accesso modello per ruolo
   - Mostra warning se >80% limite raggiunto
3. **Visualizzazione**: Mostra messaggi precedenti da session_state
4. **Input**: `st.chat_input()` con streaming

#### Fragment per Streaming
```python
@st.fragment
def stream_llm_response(prompt: str):
    # Evita full-page rerun durante streaming
    # Usa st.write_stream() per token-by-token rendering
    # Salva risposta in session_state + persistenza
```

#### Conteggio Messaggi
- Incrementa per ogni messaggio user (non solo assistant)
- Usa `increment_message_count(user_email)`
- Reset automatico ogni 24h

---

### 7. PAGINA CONFIGURAZIONE (views/2_Config.py)

#### Sezione Generale (Tutti gli utenti)
1. **Scelta Modello**: Selectbox filtrato per ruolo
2. **Temperatura**: Slider 0.0-2.0 (step 0.1)
3. **Sincronizzazione**: 
   - `st.query_params` per deep-linking
   - `save_session_config()` per persistenza
4. **Gestione Dati**:
   - Cancella cronologia chat
   - Ripristina sessione predefinita

#### Sezione Admin (Solo admin)
1. **Tab Utenti**:
   - Tabella con email, ruolo, created_at, last_login
   - Selectbox per cambio ruolo
   - Button per aggiornare ruolo
2. **Tab Informazioni Sistema** (non completato nel codice)

#### Deep Linking
- URL: `http://localhost:8501/?model={model}&temp={temperature}`
- Sincronizzazione automatica con `st.query_params`

---

### 8. PATTERN IMPLEMENTATI

#### State Management
- `st.session_state` per stato locale (messages, active_model, temperature)
- Inizializzazione implicita tramite widget key
- Sincronizzazione con persistenza via callback

#### Caching Strategy
- `@st.cache_resource` - Client OpenRouter (globale)
- `@st.cache_data(ttl=3600)` - Lista modelli (1h)
- Nessun caching per dati utente (sempre fresh)

#### Fragment Usage
- `@st.fragment` su `stream_llm_response()` per evitare full-page rerun
- Mantiene fluido il resto dell'app durante streaming

#### Error Handling
- Try-except con `st.error()` per feedback user-friendly
- Fallback per modelli se fetch fallisce
- Validazione permessi prima di operazioni critiche

#### Persistenza
- JSON files in `.streamlit/` (non committare)
- Sanitizzazione email per nomi file
- Timestamp per tracking e cleanup

---

### 9. FLUSSI CRITICI

#### Login Flow
```
User → Click "Accedi con Google" 
→ Redirect a Google OAuth2 
→ Google callback con code 
→ Exchange code → token 
→ Fetch userinfo 
→ Verifica dominio 
→ Register/Update user 
→ Save auth_state (24h) 
→ Clear query_params 
→ Rerun app
```

#### Chat Flow
```
User input → Increment counter 
→ Append to session_state.messages 
→ Display user message 
→ Fragment: Call OpenRouter API 
→ Stream response token-by-token 
→ Append assistant message 
→ Save to persistenza 
→ Display complete
```

#### Config Update Flow
```
User changes model/temp 
→ on_change callback 
→ Update st.query_params 
→ Save to session_persistence 
→ Rerun (local, non full-page)
```

---

### 10. PUNTI DI FORZA

✅ **Autenticazione Robusta**: OAuth2 Google con verifica dominio  
✅ **RBAC Granulare**: 3 ruoli con permessi specifici  
✅ **Persistenza Completa**: Auth, sessioni, utenti salvati  
✅ **Streaming Ottimizzato**: Fragment per evitare full-page rerun  
✅ **Deep Linking**: Condivisione config via URL  
✅ **Caching Intelligente**: Resource + data con TTL  
✅ **Gestione Quote**: Limite messaggi giornalieri per ruolo  
✅ **Admin Panel**: Gestione utenti e ruoli  

---

### 11. AREE DI MIGLIORAMENTO

⚠️ **Entry Point Mancante**: `streamlit_app.py` non trovato - da creare  
⚠️ **Config Streamlit**: `.streamlit/config.toml` non mostrato  
⚠️ **Export Chat**: Feature `can_export_chat` non implementata  
⚠️ **Tab Informazioni Sistema**: Incompleta in 2_Config.py  
⚠️ **Cleanup Sessioni**: Funzione `cleanup_old_sessions()` incompleta  
⚠️ **Testing**: Nessun test file trovato  
⚠️ **Logging**: Nessun sistema di logging strutturato  
⚠️ **Rate Limiting**: Nessun rate limiting API implementato  

---

## 🎯 Prossimi Step

- [ ] Creare `streamlit_app.py` con `st.navigation`
- [ ] Verificare/creare `.streamlit/config.toml`
- [ ] Completare `cleanup_old_sessions()` in session_persistence.py
- [ ] Implementare export chat feature
- [ ] Aggiungere logging strutturato
- [ ] Creare test suite
- [ ] Documentare API endpoints
- [ ] Implementare rate limiting

---

## Flussi Critici Implementati

### 1. OAuth2 Google Flow
- Redirect a Google OAuth2
- Exchange code → access_token (server-to-server)
- Fetch userinfo con token
- Verifica dominio autorizzato
- Register/Update user in users.json
- Save auth_state.json (24h TTL)

### 2. Chat Flow
- Incrementa contatore messaggi
- Append a session_state.messages
- Fragment: Call OpenRouter API
- Stream response token-by-token
- Append assistant message
- Save to persistenza

### 3. Config Update Flow
- on_change callback
- Update st.query_params (deep-linking)
- Save to session_persistence
- Rerun (local, non full-page)

## Database Persistenti

### 1. Auth State (`.streamlit/auth_state.json`)
- TTL: 24 ore
- Contenuto: is_logged_in, user_email, user_role, timestamp

### 2. Users (`.streamlit/users.json`)
- Email → {role, created_at, last_login, message_count_today, last_message_reset}
- Default: admin@example.com (admin)

### 3. Sessions (`.streamlit/sessions/{email_sanitized}_session.json`)
- Contenuto: messages[], active_model, temperature, last_updated
- Cleanup: >30 giorni

## Protocollo Memoria Progetto

### Daily Logs
- Cartella: `memory/`
- Naming: `[numero_incrementale]-[MMDDYYYY].md`
- Logica: Append se esiste, crea nuovo se non esiste

### Structural Memory
- File: `PROJECT.md` (questo file)
- Aggiornamento: Costante durante lo sviluppo
- Contenuto: Stack, architettura, convenzioni, flussi

---

## 📊 ANALISI FUNZIONALE DETTAGLIATA (10 Marzo 2026)

### 🔐 Modulo Autenticazione (`utils/auth.py`)

**Responsabilità Primaria:**
- Gestione completa flusso OAuth2/OIDC Google
- Blocco accesso non autenticato tramite `st.stop()`
- Verifica dominio autorizzato (backend security)

**Flusso Dettagliato:**
1. `require_login()` → Controlla `st.session_state.is_logged_in`
2. Se falso → Verifica persistenza con `is_auth_valid()` (24h TTL)
3. Se scaduto/assente → Mostra UI login con pulsante OAuth
4. Intercetta parametro `code` da callback Google
5. Scambio code → access_token (comunicazione server-to-server con Google)
6. Lettura userinfo tramite access_token
7. Verifica `allowed_domain` (es. `@company.com`)
8. Se dominio non autorizzato → `st.error()` + `st.stop()`
9. Se autorizzato → `register_user()` + `save_auth_state()`
10. `st.rerun()` → Accesso app

**Secrets Richiesti:**
```toml
[auth]
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
redirect_uri = "http://localhost:8501"
allowed_domain = "@company.com"  # Opzionale
```

**Gestione Errori:**
- HTTP 401 → Messaggio credenziali
- Dominio non autorizzato → Blocco con messaggio
- Eccezione generica → Retry button

---

### 🔑 Persistenza Autenticazione (`utils/auth_persistence.py`)

**Responsabilità:**
- Salvataggio stato login tra refresh pagina
- Scadenza automatica dopo 24 ore
- Gestione file `auth_state.json`

**Struttura Dati:**
```json
{
  "is_logged_in": true,
  "user_email": "user@company.com",
  "user_role": "user",
  "timestamp": "2026-03-10T14:30:00.123456"
}
```

**Funzioni Chiave:**
- `save_auth_state(email, role)` → Salva con timestamp
- `load_auth_state()` → Carica e verifica scadenza
- `is_auth_valid()` → Controlla validità (< 24h)
- `clear_auth_state()` → Logout (cancella file)

**Logica Scadenza:**
```python
if datetime.now() - timestamp > timedelta(hours=24):
    clear_auth_state()  # Forza re-login
```

---

### 👥 Gestione Utenti (`utils/user_management.py`)

**Responsabilità:**
- CRUD utenti in `users.json`
- Conteggio messaggi giornalieri
- Reset automatico contatore a mezzanotte

**Struttura users.json:**
```json
{
  "user@company.com": {
    "email": "user@company.com",
    "role": "user",
    "created_at": "2026-03-10T10:00:00",
    "last_login": "2026-03-10T14:30:00",
    "message_count_today": 5,
    "last_message_reset": "2026-03-10T00:00:00"
  }
}
```

**Funzioni Principali:**
- `register_user(email, role="user")` → Crea nuovo o aggiorna last_login
- `get_user(email)` → Recupera dati utente
- `increment_message_count(email)` → Incrementa contatore (ritorna nuovo valore)
- `get_message_count_today(email)` → Legge contatore
- `reset_daily_count_if_needed(user_data)` → Reset se (now - last_reset) >= 1 giorno
- `change_user_role(email, new_role)` → Cambio ruolo (admin only)
- `get_all_users()` → Lista utenti (admin only)
- `delete_user(email)` → Cancella utente (admin only)

**Logica Reset Giornaliero:**
```python
last_reset = datetime.fromisoformat(user_data["last_message_reset"])
if (now - last_reset).days >= 1:
    user_data["message_count_today"] = 0
    user_data["last_message_reset"] = now.isoformat()
```

---

### 🎯 Sistema Permessi (`utils/permissions.py`)

**Responsabilità:**
- Definizione ruoli e permessi
- Validazione accesso a risorse
- Mapping modelli autorizzati per ruolo

**Matrice Ruoli:**

| Ruolo | Livello | Chat | Config | Msg/Giorno | Modelli | Cancella |
|-------|---------|------|--------|-----------|---------|----------|
| admin | 3 | ✅ | ✅ | ∞ | Tutti | ✅ |
| user | 2 | ✅ | ✅ | 50 | 4 | ✅ |
| guest | 1 | ✅ | ❌ | 10 | 2 | ❌ |

**Modelli Autorizzati:**
- **Admin:** Tutti i modelli da OpenRouter
- **User:** gpt-3.5-turbo, gpt-4o-mini, claude-3-haiku, llama-3-8b
- **Guest:** gpt-3.5-turbo, claude-3-haiku

**Funzioni:**
- `get_role_permissions(role)` → Dict permessi
- `check_permission(role, permission, value=None)` → Verifica permesso
- `can_use_model(role, model_id)` → Verifica accesso modello
- `get_daily_limit(role)` → Ritorna limite messaggi (None = nessuno)

---

### 💾 Persistenza Sessione (`utils/session_persistence.py`)

**Responsabilità:**
- Salvataggio cronologia messaggi per utente
- Persistenza configurazione (modello, temperatura)
- Gestione file sessione in `.streamlit/sessions/`

**Struttura Session File:**
```json
{
  "messages": [
    {"role": "user", "content": "Ciao"},
    {"role": "assistant", "content": "Salve!"}
  ],
  "active_model": "openai/gpt-3.5-turbo",
  "temperature": 0.7,
  "last_updated": "2026-03-10T14:30:00"
}
```

**Naming File:**
- Email: `user@company.com`
- Sanitizzato: `user_at_company_com_session.json`
- Path: `.streamlit/sessions/user_at_company_com_session.json`

**Funzioni:**
- `load_session(user_email)` → Carica cronologia (default se non esiste)
- `save_session(user_email, session_data)` → Salva sessione
- `save_session_messages(user_email, messages)` → Salva solo messaggi
- `save_session_config(user_email, model, temp)` → Salva config
- `get_session_config(user_email)` → Legge config
- `clear_session(user_email)` → Ripristina predefiniti

---

### 🔌 Client API (`utils/api.py`)

**Responsabilità:**
- Inizializzazione client OpenAI (compatibile OpenRouter)
- Caching client con `@st.cache_resource`
- Fetch lista modelli disponibili

**Configurazione Client:**
```python
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["openrouter"]["api_key"],
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Chat Hub Local"
    }
)
```

**Funzioni:**
- `get_openrouter_client()` → Ritorna client cached (resource)
- `fetch_available_models()` → Recupera modelli (cache 1h)

**Caching Strategy:**
- `@st.cache_resource` → Client (globale, una sola istanza)
- `@st.cache_data(ttl=3600)` → Modelli (refresh ogni ora)

---

### 🎨 Entrypoint (`streamlit_app.py`)

**Responsabilità:**
- Configurazione pagina
- Autenticazione globale
- Caricamento/sincronizzazione sessione
- Routing multipagina
- Sidebar profilo utente

**Flusso Inizializzazione:**
1. `st.set_page_config()` → Titolo, icona, layout wide
2. `require_login()` → Blocca se non autenticato
3. Carica sessione da persistenza (se prima volta)
4. Sincronizza URL → Session State (query params)
5. Sincronizza Session State → URL (continuo)
6. Mostra profilo utente in sidebar
7. Inizializza client API
8. Esegue routing con `st.navigation()`

**Query Parameters Sincronizzati:**
- `model` → Modello LLM attivo
- `temp` → Temperatura (0.0-2.0)

**Sidebar Features:**
- Email utente
- Ruolo utente
- Conteggio messaggi giornalieri (se limite presente)
- Pulsante logout
- Pulsante salvataggio manuale sessione

---

### 💬 Pagina Chat (`views/1_Chat.py`)

**Responsabilità:**
- Visualizzazione cronologia messaggi
- Input chat con validazione permessi
- Streaming risposta LLM
- Conteggio messaggi e verifica quote

**Flusso Messaggi:**
1. Verifica limite giornaliero → `st.error()` + `st.stop()` se raggiunto
2. Verifica autorizzazione modello → `st.error()` + `st.stop()` se non autorizzato
3. Mostra cronologia precedente con `st.chat_message()`
4. Input chat (disabilitato se non autenticato)
5. Salva messaggio utente in `st.session_state.messages`
6. Mostra messaggio con `st.chat_message("user")`
7. Incrementa contatore con `increment_message_count()`
8. Chiama `stream_llm_response()` (fragment)
   - Prepara lista messaggi
   - Chiama OpenRouter API
   - Streaming con `st.write_stream()`
   - Salva risposta in session_state
   - `save_session_messages()` → Persistenza

**Fragment Optimization:**
- `@st.fragment` su `stream_llm_response()` → Solo questa parte si riesegue
- Evita rerun completo durante streaming
- Mantiene UI fluida e responsiva

**Validazioni:**
- Limite raggiunto → `st.error()` + `st.stop()`
- Modello non autorizzato → `st.error()` + `st.stop()`
- Errore API 401 → Messaggio credenziali
- Errore generico → Messaggio con dettagli

---

### ⚙️ Pagina Configurazione (`views/2_Config.py`)

**Responsabilità:**
- Selezione modello LLM
- Regolazione temperatura
- Gestione cronologia chat
- Pannello amministrativo (solo admin)

**Sezioni:**

#### A. Impostazioni Generali
- **Modello:** Selectbox filtrato per ruolo (can_use_model)
- **Temperatura:** Slider 0.0-2.0 con help text
- Callback `update_query_params()` → Sincronizza URL + persistenza

#### B. Gestione Dati
- **Cancella Cronologia:** Svuota messaggi + salva
- **Ripristina Predefiniti:** Reset modello (gpt-3.5-turbo) e temperatura (0.7)

#### C. Sezione Admin (solo `user_role == "admin"`)
- **Tab Utenti:**
  - Tabella utenti (email, ruolo, creato, ultimo login)
  - Selectbox cambio ruolo
  - Pulsante aggiornamento ruolo
  - Rerun dopo cambio
  
- **Tab Informazioni Sistema:**
  - (Placeholder per future info)

---

### 🔄 Flussi Critici

#### Flusso 1: Login Utente
```
Accesso app
  ↓
require_login() → Controlla session_state.is_logged_in
  ↓
Se False → is_auth_valid() (controlla persistenza 24h)
  ↓
Se scaduto/assente → Mostra pulsante OAuth Google
  ↓
Utente clicca → Redirect Google OAuth
  ↓
Google callback con 'code' in URL
  ↓
Scambio code → access_token (server-to-server)
  ↓
Lettura userinfo con access_token
  ↓
Verifica dominio autorizzato
  ↓
Se non autorizzato → st.error() + st.stop()
  ↓
register_user() → Crea/aggiorna in users.json
  ↓
save_auth_state() → Salva stato (24h TTL)
  ↓
st.query_params.clear() → Rimuove 'code' (usa una sola volta)
  ↓
st.rerun() → Accesso app
```

#### Flusso 2: Invio Messaggio Chat
```
Utente digita messaggio
  ↓
Verifica limite giornaliero
  ├─ get_daily_limit(user_role)
  ├─ get_message_count_today(user_email)
  └─ Se count >= limit → st.error() + st.stop()
  ↓
Verifica autorizzazione modello
  ├─ can_use_model(user_role, current_model)
  └─ Se False → st.error() + st.stop()
  ↓
Salva messaggio in st.session_state.messages
  ↓
Mostra messaggio con st.chat_message("user")
  ↓
increment_message_count(user_email)
  ↓
stream_llm_response(prompt) [FRAGMENT]
  ├─ Prepara lista messaggi
  ├─ client.chat.completions.create(stream=True)
  ├─ st.write_stream() → Streaming UI
  ├─ Salva risposta in session_state
  └─ save_session_messages() → Persistenza
```

#### Flusso 3: Cambio Configurazione
```
Utente modifica modello/temperatura
  ↓
on_change callback → update_query_params()
  ├─ st.query_params.update() → URL sync
  └─ save_session_config() → Persistenza
  ↓
Sincronizzazione automatica tra:
  - Session state
  - URL query params
  - File sessione (.streamlit/sessions/)
```

---

### 📁 Struttura Persistenza

```
.streamlit/
├── config.toml                          # Configurazione Streamlit
├── secrets.toml                         # Credenziali (gitignored)
├── users.json                           # Database utenti
├── auth_state.json                      # Stato autenticazione corrente
└── sessions/
    ├── user_at_company_com_session.json
    ├── admin_at_company_com_session.json
    └── ...
```

**Ciclo Vita Dati:**
1. **Login:** `auth_state.json` (24h TTL)
2. **Messaggi:** `sessions/{email}_session.json` (persistente)
3. **Utenti:** `users.json` (persistente)
4. **Conteggio Msg:** `users.json` (reset giornaliero)

---

### ✅ Funzionalità Implementate

- [x] Autenticazione OAuth2/OIDC Google
- [x] Verifica dominio autorizzato
- [x] Sistema ruoli (Admin, User, Guest)
- [x] Permessi granulari per ruolo
- [x] Limite messaggi giornalieri
- [x] Persistenza sessione chat
- [x] Streaming LLM con fragment
- [x] Sincronizzazione URL ↔ Session
- [x] Pannello admin gestione utenti
- [x] Caching client e modelli

### ⏳ Potenziali Miglioramenti

- [ ] Export cronologia chat (PDF/JSON)
- [ ] Statistiche uso per admin
- [ ] Gestione team/organizzazioni
- [ ] Rate limiting per IP
- [ ] Audit log azioni utenti
- [ ] Dark mode
- [ ] Supporto multi-lingua
- [ ] Webhook per notifiche

---

**Ultimo Aggiornamento**: 10 Marzo 2026
**Versione Progetto**: 1.0.0 (Analisi Funzionale Completata)
**Status**: ✅ Architettura validata, pronto per sviluppo feature
