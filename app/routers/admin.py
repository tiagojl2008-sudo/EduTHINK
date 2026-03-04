from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from datetime import date as date_type

from .. import models
from ..database import get_db
from ..utils import require_admin

router = APIRouter(prefix="/admin")


@router.get("")
async def home(request: Request, db=Depends(get_db)):
    """Página inicial do painel administrativo."""
    user = require_admin(request, db)
    rooms_list = db.query(models.Room).all()
    rooms = {r.id: r for r in rooms_list}
    today = str(date_type.today())
    today_res = db.query(models.Reservation).filter(models.Reservation.date == today).all()
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


# === CRUD de salas ===

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
    
    # Validar dias úteis
    if not work_days:
        rooms = db.query(models.Room).all()
        return request.app.state.templates.TemplateResponse(
            "admin_rooms.html",
            {"request": request, "user": require_admin(request, db), "rooms": rooms, "error": "Selecione pelo menos um dia útil."},
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
    
    # Validar dias úteis
    if not work_days:
        rooms = db.query(models.Room).all()
        return request.app.state.templates.TemplateResponse(
            "admin_rooms.html",
            {"request": request, "user": require_admin(request, db), "rooms": rooms, "error": "Selecione pelo menos um dia útil."},
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


# === Ver reservas ===

@router.get("/reservations")
async def reservations(request: Request, db=Depends(get_db)):
    user = require_admin(request, db)
    reservations = db.query(models.Reservation).order_by(models.Reservation.date.desc(), models.Reservation.start_time).all()
    rooms_list = db.query(models.Room).all()
    rooms = {r.id: r for r in rooms_list}
    return request.app.state.templates.TemplateResponse(
        "admin_reservations.html",
        {"request": request, "user": user, "reservations": reservations, "rooms": rooms},
    )


# === Editar reservas ===

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
    require_admin(request, db)
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404)
    res.title = title
    res.room_id = room_id
    res.date = date
    res.start_time = start_time
    res.end_time = end_time
    db.commit()
    return RedirectResponse(url="/admin/reservations", status_code=303)
