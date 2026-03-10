1from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from datetime import date as date_type

from .. import models
from ..database import get_db
from ..utils import require_admin

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


# ===================================================================
# SALAS
# ===================================================================

@router.get("/rooms")
async def rooms(request: Request, db=Depends(get_db)):
    """Listar todas as salas."""
    try:
        user = require_admin(request, db)
        print(f"[DEBUG] User admin: {user.name} (id={user.id})")
    except Exception as e:
        print(f"[DEBUG] Erro require_admin: {e}")
        raise
    
    rooms = db.query(models.Room).all()
    print(f"[DEBUG] /admin/rooms - {len(rooms)} salas encontradas")
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
    db=Depends(get_db),
):
    require_admin(request, db)
    
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
                {"request": request, "user": require_admin(request, db), "users": users, "error": "Este email já está em uso."},
            )
    
    target.name = name
    target.email = email
    target.role = role
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/users/delete/{user_id}")
async def delete_user(request: Request, user_id: int, db=Depends(get_db)):
    require_admin(request, db)
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if target:
        db.delete(target)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


# ===================================================================
# RESERVAS
# ===================================================================

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

#Gestão de utilizadores
@router.get("/users")
async def list_users(request:Request, db=Depends(get_db)):
    user=require_admin(request,db)
    users=db.query(models.User).all()
    return request.app.state.templates.TemplateResponse(
        "admin_users.html"
        {
            "request": request, "user": user, "users": users,
        },
    )
@router.post("/users/update/{user_id}")
async def update_user(
    request: Request, user_id: int, name: str= Form(...), email: str=Form(...), role: str=Form(...) #admin ou user
    db=Depends(get_db),
):
    admin=require_admin(request,db)
    target_user=db.query(models.User).filter(models.User.id==user_id).first()
    if not target_user:
        raise HTTPException(status_code=404)
    target_user=name
    target_user=email
    target_user=role
    db.commit()
    return RedirectResponse(url="admin/users",status_code=303)

@router.post("/users/delete/{user_id}")
async def delete_user(request: Request, user_id:int,db=Depends(get_db)):
    admin=require_admin(request,db)
    target_user=db.query(models.User).filter(models.User.id==user_id).first()

    if target_user:
        # Não permitir eliminar a si próprio
        if target_user.id==admin.id:
            raise HTTPException(statuts_code=400, detail=" Não podes eliminar-te a ti mesmo.")
        db.delete(target_user)
        db.commit()
        return RedirectResponse(url="/admin/users",status_code=303)