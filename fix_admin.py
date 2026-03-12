"""
Script para corrigir o Admin
- Atualiza password para SHA256
- Atualiza role para 'admin'
"""

import hashlib
from app.database import SessionLocal
from app.models import User

print("=" * 50)
print("🔧 CORRIGIR ADMIN")
print("=" * 50)

db = SessionLocal()

try:
    # Procurar o admin
    admin = db.query(User).filter(User.email == "admin@salas.pt").first()
    
    if admin:
        print(f"\n✅ Utilizador encontrado: {admin.name}")
        print(f"   Email: {admin.email}")
        print(f"   Role atual: {admin.role}")
        
        # Atualizar password para SHA256
        print("\n🔐 A atualizar password...")
        admin.password = hashlib.sha256("admin123".encode()).hexdigest()
        
        # Atualizar role para admin
        print("🔑 A atualizar role para admin...")
        admin.role = "admin"
        
        db.commit()
        
        print("\n✅ ADMIN CORRIGIDO COM SUCESSO!")
        print("\n📍 JÁ PODES FAZER LOGIN:")
        print("   Email: admin@salas.pt")
        print("   Password: admin123")
        print("   URL: http://127.0.0.1:8000/login")
    else:
        print("\n❌ Admin não encontrado!")
        print("   A criar admin novo...")
        
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        admin = User(
            name="Admin",
            email="admin@salas.pt",
            password=hashed,
            role="admin"
        )
        db.add(admin)
        db.commit()
        
        print("\n✅ ADMIN CRIADO COM SUCESSO!")
        print("\n📍 JÁ PODES FAZER LOGIN:")
        print("   Email: admin@salas.pt")
        print("   Password: admin123")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 50)
input("Pressiona Enter para sair...")
