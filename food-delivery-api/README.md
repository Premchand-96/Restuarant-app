# Food Delivery Platform — Backend API

A complete FastAPI + PostgreSQL backend implementing the core system from your
architecture diagram: customer ordering, restaurant menu/order management,
delivery partner workflow, payments, coupons, reviews, and an admin dashboard.

63 endpoints across auth, addresses, restaurants, menu, cart, orders, payments,
coupons, reviews, delivery partners, notifications, and admin.

## What's included

- **Auth** — signup/login (JWT), role-based access (customer, restaurant_owner,
  delivery_partner, admin)
- **Restaurants** — browse/search/filter, owner registration, admin approval
- **Menu** — categories, food items, add-ons
- **Cart** — add/update/remove items, coupon codes, live pricing (tax + delivery
  fee + discount calculation)
- **Orders** — checkout, full status tracking (placed → accepted → preparing →
  ready_for_pickup → picked_up → out_for_delivery → delivered), cancel, reorder
- **Payments** — mock gateway supporting UPI / card / net banking / wallet / COD
- **Reviews** — restaurant + food + delivery ratings, rolls up to restaurant avg
- **Delivery partners** — profile, online/offline toggle, live location, claim
  orders for pickup
- **Admin** — dashboard stats, user management, restaurant approval queue

## Requirements

- Docker + Docker Compose (recommended — no local Python/Postgres setup needed)
- OR Python 3.11+ and a local PostgreSQL instance

## Quick start (Docker — recommended)

```bash
cd food-delivery-api
docker compose up --build
```

That's it. This starts:
- PostgreSQL on `localhost:5432`
- The API on `localhost:8000`

Tables are created automatically on startup.

Open the interactive API docs: **http://localhost:8000/docs**

To stop:
```bash
docker compose down
```

To stop and wipe the database:
```bash
docker compose down -v
```

## Quick start (without Docker)

1. Install and start PostgreSQL locally, then create the database:
   ```sql
   CREATE USER fooduser WITH PASSWORD 'foodpass';
   CREATE DATABASE fooddelivery OWNER fooduser;
   ```

2. Set up the Python environment:
   ```bash
   cd food-delivery-api
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # edit .env if your DB credentials differ
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Open http://localhost:8000/docs

## Testing the API end-to-end

The fastest way to try the full flow is through the Swagger UI at `/docs`,
using the "Authorize" button after signup/login. Example curl walkthrough:

```bash
BASE=http://localhost:8000

# 1. Sign up a restaurant owner
curl -s -X POST $BASE/api/auth/signup -H "Content-Type: application/json" -d '{
  "name": "Pizza Owner", "email": "owner@example.com", "password": "pass123",
  "role": "restaurant_owner"
}' | tee owner.json

OWNER_TOKEN=$(cat owner.json | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

# 2. Register a restaurant
curl -s -X POST $BASE/api/restaurants -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" -d '{
  "name": "Tasty Pizza", "address_line": "123 Main St", "city": "Tirupati",
  "cuisine": "Italian"
}' | tee restaurant.json

RESTAURANT_ID=$(cat restaurant.json | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")

# 3. As admin, approve the restaurant (sign up an admin user first, same as step 1
#    with "role": "admin", then):
curl -s -X PATCH $BASE/api/restaurants/$RESTAURANT_ID/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"status": "approved"}'

# 4. Add a menu item
curl -s -X POST $BASE/api/restaurants/$RESTAURANT_ID/items \
  -H "Authorization: Bearer $OWNER_TOKEN" -H "Content-Type: application/json" -d '{
  "name": "Margherita Pizza", "price": 299, "is_veg": true
}' | tee item.json

ITEM_ID=$(cat item.json | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")

# 5. Sign up a customer, add address, add item to cart, checkout
curl -s -X POST $BASE/api/auth/signup -H "Content-Type: application/json" -d '{
  "name": "Jane Customer", "email": "jane@example.com", "password": "pass123"
}' | tee customer.json

