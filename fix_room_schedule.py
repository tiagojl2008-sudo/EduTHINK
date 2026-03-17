"""
Script para ajustar o horário de todas as salas para 08:00-20:00
e definir dias úteis de segunda a sexta.
"""

from app.database import get_db
from app import models

def fix_room_schedule():
    db = next(get_db())
    
    try:
        rooms = db.query(models.Room).all()
        
        if not rooms:
            print("❌ Nenhuma sala encontrada!")
            return
        
        print(f"📋 Encontradas {len(rooms)} sala(s)\n")
        
        for room in rooms:
            old_start = room.start_time
            old_end = room.end_time
            old_days = room.work_days
            
            # Atualizar horário para 08:00-20:00
            room.start_time = "08:00"
            room.end_time = "20:00"
            
            # Definir dias úteis: Segunda a Sexta (1,2,3,4,5)
            room.work_days = "1,2,3,4,5"
            
            db.commit()
            
            print(f"✅ Sala: {room.name}")
            print(f"   Horário: {old_start}-{old_end} → 08:00-20:00")
            print(f"   Dias: {old_days} → 1,2,3,4,5 (Seg-Sex)\n")
        
        print("🎉 Todas as salas foram atualizadas!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_room_schedule()
