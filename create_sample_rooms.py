"""
Script para adicionar salas de teste à base de dados.
Executa isto uma vez para popular a BD com salas de exemplo.
"""

from app.database import SessionLocal
from app import models

def create_sample_rooms():
    db = SessionLocal()
    try:
        # Verificar se já existem salas
        existing = db.query(models.Room).count()
        if existing > 0:
            print(f"Já existem {existing} salas na base de dados.")
            return
        
        # Criar salas de exemplo
        rooms = [
            models.Room(
                name="Sala A - Reuniões",
                capacity=10,
                location="Piso 1, Ala Norte",
                color="#0066cc",
                start_time="08:00",
                end_time="18:00",
                work_days="1,2,3,4,5"
            ),
            models.Room(
                name="Sala B - Formação",
                capacity=20,
                location="Piso 2, Ala Sul",
                color="#33aa66",
                start_time="09:00",
                end_time="17:00",
                work_days="1,2,3,4,5"
            ),
            models.Room(
                name="Auditório",
                capacity=50,
                location="Piso 0, Entrada",
                color="#e85d04",
                start_time="08:00",
                end_time="20:00",
                work_days="1,2,3,4,5"
            ),
        ]
        
        for room in rooms:
            db.add(room)
        
        db.commit()
        print("[OK] {} salas criadas com sucesso!".format(len(rooms)))
        
    except Exception as e:
        db.rollback()
        print("[ERRO] {}".format(e))
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_rooms()
