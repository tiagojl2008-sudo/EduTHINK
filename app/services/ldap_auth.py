import logging
import os
from typing import List

from ldap3 import ALL, Connection, Server

logger = logging.getLogger("ldap-auth")


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

        if any(sep in username for sep in ("@", "\\", "=")):
            candidates.append(username)

        if self.user_dn_template:
            candidates.append(self.user_dn_template.format(username=username))
        if self.user_domain:
            candidates.append(f"{username}@{self.user_domain}")
        if self.ntlm_domain:
            candidates.append(f"{self.ntlm_domain}\\{username}")
        candidates.append(username)

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

            conn_search = Connection(server, auto_bind=True)
            search_filter = f"(uid={username})"
            conn_search.search(self.base_dn, search_filter, attributes=['cn', 'uid'])

            if not conn_search.entries:
                if debug:
                    logger.warning("LDAP user not found: %s", username)
                conn_search.unbind()
                return False

            user_dn = conn_search.entries[0].entry_dn
            if debug:
                logger.info("LDAP user found DN: %s", user_dn)
            conn_search.unbind()

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
