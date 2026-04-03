from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.db.database import init_db
from app.api.routes import router

app = FastAPI(title="Personal Finance Analytics Pipeline", version="1.0.0")

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# API routes
app.include_router(router)

# Serve the Chart.js dashboard at "/"
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok"}
