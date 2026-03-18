import re

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date as date_type

from .. import models
from ..database import get_db
from ..utils import require_admin, times_overlap, time_in_range

router = APIRouter(prefix="/admin")


# ===================================================================
# ADMIN HOME
# ===================================================================

@router.get("")
async def home(request: Request, db=Depends(get_db)):
    """Página inicial do painel administrativo."""
    user = require_admin(request, db)
    rooms_list = db.query(models.Room).all()
    rooms = {r.id: r for r in rooms_list}
    today = str(date_type.today())
    today_res = db.query(models.Reservation).options(
        joinedload(models.Reservation.room),
        joinedload(models.Reservation.user),
    ).filter(models.Reservation.date == today).all()
    total_res = db.query(models.Reservation).count()

    return request.app.state.templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": user,
            "rooms": rooms,
            "today_reservations": today_res,
            "total_reservations": total_res,
            "today": today,
        },
    )


# ===================================================================
# SALAS
# ===================================================================

@router.get("/rooms")
async def rooms(request: Request, db=Depends(get_db)):
    """Listar todas as salas."""
    user = require_admin(request, db)
    rooms = db.query(models.Room).all()
    return request.app.state.templates.TemplateResponse(
        "admin_rooms.html",
        {"request": request, "user": user, "rooms": rooms, "error": None},
    )


@router.post("/rooms/create")
async def create_room(
    request: Request,
    name: str = Form(...),
    capacity: int = Form(...),
    location: str = Form(...),
    color: str = Form(default="#e85d04"),
    start_time: str = Form(...),
    end_time: str = Form(...),
    work_days: list = Form(default=[]),
    db=Depends(get_db),
):
    require_admin(request, db)

    errors = []
    if not work_days:
        errors.append("Selecione pelo menos um dia útil.")
    if start_time and end_time and start_time >= end_time:
        errors.append("Hora de início deve ser anterior à hora de fim.")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        errors.append("Cor inválida. Use o formato hexadecimal (ex: #e85d04).")

    if errors:
        rooms = db.query(models.Room).all()
        return request.app.state.templates.TemplateResponse(
            "admin_rooms.html",
            {"request": request, "user": require_admin(request, db), "rooms": rooms, "error": " | ".join(errors)},
        )

    room = models.Room(
        name=name,
        capacity=capacity,
        location=location,
        color=color,
        start_time=start_time,
        end_time=end_time,
        work_days=",".join(work_days),
    )
    db.add(room)
    db.commit()
    return RedirectResponse(url="/admin/rooms", status_code=303)


@router.post("/rooms/update/{room_id}")
async def update_room(
    request: Request,
    room_id: int,
    name: str = Form(...),
    capacity: int = Form(...),
    location: str = Form(...),
    color: str = Form(default="#e85d04"),
    start_time: str = Form(...),
    end_time: str = Form(...),
    work_days: list = Form(default=[]),
    db=Depends(get_db),
):
    require_admin(request, db)

    errors = []
    if not work_days:
        errors.append("Selecione pelo menos um dia útil.")
    if start_time and end_time and start_time >= end_time:
        errors.append("Hora de início deve ser anterior à hora de fim.")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        errors.append("Cor inválida. Use o formato hexadecimal (ex: #e85d04).")

    if errors:
        rooms = db.query(models.Room).all()
        return request.app.state.templates.TemplateResponse(
            "admin_rooms.html",
            {"request": request, "user": require_admin(request, db), "rooms": rooms, "error": " | ".join(errors)},
        )

    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404)

    room.name = name
    room.capacity = capacity
    room.location = location
    room.color = color
    room.start_time = start_time
    room.end_time = end_time
    room.work_days = ",".join(work_days)
    db.commit()
    return RedirectResponse(url="/admin/rooms", status_code=303)


@router.post("/rooms/delete/{room_id}")
async def delete_room(request: Request, room_id: int, db=Depends(get_db)):
    require_admin(request, db)
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        db.delete(room)
        db.commit()
    return RedirectResponse(url="/admin/rooms", status_code=303)


# ===================================================================
# UTILIZADORES
# ===================================================================

