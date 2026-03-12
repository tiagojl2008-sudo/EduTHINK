import bcrypt
from app.database import SessionLocal
from app.models import User
db=SessionLocal()
admin=db.query(User).filter(User.email=="admin@salas.pt").first()

if admin:
    #Criar hash bycrypt pra password
    hashed=bcrypt.hashpw("admin123".encode(),bcrypt.gensalt()).decode()
    admin.password=hashed
    db.commit()
    print("Password do admin atualizada com bcrypt!!")
    print("Agora podes logar com: @adminsalas.pt/admin123")
else:
    print("Admin não foi encontrado!")
    db.close()