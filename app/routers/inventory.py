from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse

from .. import models
from ..database import get_db
from ..utils import require_admin

router = APIRouter(prefix="/admin/inventory")


# Listar os equipamentos
@router.get("")
async def list_inventory(request: Request, db=Depends(get_db)):
    user = require_admin(request, db)
    equipment_list = db.query(models.Equipment).all()
    rooms = db.query(models.Room).all()
    
    return request.app.state.templates.TemplateResponse(
        "admin_inventory.html",
        {
            "request": request,
            "user": user,
            "equipment": equipment_list,
            "rooms": rooms,
        },
    )


# Adicionar equipamento
@router.post("/create")
async def create_equipment(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    quantity: int = Form(...),
    room_id: int = Form(...),
    db=Depends(get_db),
):
    user = require_admin(request, db)
    
    equipment = models.Equipment(
        name=name,
        description=description,
        quantity=quantity,
        room_id=room_id,
    )
    db.add(equipment)
    db.commit()
    
    return RedirectResponse(url="/admin/inventory", status_code=303)


# Editar equipamento
@router.post("/update/{equipment_id}")
async def update_equipment(
    request: Request,
    equipment_id: int,
    name: str = Form(...),
    description: str = Form(default=""),
    quantity: int = Form(...),
    room_id: int = Form(...),
    db=Depends(get_db),
):
    user = require_admin(request, db)
    
    equipment = db.query(models.Equipment).filter(
        models.Equipment.id == equipment_id
    ).first()
    
    if not equipment:
        raise HTTPException(status_code=404)
    
    equipment.name = name
    equipment.description = description
    equipment.quantity = quantity
    equipment.room_id = room_id
    
    db.commit()
    return RedirectResponse(url="/admin/inventory", status_code=303)


# Eliminar equipamento
@router.post("/delete/{equipment_id}")
async def delete_equipment(request: Request, equipment_id: int, db=Depends(get_db)):
    user = require_admin(request, db)
    
    equipment = db.query(models.Equipment).filter(
        models.Equipment.id == equipment_id
    ).first()
    
    if equipment:
        db.delete(equipment)
        db.commit()
    
    return RedirectResponse(url="/admin/inventory", status_code=303)

@router.post("/assign-to-user/equipment_id}")
async def assign_to_user(
    request: Requets
)