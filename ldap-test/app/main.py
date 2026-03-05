import os
import logging
from typing import List, Optional

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ldap3 import ALL, Connection, Server
from starlette.middleware.sessions import SessionMiddleware

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

app = FastAPI(title="LDAP Auth Demo")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-me-in-production"),
    same_site="lax",
    https_only=False,
)

templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request) -> str:
    username: Optional[str] = request.session.get("username")
    if not username:
        raise PermissionError("User is not authenticated")
    return username


@app.get("/")
def home(request: Request):
    if request.session.get("username"):
        return RedirectResponse(url="/protected", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if authenticator.authenticate(username=username, password=password):
        request.session["username"] = username
        return RedirectResponse(url="/protected", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Invalid credentials or LDAP server unavailable.",
        },
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@app.get("/protected")
def protected(request: Request):
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "protected.html",
        {
            "request": request,
            "username": username,
        },
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
