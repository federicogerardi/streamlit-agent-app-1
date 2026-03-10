# AI Chat Hub Implementation Plan

This document outlines the architecture and implementation steps for the AI Chat Hub application based on the provided technical specifications ([dev_specs.md](file:///home/federico/Dev/streamlit-agent-app-1/dev_specs.md)).

## Goal Description
Implement a Streamlit-based (v1.55.0) AI Chat Hub that integrates with OpenRouter for LLM access and utilizes OIDC for user authentication. The application will feature a multi-page structure, centralized state management, and an optimized chat interface using Streamlit fragments (`@st.fragment`) to ensure smooth streaming of model responses without full page reruns.

## User Review Required
> [!IMPORTANT]
> - **Authentication**: The specification requires OIDC login (`st.login`), but Streamlit Community Cloud's native `st.login` specifically works with their built-in auth, or requires custom OIDC implementations. For this implementation, I plan to build a mock authentication layer or use a generic pattern that you can hook into your specific identity provider (e.g., Auth0, Google) using standard OAuth libraries. Please confirm if a mock auth is acceptable for now.
> - **Database/Persistence**: The specification mentions "Cronologia: Visualizzazione di sessioni passate (se implementato database esterno)." Since no DB is specified, session history will only persist in `st.session_state` for the lifetime of the user's session.

## Proposed Changes

### App Core & Setup
#### [NEW] [streamlit_app.py](file:///home/federico/Dev/streamlit-agent-app-1/streamlit_app.py)
- **Role**: Entrypoint of the application.
- **Features**: 
  - Initializes `st.session_state` variables (`messages`, `active_model`, `api_client`).
  - Handles authentication routing (checks `st.user.is_logged_in` or equivalent custom state).
  - Sets up the `st.navigation` routing to the Chat and Config pages.

#### [NEW] [.streamlit/secrets.toml](file:///home/federico/Dev/streamlit-agent-app-1/.streamlit/secrets.toml)
- **Role**: Configuration file for secrets.
- **Features**: Contains template structure for `[auth]` and `[openrouter]` secrets as defined in the technical specification. **Note:** we will provide a template `secrets.example.toml` to avoid committing real secrets.

### Utilities
#### [NEW] [utils/auth.py](file:///home/federico/Dev/streamlit-agent-app-1/utils/auth.py)
- **Role**: Authentication helper functions.
- **Features**: Mock or basic framework for OIDC login/logout flow handling redirect URIs and token verification.

#### [NEW] [utils/api.py](file:///home/federico/Dev/streamlit-agent-app-1/utils/api.py)
- **Role**: OpenRouter API integration.
- **Features**: 
  - `get_openrouter_client()`: Singleton API client via `@st.cache_resource`.
  - `fetch_available_models()`: Cached function (`@st.cache_data`) to retrieve the list of models for the selectbox.

### Pages
#### [NEW] [pages/1_💬_Chat.py](file:///home/federico/Dev/streamlit-agent-app-1/pages/1_💬_Chat.py)
- **Role**: Primary user interface.
- **Features**:
  - Displays chat history from `st.session_state.messages`.
  - Provides `st.chat_input` for user prompts.
  - Implements the streaming logic using `@st.fragment` to render `st.write_stream` cleanly.
  - Handles OpenRouter API errors gracefully.

#### [NEW] [pages/2_⚙️_Config.py](file:///home/federico/Dev/streamlit-agent-app-1/pages/2_⚙️_Config.py)
- **Role**: Administrative/Configuration panel.
- **Features**:
  - Allows selection of OpenRouter models (populating `st.session_state.active_model`).
  - Allows adjusting generation parameters (e.g., temperature).
  - Updates `st.query_params` to reflect configuration state for shareable URLs.

## Verification Plan

### Automated Tests
- Run `streamlit hello` or dummy app to verify the `.venv` and Streamlit installation.

### Manual Verification
1. **Authentication Flow**:
   - Start the app with `streamlit run streamlit_app.py`.
   - Verify that the user is forced to authenticate before accessing the chat.
2. **Chat Interface & Streaming**:
   - Navigate to the Chat page.
   - Enter a prompt and verify that the response streams smoothly without reloading the entire sidebar or other components (verifying `@st.fragment` behavior).
3. **Configuration & State**:
   - Navigate to the Config page.
   - Change the selected model and verify that the URL query parameters update.
   - Return to the Chat page and verify that the selected model is correctly used for the next API call.
