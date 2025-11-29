from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # Importe isso
from fastapi.responses import FileResponse  # Importe isso
from app.api.routes import router as chat_router

app = FastAPI(title="Chat Agent API", version="1.0.0")

# Monta a pasta de arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(chat_router, prefix="/api/v1")

# Rota raiz agora entrega o Chat Visual
@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")