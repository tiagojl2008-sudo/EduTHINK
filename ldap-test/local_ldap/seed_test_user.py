"""
Seed mock users into the local LDAP test server.
Run this after starting the Docker container.
"""
from ldap3 import Connection, Server


LDAP_URI = "ldap://127.0.0.1:1389"
ADMIN_DN = "cn=admin,dc=planetexpress,dc=com"
ADMIN_PASSWORD = "GoodNewsEveryone"
BASE_DN = "ou=people,dc=planetexpress,dc=com"

MOCK_USERS = [
    {"uid": "testuser",        "cn": "Test User",       "sn": "User",     "password": "test123",  "mail": "testuser@planetexpress.com"},
    {"uid": "maria.silva",     "cn": "Maria Silva",     "sn": "Silva",    "password": "maria123", "mail": "maria.silva@planetexpress.com"},
    {"uid": "joao.santos",     "cn": "Joao Santos",     "sn": "Santos",   "password": "joao123",  "mail": "joao.santos@planetexpress.com"},
    {"uid": "ana.costa",       "cn": "Ana Costa",       "sn": "Costa",    "password": "ana123",   "mail": "ana.costa@planetexpress.com"},
    {"uid": "pedro.oliveira",  "cn": "Pedro Oliveira",  "sn": "Oliveira", "password": "pedro123", "mail": "pedro.oliveira@planetexpress.com"},
    {"uid": "sofia.ferreira",  "cn": "Sofia Ferreira",  "sn": "Ferreira", "password": "sofia123", "mail": "sofia.ferreira@planetexpress.com"},
]


def main() -> None:
    server = Server(LDAP_URI)
    conn = Connection(server, user=ADMIN_DN, password=ADMIN_PASSWORD, auto_bind=True)

    created = 0
    skipped = 0

    for u in MOCK_USERS:
        uid = u["uid"]
        user_dn = f"uid={uid},{BASE_DN}"

        conn.search(search_base=BASE_DN, search_filter=f"(uid={uid})", attributes=["uid"])
        if conn.entries:
            print(f"  [skip] {uid} already exists")
            skipped += 1
            continue

        added = conn.add(
            dn=user_dn,
            object_class=["inetOrgPerson", "top"],
            attributes={
                "cn": u["cn"],
                "sn": u["sn"],
                "uid": uid,
                "userPassword": u["password"],
                "mail": u["mail"],
            },
        )
        if not added:
            print(f"  [ERRO] {uid}: {conn.result}")
        else:
            print(f"  [OK]   {uid} created (password: {u['password']})")
            created += 1

    conn.unbind()
    print(f"\nDone: {created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()
