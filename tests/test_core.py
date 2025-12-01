from fastapi.testclient import TestClient
from app.main import app
from app.subprograms.math_tools import safe_calculator

# Cliente de teste do FastAPI (simula requisições sem subir o servidor)
client = TestClient(app)

# 1. TESTES UNITÁRIOS (Lógica Pura)
def test_calculator_basic_math():
    """Testa se a calculadora resolve contas simples."""
    assert safe_calculator("10 + 10") == "20"
    assert safe_calculator("5 * 5") == "25"
    assert safe_calculator("sqrt(144)") == "12.0"

def test_calculator_security():
    """Testa se a calculadora bloqueia injeções."""
    # Tenta importar bibliotecas
    assert "não é permitida" in safe_calculator("__import__('os')")
    # Tenta usar funções não listadas
    assert "não é permitida" in safe_calculator("eval('1+1')")

def test_calculator_math_bomb():
    """Testa se a calculadora bloqueia potências gigantes."""
    # Tenta uma exponenciação que travaria a CPU
    assert "bloqueada por segurança" in safe_calculator("99999999 ** 99999999")

# 2. TESTES DE INTEGRAÇÃO (API)
def test_api_health_structure():
    """Verifica se o endpoint responde e retorna JSON."""
    payload = {"message": "Teste de sanidade"}
    response = client.post("/api/v1/chat", json=payload)
    
    # Verifica se a API está de pé (200 OK)
    assert response.status_code == 200
    # Verifica se o JSON tem a chave 'response'
    assert "response" in response.json()

def test_api_empty_message():
    """Verifica se a API rejeita mensagens vazias."""
    # O Pydantic deve bloquear string vazia ou só espaços
    response = client.post("/api/v1/chat", json={"message": "   "})
    assert response.status_code == 422  # Unprocessable Entity