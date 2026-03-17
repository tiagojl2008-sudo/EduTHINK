"""
Script para testar login LDAP e verificar role do utilizador.
"""

from app.database import get_db
from app import models
from app.services.ldap_auth import LDAPAuthenticator

def test_ldap_login():
    db = next(get_db())
    authenticator = LDAPAuthenticator()
    
    # Testar autenticação LDAP
    print("🔐 Testar autenticação LDAP:\n")
    
    test_users = ["bender", "hermes", "fry", "professor"]
    
    for username in test_users:
        result = authenticator.authenticate(username, username)
        print(f"  {username}: {'✅' if result else '❌'}")
    
    print("\n📋 Utilizadores na BD:\n")
    
    users = db.query(models.User).all()
    for u in users:
        if u.email.endswith("planetexpress.com") or u.name in test_users:
            print(f"  • {u.name:25} | {u.email:30} | role: {u.role}")
    
    # Verificar Bender especificamente
    bender = db.query(models.User).filter(
        (models.User.name == "Bender B. Rodríguez") | (models.User.name == "bender")
    ).first()
    
    if bender:
        print(f"\n🤖 Bender encontrado:")
        print(f"   Nome: {bender.name}")
        print(f"   Email: {bender.email}")
        print(f"   Role: {bender.role}")
    
    db.close()

if __name__ == "__main__":
    test_ldap_login()
