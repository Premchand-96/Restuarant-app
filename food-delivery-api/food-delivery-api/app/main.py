from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
import app.models  # noqa: F401  (ensures all models are registered with Base)

from app.routers import (
    addresses,
    admin,
    auth,
    cart,
    coupons,
    delivery_partners,
    menu,
    notifications,
    orders,
    payments,
    restaurants,
    reviews,
)

app = FastAPI(
    title="Food Delivery Platform API",
    description="Backend API for a food delivery platform: customers, restaurants, delivery partners, and admin.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist yet. For production, prefer Alembic migrations.
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "food-delivery-api"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(addresses.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(coupons.router)
app.include_router(reviews.router)
app.include_router(delivery_partners.router)
app.include_router(notifications.router)
app.include_router(admin.router)
