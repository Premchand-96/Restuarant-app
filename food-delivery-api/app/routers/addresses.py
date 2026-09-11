import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.address import Address
from app.models.user import User
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate

router = APIRouter(prefix="/api/addresses", tags=["Addresses"])


@router.get("", response_model=List[AddressOut])
def list_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Address).filter(Address.user_id == current_user.id).all()


@router.post("", response_model=AddressOut, status_code=201)
def create_address(payload: AddressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.is_default:
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
    address = Address(user_id=current_user.id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.patch("/{address_id}", response_model=AddressOut)
def update_address(address_id: uuid.UUID, payload: AddressUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("is_default"):
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
    for key, value in update_data.items():
        setattr(address, key, value)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=204)
def delete_address(address_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return None
