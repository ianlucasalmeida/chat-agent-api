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
        
        # PROMPT REFORÇADO (FEW-SHOT): Damos exemplos do que NÃO fazer
        self.system_prompt = (
            "Você é um assistente inteligente. Você TEM uma calculadora, mas deve usá-la COM CAUTELA.\n"
            "---------------------------------------------------\n"
            "GUIA DE DECISÃO:\n"
            "1. PERGUNTAS GERAIS (Definições, História, 'O que é...'):\n"
            "   - Responda APENAS TEXTO explicativo.\n"
            "   - JAMAIS use a tag TOOL_CALCULATOR.\n"
            "   - Exemplo: 'O que é uma matriz?' -> Resposta: 'Uma matriz é uma tabela organizada...'\n\n"
            "2. CÁLCULOS MATEMÁTICOS EXPLÍCITOS:\n"
            "   - Use a tag TOOL_CALCULATOR apenas se houver uma conta clara.\n"
            "   - FORMATO: TOOL_CALCULATOR: [expressão]\n"
            "   - NÃO coloque o resultado final. Deixe o Python calcular.\n"
            "   - Exemplo: 'Quanto é 8 vezes 8?' -> Resposta: 'TOOL_CALCULATOR: 8 * 8'\n"
            "---------------------------------------------------\n"
            "IMPORTANTE: Se a pergunta for ambígua, PREFIRA EXPLICAR COM TEXTO.\n"
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
                "options": {
                    "temperature": 0.0 # Zero criatividade para seguir regras
                }
            }
            
            logger.info(f"Enviando para Ollama...") 
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            
            if response.status_code != 200:
                return "Erro de conexão com a IA."
            
            ai_response = response.json().get("response", "").strip()
            
            # --- LÓGICA BLINDADA DE TOOL ---
            if "TOOL_CALCULATOR:" in ai_response:
                try:
                    parts = ai_response.split("TOOL_CALCULATOR:")
                    # Pega a parte da expressão
                    raw_expr = parts[1].strip()
                    
                    # 1. GUILHOTINA DE RESULTADO ALUCINADO
                    # Corta qualquer tentativa do LLM de responder depois de um igual ou texto
                    # Ex: "10 * 10 = 100" vira "10 * 10"
                    separators = ["=", "is", "são", "igual", "->"]
                    for sep in separators:
                        if sep in raw_expr:
                            raw_expr = raw_expr.split(sep)[0]

                    # 2. LIMPEZA (Regex)
                    clean_expr = re.sub(r'[^\d\.\+\-\*\/\(\)sqrt]', '', raw_expr)
                    
                    # 3. VALIDAÇÃO DE OPERADOR (A GRANDE CORREÇÃO)
                    # Para ser uma conta, precisa ter números E pelo menos um operador/função.
                    # Isso impede que "Capítulo 1" vire cálculo "1".
                    has_operator = any(op in clean_expr for op in ['+', '-', '*', '/', 'sqrt'])
                    
                    if len(clean_expr) > 0 and has_operator:
                        logger.info(f"🧮 Expressão Válida Identificada: {clean_expr}")
                        result = safe_calculator(clean_expr)
                        return f"🧮 Resultado calculado: {result}"
                    else:
                        # Se caiu aqui, é porque o LLM alucinou a tool para um texto sem conta.
                        # Retornamos o texto original da resposta (removendo a tag suja)
                        # Ex: "TOOL_CALCULATOR: Matriz é..." -> Retorna "Matriz é..."
                        logger.warning(f"⚠️ Falso positivo de Tool ignorado: '{clean_expr}'")
                        clean_text_response = ai_response.replace("TOOL_CALCULATOR:", "").strip()
                        # Se sobrou texto útil, retorna ele. Senão, pede desculpas.
                        return clean_text_response if len(clean_text_response) > 5 else "Poderia reformular sua pergunta?"

                except IndexError:
                    return "Erro ao processar cálculo."
            
            # Se não tem tag, é texto puro
            return ai_response.replace(self.system_prompt, "")

        except Exception as e:
            return f"Erro interno: {e}"

def create_agent_instance():
    FORCE_MANUAL = True 
    if FORCE_MANUAL:
        return ManualAgent(settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)
    return ManualAgent(settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)