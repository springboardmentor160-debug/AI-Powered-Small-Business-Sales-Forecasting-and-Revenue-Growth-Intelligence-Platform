from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from auth import RoleChecker, get_password_hash

router = APIRouter(prefix="/api/v1/staff", tags=["Staff Administration"])
admin_only = RoleChecker(["admin"])


@router.get("/", response_model=List[schemas.StaffOut], dependencies=[Depends(admin_only)])
def list_staff(db: Session = Depends(get_db)):
    members = db.query(models.Staff).all()
    return [
        schemas.StaffOut(
            staff_id=m.staff_id,
            username=m.username,
            email=m.email,
            full_name=m.full_name,
            role_id=m.role_id,
            outlet_id=m.outlet_id,
            is_active=m.is_active,
            role_name=m.role.role_name if m.role else None
        ) for m in members
    ]


@router.post("/", response_model=schemas.StaffOut, dependencies=[Depends(admin_only)])
def create_staff(staff_in: schemas.StaffCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Staff).filter(
        (models.Staff.username == staff_in.username) | (models.Staff.email == staff_in.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already in use")

    role = db.query(models.Role).filter(models.Role.role_id == staff_in.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role ID not found")

    new_staff = models.Staff(
        username=staff_in.username,
        email=staff_in.email,
        hashed_password=get_password_hash(staff_in.password),
        full_name=staff_in.full_name,
        role_id=staff_in.role_id,
        outlet_id=staff_in.outlet_id
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return schemas.StaffOut(
        staff_id=new_staff.staff_id,
        username=new_staff.username,
        email=new_staff.email,
        full_name=new_staff.full_name,
        role_id=new_staff.role_id,
        outlet_id=new_staff.outlet_id,
        is_active=new_staff.is_active,
        role_name=role.role_name
    )
