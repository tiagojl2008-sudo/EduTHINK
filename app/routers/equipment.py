from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse

from .. import models
from ..database import get_db
from ..utils import require_admin

router = APIRouter(prefix="/admin/equipment")


@router.get("")
async def list_equipment(request: Request, db=Depends(get_db)):
    """Listar todos os equipamentos."""
    user = require_admin(request, db)
    equipment_list = db.query(models.Equipment).all()
    rooms = db.query(models.Room).all()
    return request.app.state.templates.TemplateResponse(
        "admin_equipment.html",
        {"request": request, "user": user, "equipment_list": equipment_list, "rooms": rooms},
    )


@router.post("/create")
async def create_equipment(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    quantity: int = Form(...),
    room_id: int = Form(...),
    db=Depends(get_db),
):
    """Criar novo equipamento."""
    require_admin(request, db)
    equipment = models.Equipment(
        name=name,
        description=description,
        quantity=quantity,
        room_id=room_id,
    )
    db.add(equipment)
    db.commit()
    return RedirectResponse(url="/admin/equipment", status_code=303)


@router.post("/delete/{equip_id}")
async def delete_equipment(request: Request, equip_id: int, db=Depends(get_db)):
    """Eliminar equipamento."""
    require_admin(request, db)
    equipment = db.query(models.Equipment).filter(models.Equipment.id == equip_id).first()
    if equipment:
        db.delete(equipment)
        db.commit()
    return RedirectResponse(url="/admin/equipment", status_code=303)
