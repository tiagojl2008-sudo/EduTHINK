import logging
import os

from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from .. import models
from ..database import get_db
from ..utils import get_current_user, verify_password

limiter = Limiter(key_func=get_remote_address)

_cookie_secure = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
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
@limiter.limit("5/minute")
def login(request: Request, username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    logger.info(f"Tentativa de login: {username}")

    # Procurar utilizador por email OU username
    user = db.query(models.User).filter(
        (models.User.email == username) | (models.User.name == username)
    ).first()

    if user and user.password:
        logger.info(f"User encontrado na BD: {user.email}")

        # Verificar password com bcrypt
        if verify_password(password, user.password):
            logger.info(f"Login sucesso: {username}")
            resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
            resp.set_cookie("user_id", str(user.id), httponly=True, samesite="strict", secure=_cookie_secure, max_age=60*60*2)
            return resp

        logger.warning(f"Password incorreta para: {username}")

    # Tentar autenticação LDAP
    logger.info(f"Tentando LDAP para: {username}")
    if authenticator.authenticate(username=username, password=password):
        if not user:
            # Procurar se já existe user com este email LDAP
            ldap_email_domain = os.getenv("LDAP_EMAIL_DOMAIN", "planetexpress.com")
            ldap_email = f"{username}@{ldap_email_domain}"
            user = db.query(models.User).filter(
                (models.User.email == ldap_email) | (models.User.name == username)
            ).first()
            
            if not user:
                # Criar novo user
                user = models.User(name=username, email=ldap_email, password="", role="user")
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"User LDAP criado: {username}")
            else:
                logger.info(f"User LDAP existente: {user.name} (role: {user.role})")

        resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        resp.set_cookie("user_id", str(user.id), httponly=True, samesite="strict", secure=_cookie_secure, max_age=60*60*2)
        return resp

    # Erro de autenticação
    logger.error(f"Login falhou para: {username}")
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
