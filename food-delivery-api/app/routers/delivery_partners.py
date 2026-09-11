from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_delivery_partner
from app.db.database import get_db
from app.models.delivery_partner import DeliveryPartner
from app.models.user import User
from app.schemas.misc import (
    DeliveryLocationUpdate,
    DeliveryPartnerCreate,
    DeliveryPartnerOut,
    DeliveryStatusUpdate,
)

router = APIRouter(prefix="/api/delivery-partners", tags=["Delivery Partners"])


@router.post("/profile", response_model=DeliveryPartnerOut, status_code=201)
def create_profile(payload: DeliveryPartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(require_delivery_partner)):
    existing = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    partner = DeliveryPartner(user_id=current_user.id, **payload.model_dump())
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return partner


@router.get("/me", response_model=DeliveryPartnerOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(require_delivery_partner)):
    partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")
    return partner


@router.patch("/me/status", response_model=DeliveryPartnerOut)
def update_online_status(payload: DeliveryStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_delivery_partner)):
    partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Profile not found")
    partner.is_online = payload.is_online
    db.commit()
    db.refresh(partner)
    return partner


@router.patch("/me/location", response_model=DeliveryPartnerOut)
def update_location(payload: DeliveryLocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_delivery_partner)):
    partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Profile not found")
    partner.current_latitude = payload.latitude
    partner.current_longitude = payload.longitude
    db.commit()
    db.refresh(partner)
    return partner
