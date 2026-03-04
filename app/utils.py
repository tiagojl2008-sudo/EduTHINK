from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from . import models
from .database import get_db


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Lê o cookie `user_id` e retorna o objecto User ou None."""
    uid = request.cookies.get("user_id")
    if not uid:
        return None
    return db.query(models.User).filter(models.User.id == int(uid)).first()


def require_login(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


def require_admin(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


def times_overlap(s1: str, e1: str, s2: str, e2: str) -> bool:
    """Retorna True se dois horários HH:MM se sobrepõem."""
    t1 = datetime.strptime(s1, "%H:%M").time()
    t2 = datetime.strptime(e1, "%H:%M").time()
    t3 = datetime.strptime(s2, "%H:%M").time()
    t4 = datetime.strptime(e2, "%H:%M").time()
    return t1 < t4 and t2 > t3


def time_in_range(start: str, end: str, room_start: str, room_end: str) -> bool:
    t_start=datetime.strptime(start, "%H:%M").time()
    t_end=datetime.strptime(end, "%H:%M").time()
    room_start=datetime.strptime(room_start,"%H:%M").time()
    room_end=datetime.strptime(room_end,"%H:%M").time()
    return t_start >= room_start and t_end <= room_end
