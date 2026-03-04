import hashlib
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine

# helper utilities have been moved to app/utils.py

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

# Montar ficheiros estáticos (imagens, CSS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# include routers
from .routers import auth, public, dashboard, admin, equipment # noqa: E402

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(equipment.router)

# cria admin default se não existir
@app.on_event("startup")
async def create_default_admin():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.role == "admin").first()
        if not admin:
            hashed = hashlib.sha256("admin123".encode()).hexdigest()
            db.add(models.User(name="Admin", email="admin@salas.pt", password=hashed, role="admin"))
            db.commit()
    finally:
        db.close()


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
