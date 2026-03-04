from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
import hashlib

from .. import models
from ..database import get_db
from ..utils import get_current_user

router = APIRouter()


@router.get("/login")
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db),
):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = db.query(models.User).filter(models.User.email == email, models.User.password == hashed_password).first()
    if not user:
        return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": "Email ou palavra-passe incorretos."})
    resp = RedirectResponse(url="/admin" if user.role == "admin" else "/dashboard", status_code=303)
    resp.set_cookie("user_id", str(user.id), httponly=True)
    return resp


@router.get("/register")
async def register_page(request: Request):
    return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db),
):
    # Verificar se email já existe
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return request.app.state.templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Este email já está registado."}
        )
    
    # Criar utilizador
    hashed = hashlib.sha256(password.encode()).hexdigest()
    new_user = models.User(name=name, email=email, password=hashed, role="user")
    db.add(new_user)
    db.commit()
    
    # Login automático
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie("user_id", str(new_user.id), httponly=True)
    return resp


@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("user_id")
    return resp
