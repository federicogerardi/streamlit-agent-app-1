"""
Script di test per validare la persistenza della sessione.
Eseguire con: python test_persistence.py
"""

import json
from pathlib import Path
from utils.session_persistence import (
    load_session,
    save_session,
    save_session_messages,
    save_session_config,
    clear_session,
    get_session_file,
    cleanup_old_sessions
)

# Email di test
TEST_EMAIL = "test@example.com"

def test_session_file_path():
    """Test 1: Verifica che il percorso del file sessione sia corretto."""
    print("\n🧪 Test 1: Percorso file sessione")
    session_file = get_session_file(TEST_EMAIL)
    print(f"   ✅ Percorso: {session_file}")
    assert "test_at_example_dot_com_session.json" in str(session_file)
    print("   ✅ PASS")

def test_load_nonexistent_session():
    """Test 2: Caricamento sessione inesistente ritorna valori predefiniti."""
    print("\n🧪 Test 2: Caricamento sessione inesistente")
    
    # Pulisci prima
    clear_session(TEST_EMAIL)
    
    session = load_session(TEST_EMAIL)
    print(f"   ✅ Sessione caricata: {session}")
    
    assert session["messages"] == []
    assert session["active_model"] == "openai/gpt-3.5-turbo"
    assert session["temperature"] == 0.7
    assert "last_updated" in session
    print("   ✅ PASS")

def test_save_and_load_session():
    """Test 3: Salvataggio e caricamento sessione completa."""
    print("\n🧪 Test 3: Salvataggio e caricamento sessione")
    
    # Crea sessione di test
    test_session = {
        "messages": [
            {"role": "user", "content": "Ciao"},
            {"role": "assistant", "content": "Ciao! Come stai?"}
        ],
        "active_model": "anthropic/claude-3-opus",
        "temperature": 0.5
    }
    
    # Salva
    result = save_session(TEST_EMAIL, test_session)
    print(f"   ✅ Salvataggio: {result}")
    assert result == True
    
    # Carica
    loaded = load_session(TEST_EMAIL)
    print(f"   ✅ Caricamento: {loaded}")
    
    assert loaded["messages"] == test_session["messages"]
    assert loaded["active_model"] == test_session["active_model"]
    assert loaded["temperature"] == test_session["temperature"]
    print("   ✅ PASS")

def test_save_messages_only():
    """Test 4: Salvataggio solo messaggi."""
    print("\n�912 Test 4: Salvataggio solo messaggi")
    
    # Salva configurazione iniziale
    save_session_config(TEST_EMAIL, "openai/gpt-4o", 0.8)
    
    # Salva messaggi
    messages = [
        {"role": "user", "content": "Test 1"},
        {"role": "assistant", "content": "Risposta 1"}
    ]
    result = save_session_messages(TEST_EMAIL, messages)
    print(f"   ✅ Salvataggio messaggi: {result}")
    assert result == True
    
    # Verifica che configurazione sia preservata
    loaded = load_session(TEST_EMAIL)
    assert loaded["messages"] == messages
    assert loaded["active_model"] == "openai/gpt-4o"
    assert loaded["temperature"] == 0.8
    print("   ✅ PASS")

def test_save_config_only():
    """Test 5: Salvataggio solo configurazione."""
    print("\n🧪 Test 5: Salvataggio solo configurazione")
    
    # Salva messaggi iniziali
    messages = [{"role": "user", "content": "Messaggio"}]
    save_session_messages(TEST_EMAIL, messages)
    
    # Salva configurazione
    result = save_session_config(TEST_EMAIL, "meta-llama/llama-3-8b", 1.2)
    print(f"   ✅ Salvataggio configurazione: {result}")
    assert result == True
    
    # Verifica che messaggi siano preservati
    loaded = load_session(TEST_EMAIL)
    assert loaded["messages"] == messages
    assert loaded["active_model"] == "meta-llama/llama-3-8b"
    assert loaded["temperature"] == 1.2
    print("   ✅ PASS")

def test_clear_session():
    """Test 6: Cancellazione sessione."""
    print("\n🧪 Test 6: Cancellazione sessione")
    
    # Salva una sessione
    save_session(TEST_EMAIL, {
        "messages": [{"role": "user", "content": "Test"}],
        "active_model": "openai/gpt-3.5-turbo",
        "temperature": 0.7
    })
    
    # Verifica che esista
    session_file = get_session_file(TEST_EMAIL)
    assert session_file.exists()
    print(f"   ✅ Sessione esiste: {session_file}")
    
    # Cancella
    result = clear_session(TEST_EMAIL)
    print(f"   ✅ Cancellazione: {result}")
    assert result == True
    
    # Verifica che non esista più
    assert not session_file.exists()
    print("   ✅ PASS")

def test_file_format():
    """Test 7: Verifica formato JSON file."""
    print("\n🧪 Test 7: Verifica formato JSON file")
    
    # Salva sessione
    test_session = {
        "messages": [{"role": "user", "content": "Test"}],
        "active_model": "openai/gpt-3.5-turbo",
        "temperature": 0.7
    }
    save_session(TEST_EMAIL, test_session)
    
    # Leggi file direttamente
    session_file = get_session_file(TEST_EMAIL)
    with open(session_file, "r") as f:
        file_content = json.load(f)
    
    print(f"   ✅ Contenuto file: {file_content}")
    
    # Verifica struttura
    assert "messages" in file_content
    assert "active_model" in file_content
    assert "temperature" in file_content
    assert "last_updated" in file_content
    print("   ✅ PASS")

def test_multiple_users():
    """Test 8: Sessioni separate per utenti diversi."""
    print("\n🧪 Test 8: Sessioni separate per utenti")
    
    user1 = "user1@example.com"
    user2 = "user2@example.com"
    
    # Salva sessioni diverse
    save_session(user1, {
        "messages": [{"role": "user", "content": "User 1"}],
        "active_model": "openai/gpt-3.5-turbo",
        "temperature": 0.5
    })
    
    save_session(user2, {
        "messages": [{"role": "user", "content": "User 2"}],
        "active_model": "anthropic/claude-3-opus",
        "temperature": 0.8
    })
    
    # Carica e verifica isolamento
    session1 = load_session(user1)
    session2 = load_session(user2)
    
    assert session1["messages"][0]["content"] == "User 1"
    assert session2["messages"][0]["content"] == "User 2"
    assert session1["active_model"] != session2["active_model"]
    print("   ✅ PASS")
    
    # Cleanup
    clear_session(user1)
    clear_session(user2)

def run_all_tests():
    """Esegui tutti i test."""
    print("=" * 60)
    print("🧪 TEST SUITE - PERSISTENZA SESSIONE")
    print("=" * 60)
    
    try:
        test_session_file_path()
        test_load_nonexistent_session()
        test_save_and_load_session()
        test_save_messages_only()
        test_save_config_only()
        test_clear_session()
        test_file_format()
        test_multiple_users()
        
        print("\n" + "=" * 60)
        print("✅ TUTTI I TEST PASSATI!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLITO: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRORE INASPETTATO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
