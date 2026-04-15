from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates"))
)


@router.get("/blocked", response_class=HTMLResponse)
def blocked(request: Request):
    template = templates.get_template("blocked.html")
    return HTMLResponse(template.render(request=request))