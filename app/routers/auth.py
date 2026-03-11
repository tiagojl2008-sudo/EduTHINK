import logging
import os

import bcrypt
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse

from .. import models
from ..database import get_db
from ..utils import get_current_user
from ..services.ldap_auth import LDAPAuthenticator

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("ldap-auth")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


authenticator = LDAPAuthenticator()
router = APIRouter()


@router.get("/login")
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    # Rate limiting via slowapi
    limiter = request.app.state.limiter
    limiter.check("5/minute", request)

    # Tentar autenticação local primeiro (para admin e users na BD)
    user = db.query(models.User).filter(models.User.email == username).first()

    if user and user.password:
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
            resp.set_cookie("user_id", str(user.id), httponly=True, samesite="lax", max_age=60*60*24*7)
            return resp

    # Tentar autenticação LDAP
    if authenticator.authenticate(username=username, password=password):
        if not user:
            user = models.User(name=username, email=username, password="", role="user")
            db.add(user)
            db.commit()
            db.refresh(user)

        resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        resp.set_cookie("user_id", str(user.id), httponly=True, samesite="lax", max_age=60*60*24*7)
        return resp

    # Erro de autenticação
    return request.app.state.templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Credenciais inválidas ou servidor LDAP indisponível.",
        },
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@router.get("/register")
async def register_page(request: Request):
    return RedirectResponse(url="/login", status_code=303)


@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("user_id")
    return resp
