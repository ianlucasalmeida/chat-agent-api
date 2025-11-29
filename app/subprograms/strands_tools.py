from strands import tool
from app.subprograms.math_tools import safe_calculator

# O decorador @tool diz ao Agente: "Ei, você pode usar isso aqui!"
@tool
def calculator_tool(expression: str) -> str:
    """
    Useful for solving math problems.
    Input should be a mathematical expression string like "10 * 10" or "sqrt(144)".
    
    Args:
        expression (str): The math expression to evaluate.
        
    Returns:
        str: The calculated result.
    """
    # Reutiliza sua lógica segura existente
    return safe_calculator(expression)