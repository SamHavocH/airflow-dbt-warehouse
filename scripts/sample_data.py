from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from random import Random
from uuid import NAMESPACE_URL, uuid5


def _ts(days_ago: int, hour: int = 10) -> datetime:
    base = datetime(2026, 5, 20, hour, 0, tzinfo=UTC)
    return base - timedelta(days=days_ago)


CUSTOMERS = [
    ("C001", "Ana Silva", "ana@example.com", "BR", "Sao Paulo"),
    ("C002", "Bruno Costa", "bruno@example.com", "BR", "Rio de Janeiro"),
    ("C003", "Carla Gomez", "carla@example.com", "AR", "Buenos Aires"),
    ("C004", "Diego Lima", "diego@example.com", "BR", "Curitiba"),
    ("C005", "Emma Johnson", "emma@example.com", "US", "Austin"),
]

PRODUCTS = [
    ("P001", "Noise cancelling headphones", "electronics", Decimal("199.90")),
    ("P002", "Standing desk mat", "office", Decimal("59.90")),
    ("P003", "Mechanical keyboard", "electronics", Decimal("129.00")),
    ("P004", "Analytics notebook", "office", Decimal("18.50")),
    ("P005", "Coffee subscription", "lifestyle", Decimal("34.00")),
]


def build_customers() -> list[dict[str, object]]:
    rows = []
    for idx, (customer_id, name, email, country, city) in enumerate(CUSTOMERS, start=1):
        rows.append(
            {
                "customer_id": customer_id,
                "full_name": name,
                "email": email,
                "country": country,
                "city": city,
                "created_at": _ts(60 - idx),
                "updated_at": _ts(5 - (idx % 3)),
            }
        )

    rows.append({**rows[1], "city": "Niteroi", "updated_at": _ts(1)})
    return rows


def build_products() -> list[dict[str, object]]:
    return [
        {
            "product_id": product_id,
            "product_name": name,
            "category": category,
            "unit_price": price,
            "updated_at": _ts(2),
        }
        for product_id, name, category, price in PRODUCTS
    ]


def build_orders(days: int = 45) -> list[dict[str, object]]:
    rnd = Random(42)
    statuses = ["completed", "completed", "completed", "refunded", "cancelled"]
    rows = []
    for day in range(days):
        for order_number in range(1, rnd.randint(3, 7)):
            customer_id = rnd.choice(CUSTOMERS)[0]
            product_id, _, _, price = rnd.choice(PRODUCTS)
            quantity = rnd.randint(1, 4)
            status = rnd.choice(statuses)
            order_id = f"O{day:03d}{order_number:02d}"
            ordered_at = _ts(day, hour=rnd.randint(8, 22))
            rows.append(
                {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "product_id": product_id,
                    "ordered_at": ordered_at,
                    "quantity": quantity,
                    "unit_price": price,
                    "discount_amount": Decimal(str(rnd.choice([0, 0, 5, 10]))),
                    "status": status,
                    "updated_at": ordered_at + timedelta(hours=rnd.randint(1, 36)),
                }
            )

    duplicate = rows[8].copy()
    duplicate["status"] = "completed"
    duplicate["updated_at"] = duplicate["updated_at"] + timedelta(days=1)
    rows.append(duplicate)
    return rows


def build_events(days: int = 45) -> list[dict[str, object]]:
    rnd = Random(7)
    events = ["page_view", "product_view", "add_to_cart", "checkout_started", "purchase"]
    rows = []
    for day in range(days):
        for sequence in range(rnd.randint(8, 18)):
            customer_id = rnd.choice(CUSTOMERS)[0]
            event_name = rnd.choices(events, weights=[40, 25, 15, 10, 10], k=1)[0]
            occurred_at = _ts(day, hour=rnd.randint(0, 23)) + timedelta(minutes=rnd.randint(0, 59))
            event_key = f"{customer_id}-{event_name}-{occurred_at.isoformat()}-{sequence}"
            rows.append(
                {
                    "event_id": str(uuid5(NAMESPACE_URL, event_key)),
                    "customer_id": customer_id,
                    "session_id": str(uuid5(NAMESPACE_URL, f"{customer_id}-{day}-{sequence // 4}")),
                    "event_name": event_name,
                    "occurred_at": occurred_at,
                    "utm_source": rnd.choice(["organic", "paid_search", "email", "direct"]),
                    "loaded_at": datetime.now(UTC),
                }
            )
    return rows
