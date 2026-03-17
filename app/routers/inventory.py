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
    users = db.query(models.User).all()

    return request.app.state.templates.TemplateResponse(
        "admin_iventory.html",
        {
            "request": request,
            "user": user,
            "equipment": equipment_list,
            "rooms": rooms,
            "users": users,
        },
    )


# Adicionar equipamento
@router.post("/create")
async def create_equipment(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    room_id: int = Form(...),
    db=Depends(get_db),
):
    user = require_admin(request, db)

    equipment = models.Equipment(
        name=name,
        description=description,
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


# Atribuir equipamento a utilizador
@router.post("/assign-to-user/{equipment_id}")
async def assign_to_user(
    request: Request,
    equipment_id: int,
    user_id: int = Form(...),
    notes: str = Form(default=""),
    db=Depends(get_db)
):
    user = require_admin(request, db)
    
    try:
        # Verificar se equipamento existe
        equipment = db.query(models.Equipment).filter(
            models.Equipment.id == equipment_id
        ).first()
        
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        
        # Verificar se utilizador existe
        target_user = db.query(models.User).filter(
            models.User.id == user_id
        ).first()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")
        
        # Criar atribuição
        from datetime import datetime
        assignment = models.UserEquipment(
            user_id=user_id,
            equipment_id=equipment_id,
            assigned_date=datetime.now().strftime("%Y-%m-%d"),
            notes=notes
        )
        db.add(assignment)
        db.commit()

        return RedirectResponse(url="/admin/inventory", status_code=303)

    except Exception as e:
        print(f"ERRO ao atribuir: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Remover atribuição de equipamento a utilizador
@router.post("/remove-assignment/{assignment_id}")
async def remove_assignment(request: Request, assignment_id: int, db=Depends(get_db)):
    user = require_admin(request, db)
    
    assignment = db.query(models.UserEquipment).filter(
        models.UserEquipment.id == assignment_id
    ).first()
    
    if assignment:
        db.delete(assignment)
        db.commit()
    
    return RedirectResponse(url="/admin/inventory/by-user", status_code=303)


# Ver equipamentos por utilizador
@router.get("/by-user")
async def equipment_by_user(request: Request, db=Depends(get_db)):
    user = require_admin(request, db)

    assignments = db.query(models.UserEquipment).all()
    users = db.query(models.User).all()
    equipment_list = db.query(models.Equipment).all()

    return request.app.state.templates.TemplateResponse(
        "admin_equipment_by_user.html",
        {
            "request": request,
            "user": user,
            "assignments": assignments,
            "users": users,
            "equipment": equipment_list,
        },
    )


# Devolver equipamento (remove atribuição)
@router.post("/return-equipment/{assignment_id}")
async def return_equipment(request: Request, assignment_id: int, db=Depends(get_db)):
    user = require_admin(request, db)

    assignment = db.query(models.UserEquipment).filter(
        models.UserEquipment.id == assignment_id
    ).first()

    if assignment:
        db.delete(assignment)
        db.commit()

    return RedirectResponse(url="/admin/inventory/by-user", status_code=303)