from fastapi import APIRouter, Request, Depends
from datetime import date as date_type
from sqlalchemy.orm import joinedload

from .. import models
from ..database import get_db
from ..utils import get_current_user

router = APIRouter()


@router.get("/")
async def public_view(request: Request, db=Depends(get_db)):
    rooms = db.query(models.Room).all()
    today = str(date_type.today())
    reservations = db.query(models.Reservation).options(
        joinedload(models.Reservation.room),
        joinedload(models.Reservation.user),
    ).filter(models.Reservation.date == today).all()
    user = get_current_user(request, db)
    return request.app.state.templates.TemplateResponse(
        "public.html",
        {"request": request, "rooms": rooms, "reservations": reservations, "today": today, "user": user},
    )
