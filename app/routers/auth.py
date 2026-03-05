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
        self.server_uri = os.getenv("LDAP_SERVER_URI", "ldap://127.0.0.1:1389")
        self.base_dn = os.getenv("LDAP_BASE_DN", "ou=people,dc=planetexpress,dc=com")
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
            
            # Primeiro, pesquisar o DN do utilizador
            conn_search = Connection(server, auto_bind=True)
            search_filter = f"(uid={username})"
            conn_search.search(self.base_dn, search_filter, attributes=['cn', 'uid'])
            
            if not conn_search.entries:
                if debug:
                    logger.warning("LDAP user not found: %s", username)
                conn_search.unbind()
                return False
            
            # Obter o DN do primeiro resultado
            user_dn = conn_search.entries[0].entry_dn
            if debug:
                logger.info("LDAP user found DN: %s", user_dn)
            conn_search.unbind()
            
            # Tentar autenticar com o DN encontrado
            try:
                conn = Connection(
                    server,
                    user=str(user_dn),
                    password=password,
                    auto_bind=True,
                    raise_exceptions=True,
                )
                conn.unbind()
                if debug:
                    logger.info("LDAP bind success for: %s", username)
                return True
            except Exception as exc:
                if debug:
                    logger.warning(
                        "LDAP bind failed for %s: %s: %s",
                        username,
                        type(exc).__name__,
                        exc,
                    )
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
    import hashlib
    
    # Tentar autenticação local primeiro (para admin e users na BD)
    user = db.query(models.User).filter(models.User.email == username).first()
    
    if user and user.password:
        # User existe na BD com password - autenticação local
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if hashed == user.password or password == user.password:
            # Login local bem sucedido
            resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
            resp.set_cookie("user_id", str(user.id), httponly=True, max_age=60*60*24*7)
            return resp
    
    # Tentar autenticação LDAP
    if authenticator.authenticate(username=username, password=password):
        # User não existe na BD - criar automaticamente
        if not user:
            user = models.User(name=username, email=username, password="", role="user")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Login LDAP bem sucedido
        resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        resp.set_cookie("user_id", str(user.id), httponly=True, max_age=60*60*24*7)
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
    # Redirecionar para login (registo desativado)
    return RedirectResponse(url="/login", status_code=303)


@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("user_id")
    return resp