@router.get("/users")
async def users(request: Request, db=Depends(get_db)):
    user = require_admin(request, db)
    users = db.query(models.User).all()
    return request.app.state.templates.TemplateResponse(
        "admin_users.html",
        {"request": request, "user": user, "users": users, "error": None},
    )


@router.post("/users/create")
async def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(default="user"),
    db=Depends(get_db),
):
    require_admin(request, db)

    # Verificar se email já existe
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        users = db.query(models.User).all()
        return request.app.state.templates.TemplateResponse(
            "admin_users.html",
            {"request": request, "user": require_admin(request, db), "users": users, "error": "Este email já está registado."},
        )

    # Criar utilizador (password vazia, usa LDAP)
    new_user = models.User(
        name=name,
        email=email,
        password="",
        role=role
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/users/update/{user_id}")
async def update_user(
    request: Request,
    user_id: int,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(default="user"),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)

    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)

    # Verificar email duplicado
    if email != target.email:
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing and existing.id != user_id:
            users = db.query(models.User).all()
            return request.app.state.templates.TemplateResponse(
                "admin_users.html",
                {"request": request, "user": admin, "users": users, "error": "Este email já está em uso."},
            )

    target.name = name
    target.email = email
    target.role = role
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/users/delete/{user_id}")
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    target = db.query(models.User).filter(models.User.id == user_id).first()

    if target:
        # Não permitir eliminar a si próprio
        if target.id == admin.id:
            raise HTTPException(status_code=400, detail="Não podes eliminar-te a ti mesmo.")
        db.delete(target)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


# ===================================================================
# RESERVAS
# ===================================================================

@router.get("/reservations")
async def reservations(request: Request, db=Depends(get_db)):
    user = require_admin(request, db)
    reservations = db.query(models.Reservation).options(
        joinedload(models.Reservation.room),
        joinedload(models.Reservation.user),
    ).order_by(models.Reservation.date.desc(), models.Reservation.start_time).all()
    rooms_list = db.query(models.Room).all()
    rooms = {r.id: r for r in rooms_list}

    return request.app.state.templates.TemplateResponse(
        "admin_reservations.html",
        {"request": request, "user": user, "reservations": reservations, "rooms": rooms},
    )


@router.post("/reservations/update/{res_id}")
async def update_reservation(
    request: Request,
    res_id: int,
    title: str = Form(...),
    room_id: int = Form(...),
    date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    db=Depends(get_db),
):
    user = require_admin(request, db)
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404)

    errors = []

    if not title or len(title.strip()) == 0:
        errors.append("Título é obrigatório.")
    elif len(title) > 100:
        errors.append("Título muito longo (máx. 100 caracteres).")

    if start_time and end_time and start_time >= end_time:
        errors.append("Hora de início deve ser anterior à hora de fim.")

    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        errors.append("Sala não encontrada.")
    elif start_time and end_time and start_time < end_time:
        if not time_in_range(start_time, end_time, room.start_time, room.end_time):
            errors.append(f"Fora do horário útil ({room.start_time} – {room.end_time}).")

        existing = db.query(models.Reservation).filter(
            models.Reservation.room_id == room_id,
            models.Reservation.date == date,
            models.Reservation.id != res_id,
        ).all()
        for r in existing:
            if times_overlap(start_time, end_time, r.start_time, r.end_time):
                errors.append(f"Conflito com reserva existente: {r.title} ({r.start_time}–{r.end_time})")
                break

    if errors:
        reservations = db.query(models.Reservation).order_by(models.Reservation.date.desc(), models.Reservation.start_time).all()
        rooms_list = db.query(models.Room).all()
        rooms_map = {r.id: r for r in rooms_list}
        return request.app.state.templates.TemplateResponse(
            "admin_reservations.html",
            {"request": request, "user": user, "reservations": reservations, "rooms": rooms_map, "error": " | ".join(errors)},
        )

    res.title = title.strip()
    res.room_id = room_id
    res.date = date
    res.start_time = start_time
    res.end_time = end_time
    db.commit()
    return RedirectResponse(url="/admin/reservations", status_code=303)
