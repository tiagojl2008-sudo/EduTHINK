import os
from contextlib import asynccontextmanager

import bcrypt
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from . import models
from .database import get_db


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cria admin default se não existir
    from .database import SessionLocal
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.role == "admin").first()
        if not admin:
            hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            db.add(models.User(name="Admin", email="admin@salas.pt", password=hashed, role="admin"))
            db.commit()
    finally:
        db.close()
    yield


secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    import warnings
    warnings.warn(
        "SECRET_KEY não está definida! A usar chave temporária. "
        "Define a variável de ambiente SECRET_KEY em produção.",
        stacklevel=2,
    )
    secret_key = "dev-secret-key-change-in-prod"

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_middleware(SessionMiddleware, secret_key=secret_key)
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

# Montar ficheiros estáticos (imagens, CSS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "user": None, "detail": "Demasiadas tentativas. Tenta novamente mais tarde."},
        status_code=429,
    )

# include routers
from .routers import auth, public, dashboard, admin, inventory  # noqa: E402

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(inventory.router)


# Handler de erros HTTP
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    from .utils import get_current_user
    from .database import SessionLocal

    db = SessionLocal()
    user = get_current_user(request, db)
    db.close()

    if exc.status_code == 403:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "user": user, "detail": exc.detail},
            status_code=403
        )
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "user": user, "detail": str(exc.detail)},
        status_code=exc.status_code
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
