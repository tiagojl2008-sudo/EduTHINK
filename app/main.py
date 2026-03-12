import hashlib
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from . import models
from .database import get_db

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod"))
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

# Montar ficheiros estáticos (imagens, CSS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# include routers
from .routers import auth, public, dashboard, admin, inventory, user_equipment # noqa: E402

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(inventory.router)
app.include_router(user_equipment.router)

# cria admin default se não existir
@app.on_event("startup")
async def create_default_admin():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        # Verificar se já existe admin pelo EMAIL (não por role)
        admin = db.query(models.User).filter(models.User.email == "admin@salas.pt").first()
        if not admin:
            hashed = hashlib.sha256("admin123".encode()).hexdigest()
            db.add(models.User(name="Admin", email="admin@salas.pt", password=hashed, role="admin"))
            db.commit()
            print("✅ Admin padrão criado: admin@salas.pt / admin123")
        else:
            print("ℹ️ Admin já existe na base de dados")
    except Exception as e:
        print(f"⚠️ Erro ao criar admin: {e}")
        db.rollback()
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


# Endpoint de debug para testar autenticação
@app.get("/debug/auth")
async def debug_auth(request: Request, db=Depends(get_db)):
    from .utils import get_current_user, require_admin
    user = get_current_user(request, db)
    is_admin = user.role == "admin" if user else False
    return {
        "logged_in": user is not None,
        "is_admin": is_admin,
        "user_id": request.cookies.get("user_id"),
        "user": {"name": user.name, "email": user.email, "role": user.role} if user else None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
