# Local LDAP Test Module

This module runs an isolated OpenLDAP instance for local testing only.

## Start Local LDAP

```bash
cd local_ldap
docker compose up -d
docker compose ps
```

LDAP will be available at `ldap://127.0.0.1:1389`.

Create test user:

```bash
cd ..
.venv/bin/python local_ldap/seed_test_user.py
```

## Test User

- Username: `testuser`
- Password: `test123`
- DN: `uid=testuser,ou=people,dc=planetexpress,dc=com`

## Run the app against local LDAP

From project root:

```bash
cp local_ldap/.env.local-ldap.example .env.local-ldap
uvicorn app.main:app --reload --env-file .env.local-ldap
```

Then login in the app using `testuser` / `test123`.

## Stop Local LDAP

```bash
cd local_ldap
docker compose down
```
