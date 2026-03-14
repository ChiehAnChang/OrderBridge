from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import APP_NAME, APP_VERSION
from app.database import init_db
from app.routes import sessions, conversation, history, stt, ocr

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Serve generated images
OUTDIR = Path("outputs")
OUTDIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=OUTDIR), name="static")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Routers
app.include_router(sessions.router)
app.include_router(conversation.router)
app.include_router(history.router)
app.include_router(stt.router)
app.include_router(ocr.router)


@app.get("/")
def root():
    return {"message": f"{APP_NAME} API is running", "version": APP_VERSION}
