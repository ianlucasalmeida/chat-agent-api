import math
import logging

# Configura um logger específico para segurança
logger = logging.getLogger("security.math")

def safe_calculator(expression: str) -> str:
    """
    Executa cálculos matemáticos com restrições severas de segurança.
    Bloqueia: Funções perigosas, loops infinitos e 'Math Bombs'.
    """
    try:
        # 1. BLINDAGEM DE TAMANHO DA EXPRESSÃO
        # Ninguém precisa de mais de 50 caracteres para uma conta de chat.
        # Isso impede tentativas de ofuscação de código longo.
        if len(expression) > 50:
            logger.warning(f"Tentativa de ataque de Buffer: {len(expression)} chars")
            return "Erro: Expressão muito longa para cálculo."

        # 2. BLINDAGEM CONTRA 'MATH BOMBS' (Exponenciação Gigante)
        # Impede coisas como 999**999 que travam a CPU.
        if "**" in expression:
            # Permite potências pequenas, mas bloqueia abusos
            # Se a string for longa e tiver potência, é suspeito.
            if len(expression) > 10: 
                return "Erro: Potência muito complexa bloqueada por segurança."
        
        # 3. WHITELIST DE FUNÇÕES (O que é permitido)
        allowed_names = {
            "sqrt": math.sqrt, "pow": math.pow, "abs": abs,
            "round": round, "min": min, "max": max,
            "pi": math.pi, "e": math.e
        }
        
        # 4. COMPILAÇÃO SEGURA
        # Transforma string em bytecode para análise estática antes de rodar
        code = compile(expression, "<string>", "eval")
        
        # Verifica cada nome/função chamado na expressão
        for name in code.co_names:
            if name not in allowed_names:
                logger.warning(f"Tentativa de Injeção bloqueada: '{name}'")
                return f"Erro: A função '{name}' não é permitida. Tentativa registrada."
        
        # 5. EXECUÇÃO ISOLADA
        # __builtins__={} remove acesso a funções do sistema como print, open, import
        result = eval(code, {"__builtins__": {}}, allowed_names)
        
        # Limita o tamanho da resposta (para não retornar 1 milhão de dígitos)
        str_result = str(result)
        if len(str_result) > 50:
            return f"{str_result[:50]}... (truncado)"
            
        return str_result
        
    except SyntaxError:
        return "Erro: Expressão matemática inválida."
    except ZeroDivisionError:
        return "Erro: Divisão por zero não é permitida."
    except Exception as e:
        logger.error(f"Erro de Execução: {str(e)}")
        return "Erro ao calcular."