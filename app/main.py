from fastapi import FastAPI
from app.config import APP_NAME, APP_VERSION
from app.database import init_db
from app.routes import sessions, conversation, history, stt

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Routers
app.include_router(sessions.router)
app.include_router(conversation.router)
app.include_router(history.router)
app.include_router(stt.router)


@app.get("/")
def root():
    return {"message": f"{APP_NAME} API is running", "version": APP_VERSION}
