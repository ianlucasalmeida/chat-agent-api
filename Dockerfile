FROM python:3.10-slim

# Evita arquivos temporários
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Instala curl para healthchecks se necessário
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY ./app ./app

# Segurança: Cria usuário não-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Inicia a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]