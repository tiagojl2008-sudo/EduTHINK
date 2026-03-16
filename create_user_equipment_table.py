"""
Script para adicionar a tabela user_equipment à base de dados
"""

from app.database import engine
from app.models import Base, UserEquipment

print("=" * 50)
print("🔧 CRIAR TABELA user_equipment")
print("=" * 50)

try:
    # Criar apenas a tabela user_equipment
    UserEquipment.__table__.create(bind=engine)
    print("\n✅ Tabela user_equipment criada com sucesso!")
    print("\nAgora já podes atribuir equipamentos a utilizadores.")
except Exception as e:
    print(f"\n⚠️ Aviso: {e}")
    print("A tabela pode já existir.")

print("\n" + "=" * 50)
input("Pressiona Enter para sair...")
