cd local_ldap && docker compose up -d
cd .. && .venv/bin/python local_ldap/seed_test_user.py
cp local_ldap/.env.local-ldap.example .env.local-ldap
uvicorn app.main:app --reload --env-file .env.local-ldap
Login: testuser / test123