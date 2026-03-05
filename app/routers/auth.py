from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
import hashlib

from .. import models
from ..database import get_db
from ..utils import get_current_user
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ldap3 import ALL, Connection, Server
from starlette.middleware.sessions import SessionMiddleware
import logging
import os
from typing import List


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



class LDAPAuthenticator:
    def __init__(self) -> None:
        self.server_uri = os.getenv("LDAP_SERVER_URI", "ldap://localhost:389")
        self.base_dn = os.getenv("LDAP_BASE_DN", "")
        self.user_dn_template = os.getenv("LDAP_USER_DN_TEMPLATE", "")
        self.user_domain = os.getenv("LDAP_USER_DOMAIN", "")
        self.ntlm_domain = os.getenv("LDAP_NTLM_DOMAIN", "")
    @staticmethod
    def _debug_enabled() -> bool:
        return os.getenv("LDAP_DEBUG", "false").lower() in ("1", "true", "yes", "on")

    def _build_bind_candidates(self, username: str) -> List[str]:
        candidates: List[str] = []

        # If user already typed a complete principal (DN/UPN/DOMAIN\user), try it first.
        if any(sep in username for sep in ("@", "\\", "=")):
            candidates.append(username)

        if self.user_dn_template:
            candidates.append(self.user_dn_template.format(username=username))
        if self.user_domain:
            candidates.append(f"{username}@{self.user_domain}")
        if self.ntlm_domain:
            candidates.append(f"{self.ntlm_domain}\\{username}")
        candidates.append(username)

        # Keep order but remove duplicates.
        return list(dict.fromkeys(candidates))

    def authenticate(self, username: str, password: str) -> bool:
        debug = self._debug_enabled()
        if not username or not password:
            if debug:
                logger.warning("LDAP auth blocked: empty username or password.")
            return False

        try:
            server = Server(self.server_uri, get_info=ALL)
            if debug:
                logger.info("LDAP server configured: %s", self.server_uri)
            for bind_user in self._build_bind_candidates(username):
                try:
                    if debug:
                        logger.info("LDAP bind attempt with user format: %s", bind_user)
                    conn = Connection(
                        server,
                        user=bind_user,
                        password=password,
                        auto_bind=True,
                        raise_exceptions=True,
                    )
                    conn.unbind()
                    if debug:
                        logger.info("LDAP bind success for: %s", bind_user)
                    return True
                except Exception as exc:
                    if debug:
                        logger.warning(
                            "LDAP bind failed for %s: %s: %s",
                            bind_user,
                            type(exc).__name__,
                            exc,
                        )
                    continue
            if debug:
                logger.error("LDAP auth failed for username: %s", username)
            return False
        except Exception as exc:
            if debug:
                logger.exception("LDAP server/connect error: %s: %s", type(exc).__name__, exc)
            return False


authenticator = LDAPAuthenticator()
router = APIRouter()


@router.get("/login")
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db = Depends(get_db)):
    if authenticator.authenticate(username=username, password=password):
        # Buscar user na BD pelo username (email)
        user = db.query(models.User).filter(models.User.email == username).first()
        if not user:
            # User não existe na BD - criar automaticamente
            user = models.User(name=username, email=username, password="", role="user")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Guardar user_id em cookie (não guardar password)
        resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        resp.set_cookie("user_id", str(user.id), httponly=True, max_age=60*60*24*7)
        return resp

    # Erro de autenticação
    return request.app.state.templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Invalid credentials or LDAP server unavailable.",
        },
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@router.get("/register")
async def register_page(request: Request):
    # Redirecionar para login (registo desativado)
    return RedirectResponse(url="/login", status_code=303)


@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("user_id")
    return resp
