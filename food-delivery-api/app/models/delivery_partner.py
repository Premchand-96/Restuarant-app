import enum
import uuid

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class VehicleType(str, enum.Enum):
    bike = "bike"
    bicycle = "bicycle"
    scooter = "scooter"
    car = "car"


class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    vehicle_type = Column(Enum(VehicleType), default=VehicleType.bike)
    vehicle_number = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    is_online = Column(Boolean, default=False)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    avg_rating = Column(Float, default=0.0)
    total_deliveries = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="delivery_partner_profile")
    orders = relationship("Order", back_populates="delivery_partner")
