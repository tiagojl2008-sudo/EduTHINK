"""
Script para limpar utilizadores duplicados e testar login LDAP.
"""

from app.database import get_db
from app import models

def clean_duplicate_users():
    db = next(get_db())
    
    # Eliminar utilizadores com nomes duplicados (manter apenas os do LDAP)
    users_to_delete = [
        ("admin", "user"),  # Manter Admintgg
        ("testuser", "user"),
        ("testuser", "admin"),
        ("professor", "user"),  # Manter Hubert Farnsworth
    ]
    
    print("🧹 A limpar utilizadores duplicados...\n")
    
    for name, role in users_to_delete:
        users = db.query(models.User).filter(
            models.User.name == name,
            models.User.role == role
        ).all()
        
        for user in users:
            # Não eliminar se for o único
            if db.query(models.User).filter(models.User.name == name).count() > 1:
                print(f"🗑️  A eliminar: {user.name} ({user.email}) - role: {user.role}")
                db.delete(user)
    
    db.commit()
    
    print("\n✅ Limpeza concluída!\n")
    
    # Listar todos os utilizadores
    print("📋 Utilizadores na BD:")
    print("=" * 60)
    users = db.query(models.User).all()
    for u in users:
        print(f"  • {u.name:25} | {u.email:30} | {u.role}")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    clean_duplicate_users()