CUSTOMER_TOKEN=$(cat customer.json | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

curl -s -X POST $BASE/api/addresses -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" -d '{
  "line1": "456 Side St", "city": "Tirupati", "state": "AP", "postal_code": "517501"
}' | tee address.json

ADDRESS_ID=$(cat address.json | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")

curl -s -X POST $BASE/api/cart/items -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" -d "{\"food_item_id\": \"$ITEM_ID\", \"quantity\": 2}"

curl -s -X POST $BASE/api/orders -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" -d "{
  \"delivery_address_id\": \"$ADDRESS_ID\", \"payment_method\": \"cash_on_delivery\"
}"
```

## Project structure

```
food-delivery-api/
├── app/
│   ├── main.py              # FastAPI app entrypoint, router wiring
│   ├── core/
│   │   ├── config.py        # Settings (env vars)
│   │   ├── security.py      # Password hashing, JWT
│   │   └── deps.py          # Auth dependencies, role guards
│   ├── db/
│   │   └── database.py      # SQLAlchemy engine/session
│   ├── models/               # SQLAlchemy ORM models (11 tables)
│   ├── schemas/               # Pydantic request/response schemas
│   └── routers/               # API endpoints, grouped by domain
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Design notes / what's simplified vs. the original architecture

This backend covers the customer/restaurant/delivery-partner/admin flows and
the database layer from your diagram. A few things are intentionally
simplified for a working MVP rather than a production system:

- **Payments** are mocked (marked "success" immediately, except COD which
  stays "pending" until delivery) — no real payment gateway is integrated.
- **No push notifications / SMS / OTP** — the `Notification` model exists but
  nothing sends real notifications yet; OTP-based signup isn't implemented
  (plain email/password auth only).
- **No image upload** — `image_url` / `logo_url` fields exist but there's no
  file upload endpoint; you'd point these at URLs from S3 or similar.
- **No live GPS tracking / maps** — delivery partner location is stored but
  there's no real-time websocket tracking or map integration.
- **No Kubernetes/Terraform/CI-CD** — this ships as a Docker Compose app for
  local/dev use. The `DevOps`/`Production` layers from your diagram (EKS, RDS,
  Kubernetes, Argo CD, Terraform, CloudFront, etc.) are infrastructure
  decisions for when you're ready to deploy this to AWS — they're not
  something to scaffold speculatively before the app itself is proven out.
- **No automated test suite** — the routes and pricing/state-machine logic
  were manually verified (see below), but there's no pytest suite yet.

## What was verified

Since this sandbox doesn't have Docker or PostgreSQL available to run a live
end-to-end test, verification was done at the code level:

- The full app imports cleanly with no errors; all 63 routes register
- Fixed a routing bug where `/api/restaurants/me/mine` was being shadowed by
  `/api/restaurants/{restaurant_id}` (route ordering matters in FastAPI —
  fixed by declaring the literal path first)
- Cart/order pricing math (subtotal, flat & percentage discounts with caps,
  discount clamping, tax, delivery fee) was unit-tested in isolation against
  five scenarios including edge cases
- The order status state machine was validated to walk the full lifecycle
  (placed → accepted → preparing → ready_for_pickup → picked_up →
  out_for_delivery → delivered) with no gaps

**You should still run `docker compose up --build` and click through `/docs`
yourself before relying on this** — that exercises the real database layer
(foreign keys, cascades, UUID handling) which couldn't be tested in this
sandbox.

## Next steps to extend this

1. Add a `restaurant_id` param check + Alembic migrations for schema changes
   instead of `create_all` (already scaffolded — just needs `alembic init`)
2. Add real payment gateway integration (Razorpay/Stripe)
3. Add WebSocket support for live order tracking updates
4. Build the customer web/mobile app, restaurant dashboard, and delivery
   partner app against this API
5. Add a pytest suite with a test database
