from datetime import datetime

def get_current_time(timezone: str = "UTC") -> str:
    """Retorna a data e hora atuais formatadas."""
    now = datetime.now()
    return now.strftime("%A, %d de %B de %Y, %H:%M:%S")