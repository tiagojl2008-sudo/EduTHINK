from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from datetime import datetime, date as date_type
import hashlib
import os

from .. import models
from ..database import get_db
from ..utils import require_login, times_overlap, time_in_range, get_current_user

router = APIRouter()


# ===================================================================
# DASHBOARD
# ===================================================================

@router.get("/dashboard")
async def dashboard(request: Request, db=Depends(get_db)):
    user = require_login(request, db)
    rooms = db.query(models.Room).all()
    today = str(date_type.today())
    all_res = db.query(models.Reservation).filter(models.Reservation.date == today).all()
    my_res = db.query(models.Reservation).filter(
        models.Reservation.user_id == user.id
    ).order_by(models.Reservation.date, models.Reservation.start_time).all()
    
    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "rooms": rooms,
            "today": today,
            "all_reservations": all_res,
            "my_reservations": my_res,
            "error": None,
        },
    )


# ===================================================================
# CRIAR RESERVA
# ===================================================================

@router.post("/reservations/create")
async def create_reservation(
    request: Request,
    room_id: int = Form(...),
    date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    title: str = Form(...),
    db=Depends(get_db),
):
    user = require_login(request, db)
    room = db.query(models.Room).filter(models.Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

    # Verificar dia da semana
    python_dow = datetime.strptime(date, "%Y-%m-%d").weekday()
    dow = (python_dow + 1) % 7
    work_days = [int(d) for d in room.work_days.split(",")]

    errors = []

    # Validação: A data não pode ser no passado
    today = date_type.today()
    reservation_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    if reservation_date < today:
        errors.append("Não é possível reservar datas passadas.")
    
    # Validação: Se for hoje, hora deve ser >= hora atual
    if reservation_date == today:
        from datetime import datetime as dt
        current_time = dt.now().strftime("%H:%M")
        if start_time < current_time:
            errors.append("Não é possível reservar horas passadas de hoje.")

    if dow not in work_days:
        errors.append("A sala está encerrada nesse dia da semana.")

    if start_time >= end_time:
        errors.append("A hora de início deve ser anterior à hora de fim.")

    if not time_in_range(start_time, end_time, room.start_time, room.end_time):
        errors.append(f"Fora do horário útil ({room.start_time} – {room.end_time}).")

    # Verificar conflitos com TODAS as reservas (incluindo as do próprio utilizador)
    existing = db.query(models.Reservation).filter(
        models.Reservation.room_id == room_id,
        models.Reservation.date == date
    ).all()

    for r in existing:
        # Ignorar a própria reserva se estiver a editar (não é o caso aqui)
        if times_overlap(start_time, end_time, r.start_time, r.end_time):
            errors.append(f"Conflito com reserva existente: {r.title} ({r.start_time}–{r.end_time})")
            break

    if errors:
        rooms = db.query(models.Room).all()
        today_str = str(date_type.today())
        all_res = db.query(models.Reservation).filter(models.Reservation.date == today_str).all()
        my_res = db.query(models.Reservation).filter(models.Reservation.user_id == user.id).all()

        return request.app.state.templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "rooms": rooms,
                "today": today_str,
                "all_reservations": all_res,
                "my_reservations": my_res,
                "error": " | ".join(errors),
            },
        )
    
    # Criar reserva
    reservation = models.Reservation(
        title=title,
        date=date,
        start_time=start_time,
        end_time=end_time,
        room_id=room_id,
        user_id=user.id,
    )
    db.add(reservation)
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=303)


# ===================================================================
# ELIMINAR RESERVA
# ===================================================================

@router.post("/reservations/delete/{res_id}")
async def delete_reservation(request: Request, res_id: int, db=Depends(get_db)):
    user = require_login(request, db)
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    if res.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Não tens permissão")
    
    db.delete(res)
    db.commit()
    
    redirect = "/admin/reservations" if user.role == "admin" else "/dashboard"
    return RedirectResponse(url=redirect, status_code=303)


# ===================================================================
# ÁREA DO UTILIZADOR
# ===================================================================

@router.get("/user")
async def user_page(request: Request, db=Depends(get_db)):
    user = require_login(request, db)
    
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Admin não tem acesso a esta área.")
    
    my_res = db.query(models.Reservation).filter(models.Reservation.user_id == user.id).all()
    rooms = db.query(models.Room).all()
    
    return request.app.state.templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user": user,
            "my_reservations": my_res,
            "rooms": rooms,
            "success": None,
        },
    )


# ===================================================================
# ATUALIZAR PERFIL
# ===================================================================

@router.post("/user/update")
async def update_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(default=""),
    avatar: UploadFile = File(None),
    db=Depends(get_db),
):
    user = require_login(request, db)
    
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Admin não tem acesso a esta área.")
    
    # Processar avatar
    if avatar and avatar.filename:
        allowed_ext = [".jpg", ".jpeg", ".png", ".gif"]
        file_ext = avatar.filename[avatar.filename.rfind("."):]
        
        if file_ext.lower() not in allowed_ext:
            my_res = db.query(models.Reservation).filter(models.Reservation.user_id == user.id).all()
            rooms = db.query(models.Room).all()
            return request.app.state.templates.TemplateResponse(
                "user.html",
                {
                    "request": request,
                    "user": user,
                    "my_reservations": my_res,
                    "rooms": rooms,
                    "error": "Formato não permitido. Usa JPG, PNG ou GIF.",
                },
            )
        
        content = await avatar.read()
        if len(content) > 2 * 1024 * 1024:
            my_res = db.query(models.Reservation).filter(models.Reservation.user_id == user.id).all()
            rooms = db.query(models.Room).all()
            return request.app.state.templates.TemplateResponse(
                "user.html",
                {
                    "request": request,
                    "user": user,
                    "my_reservations": my_res,
                    "rooms": rooms,
                    "error": "Ficheiro muito grande. Máximo 2MB.",
                },
            )
        
        os.makedirs("app/static/avatars", exist_ok=True)
        new_filename = f"user_{user.id}{file_ext}"
        file_path = f"app/static/avatars/{new_filename}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        user.avatar = f"/static/avatars/{new_filename}"
    
    # Verificar email duplicado
    if email != user.email:
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            my_res = db.query(models.Reservation).filter(models.Reservation.user_id == user.id).all()
            rooms = db.query(models.Room).all()
            return request.app.state.templates.TemplateResponse(
                "user.html",
                {
                    "request": request,
                    "user": user,
                    "my_reservations": my_res,
                    "rooms": rooms,
                    "error": "Este email já está em uso.",
                },
            )
    
    # Atualizar dados
    user.name = name
    user.email = email
    if password:
        user.password = hashlib.sha256(password.encode()).hexdigest()
    
    db.commit()
    
    my_res = db.query(models.Reservation).filter(models.Reservation.user_id == user.id).all()
    rooms = db.query(models.Room).all()
    
    return request.app.state.templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user": user,
            "my_reservations": my_res,
            "rooms": rooms,
            "success": "Perfil atualizado com sucesso!",
        },
    )

