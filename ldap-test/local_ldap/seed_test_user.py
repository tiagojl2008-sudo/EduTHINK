from ldap3 import Connection, Server


LDAP_URI = "ldap://127.0.0.1:1389"
ADMIN_DN = "cn=admin,dc=planetexpress,dc=com"
ADMIN_PASSWORD = "GoodNewsEveryone"
USER_DN = "uid=testuser,ou=people,dc=planetexpress,dc=com"


def main() -> None:
    server = Server(LDAP_URI)
    conn = Connection(server, user=ADMIN_DN, password=ADMIN_PASSWORD, auto_bind=True)

    conn.search(
        search_base="ou=people,dc=planetexpress,dc=com",
        search_filter="(uid=testuser)",
        attributes=["uid"],
    )
    if conn.entries:
        print("testuser already exists.")
        conn.unbind()
        return

    added = conn.add(
        dn=USER_DN,
        object_class=["inetOrgPerson", "top"],
        attributes={
            "cn": "Test User",
            "sn": "User",
            "uid": "testuser",
            "userPassword": "test123",
        },
    )
    if not added:
        raise RuntimeError(f"Failed to add test user: {conn.result}")

    conn.unbind()
    print("testuser created with password test123.")


if __name__ == "__main__":
    main()
