"""
Script para criar utilizadores na base de dados com diferentes roles.
Estes utilizadores vão autenticar via LDAP (Planet Express).

Utilizadores criados:
- fry / fry → role: user
- leela / leela → role: user  
- bender / bender → role: manager
- hermes / hermes → role: admin
"""

from app.database import get_db
from app import models
import hashlib

def create_ldap_users():
    db = next(get_db())
    
    # Lista de utilizadores a criar
    users_to_create = [
        {"username": "fry", "name": "Philip J. Fry", "role": "user"},
        {"username": "leela", "name": "Turanga Leela", "role": "user"},
        {"username": "bender", "name": "Bender B. Rodríguez", "role": "manager"},
        {"username": "hermes", "name": "Hermes Conrad", "role": "admin"},
        {"username": "amy", "name": "Amy Wong", "role": "user"},
        {"username": "professor", "name": "Hubert Farnsworth", "role": "manager"},
    ]
    
    print("📋 A criar utilizadores LDAP...\n")
    
    for user_data in users_to_create:
        email = f"{user_data['username']}@planetexpress.com"
        
        # Verificar se já existe
        existing = db.query(models.User).filter(models.User.email == email).first()
        
        if existing:
            print(f"⚠️  {user_data['name']} já existe (role: {existing.role})")
            continue
        
        # Criar utilizador (password vazia - usa LDAP)
        new_user = models.User(
            name=user_data['name'],
            email=email,
            password="",  # LDAP auth
            role=user_data['role']
        )
        
        db.add(new_user)
        db.commit()
        
        print(f"✅ {user_data['name']} criado (role: {user_data['role']})")
    
    print("\n🎉 Utilizadores criados com sucesso!")
    print("\n📝 Utilizadores disponíveis:")
    print("┌─────────────┬──────────────┬─────────────────────────┐")
    print("│ Username    │ Role         │ Email                   │")
    print("├─────────────┼──────────────┼─────────────────────────┤")
    print("│ fry         │ user         │ fry@planetexpress.com   │")
    print("│ leela       │ user         │ leela@planetexpress.com │")
    print("│ bender      │ manager      │ bender@planetexpress.com│")
    print("│ hermes      │ admin        │ hermes@planetexpress.com│")
    print("│ amy         │ user         │ amy@planetexpress.com   │")
    print("│ professor   │ manager      │ professor@planetexpress.│")
    print("└─────────────┴──────────────┴─────────────────────────┘")
    print("\n🔑 Password: mesma que o username (ex: fry/fry)")
    
    db.close()

if __name__ == "__main__":
    create_ldap_users()
