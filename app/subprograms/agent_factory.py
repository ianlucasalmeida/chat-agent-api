import logging
import requests
import re
import os
from app.config import settings
from app.subprograms.strands_tools import calculator_tool as strands_tool_decorator
from app.subprograms.math_tools import safe_calculator

logger = logging.getLogger("uvicorn.error")

class ManualAgent:
    def __init__(self, model, base_url):
        self.model = model
        self.base_url = base_url
        self.system_prompt = (
            "Você é um assistente inteligente. Você TEM uma calculadora.\n"
            "GUIA DE DECISÃO:\n"
            "1. PERGUNTAS GERAIS: Responda APENAS TEXTO.\n"
            "2. CÁLCULOS MATEMÁTICOS: Use a tag TOOL_CALCULATOR.\n"
            "   - FORMATO: TOOL_CALCULATOR: [expressão]\n"
            "   - Exemplo: 'Raiz de 144' -> TOOL_CALCULATOR: sqrt(144)\n"
        )

    def __call__(self, message: str):
        return self.run(message)

    def run(self, user_message: str):
        full_prompt = f"{self.system_prompt}\nUser: {user_message}\nAssistant:"
        
        try:
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            if response.status_code != 200:
                return "Erro de conexão com a IA."
            
            ai_response = response.json().get("response", "").strip()
            
            if "TOOL_CALCULATOR:" in ai_response:
                try:
                    parts = ai_response.split("TOOL_CALCULATOR:")
                    raw_expr = parts[1].strip()
                    
                    # --- CORREÇÃO 1: GUILHOTINA ---
                    separators = ["=", "is", "são", "igual", "->", "é"]
                    for sep in separators:
                        if sep in raw_expr:
                            raw_expr = raw_expr.split(sep)[0]

                    # --- NORMALIZAÇÃO DE SÍMBOLOS ---
                    replacements = {
                        "√": "sqrt",
                        "x": "*",    
                        "X": "*",    
                        "÷": "/",
                        ":": "/",    
                        "^": "**",   
                        "math.": ""  
                    }
                    for symbol, python_equivalent in replacements.items():
                        raw_expr = raw_expr.replace(symbol, python_equivalent)

                    # --- CORREÇÃO 3: CASO ESPECIAL DE RAIZ SEM PARÊNTESES ---
                    
                    if "sqrt" in raw_expr and "(" not in raw_expr:
                        raw_expr = raw_expr.replace("sqrt", "sqrt(") + ")"

                    # 3. LIMPEZA (Regex)
                    clean_expr = re.sub(r'[^\d\.\+\-\*\/\(\)sqrt]', '', raw_expr)
                    
                    # 4. VALIDAÇÃO DE OPERADOR
                    has_operator = any(op in clean_expr for op in ['+', '-', '*', '/', 'sqrt', '**'])
                    
                    if len(clean_expr) > 0 and has_operator:
                        logger.info(f"Expressão Normalizada: {clean_expr}")
                        result = safe_calculator(clean_expr)
                        return f"Resultado calculado: {result}"
                    else:
                        logger.warning(f"Falso positivo ou texto puro: '{clean_expr}'")
                        clean_text = ai_response.replace("TOOL_CALCULATOR:", "").strip()
                        return clean_text

                except IndexError:
                    return "Erro ao processar cálculo."
            
            return ai_response.replace(self.system_prompt, "")

        except Exception as e:
            return f"Erro interno: {e}"

def create_agent_instance():
    FORCE_MANUAL = True 
    if FORCE_MANUAL:
        return ManualAgent(settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)
    return ManualAgent(settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)