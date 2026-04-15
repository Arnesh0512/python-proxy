from fastapi import APIRouter, WebSocket, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import asyncio
import json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates"))
)

clients = set()
log_buffer = set()
lock = asyncio.Lock()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    template = templates.get_template("index.html")
    return HTMLResponse(template.render(request=request))


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        clients.discard(ws)


@router.post("/log")
async def receive_log(payload: dict):
    msg = payload.get("msg")

    if isinstance(msg, dict):
        msg = json.dumps(msg)

    msg = str(msg)

    async with lock:
        log_buffer.add(msg)

    return {"ok": True}


async def flush_logs():
    while True:
        await asyncio.sleep(2)

        async with lock:
            if not log_buffer:
                continue

            batch = list(log_buffer)
            log_buffer.clear()

        for ws in list(clients):
            try:
                for log in batch:
                    await ws.send_text(log)
            except:
                clients.discard(ws)


@router.on_event("startup")
async def startup():
    asyncio.create_task(flush_logs())