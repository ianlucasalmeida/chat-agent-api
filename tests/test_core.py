from fastapi.testclient import TestClient
from app.main import app
from app.subprograms.math_tools import safe_calculator

client = TestClient(app)

# 1. Teste Unitário: Valida a lógica matemática isolada
def test_calculator_logic():
    assert safe_calculator("10 + 10") == "20"
    assert safe_calculator("sqrt(144)") == "12.0"
    # Teste de segurança
    result_danger = safe_calculator("__import__('os')")
    assert "não é permitida" in result_danger

# 2. Teste de Integração: Valida a API (Health Check)
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Online", "service": "Chat Agent API"}

# 3. Teste de Fluxo: Garante que o endpoint /chat responde (Mockando a IA)
# Nota: Não testamos a resposta exata da IA aqui porque ela varia, 
# mas garantimos que a API não quebra.
def test_chat_endpoint_structure():
    payload = {"message": "Teste automatizado"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    assert "response" in response.json()