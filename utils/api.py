import streamlit as st
from openai import OpenAI
import httpx

@st.cache_resource
def get_openrouter_client():
    """
    Ritorna il client configurato per OpenRouter.
    """
    if "openrouter" not in st.secrets or "api_key" not in st.secrets["openrouter"]:
        st.error("Configurazione [openrouter] o api_key mancante nei secrets.")
        st.stop()
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["openrouter"]["api_key"],
        default_headers={
            "HTTP-Referer": "http://localhost:8501", # Your URL
            "X-Title": "AI Chat Hub Local"
        }
    )
    return client

@st.cache_data(ttl=3600)
def fetch_available_models():
    """
    Recupera la lista dei modelli da OpenRouter.
    """
    try:
        response = httpx.get("https://openrouter.ai/api/v1/models")
        response.raise_for_status()
        models_data = response.json().get("data", [])
        return [model["id"] for model in models_data]
    except Exception as e:
        st.warning(f"Impossibile caricare i modelli: {e}")
        return ["anthropic/claude-3-opus", "openai/gpt-4o", "meta-llama/llama-3-8b-instruct"]
