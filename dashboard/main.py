from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routes import dashboard, blocked, settings

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# include routers
app.include_router(dashboard.router)
app.include_router(blocked.router)
app.include_router(settings.router)