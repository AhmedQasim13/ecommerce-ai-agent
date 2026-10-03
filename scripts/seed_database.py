"""Seed the database with mock e-commerce data.

Run from the project root:  python -m scripts.seed_database
WARNING: this wipes all rows in the five tables first.
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import text

from app.database.models import Category, Customer, Order, OrderItem, Product
from app.database.session import SessionLocal

random.seed(42)  # same data on every run

N_CUSTOMERS = 40
N_ORDERS = 200
DAYS_BACK = 180

OUT_OF_STOCK = {"ASUS ROG Strix G16 RTX 5070", "iPhone 17 Pro", "Google Pixel 9"}
POPULARITY_BOOST = {
    "Lenovo LOQ 15 RTX 5050": 4,
    "iPhone 17": 4,
    "Xiaomi Redmi Note 14 Pro": 3,
    "ASUS TUF Gaming F15 RTX 4050": 2.5,
    "Logitech G435": 2,
}


# ---------- catalog helpers: (category, brand, name, price EGP, rating, specs) ----------
def laptop(brand, name, price, rating, cpu, ram, ssd, gpu, vram, screen):
    return ("Laptops", brand, name, price, rating, {
        "cpu": cpu, "ram_gb": ram, "storage_gb": ssd,
        "gpu": gpu, "vram_gb": vram, "screen_in": screen})


def phone(brand, name, price, rating, storage, ram, screen):
    return ("Phones", brand, name, price, rating, {
        "storage_gb": storage, "ram_gb": ram, "screen_in": screen})


def headphones(brand, name, price, rating, kind, anc, battery_h):
    return ("Headphones", brand, name, price, rating, {
        "type": kind, "noise_cancelling": anc, "battery_hours": battery_h})


def monitor(brand, name, price, rating, size, res, hz, panel):
    return ("Monitors", brand, name, price, rating, {
        "size_in": size, "resolution": res, "refresh_hz": hz, "panel": panel})


def accessory(brand, name, price, rating, kind):
    return ("Accessories", brand, name, price, rating, {"type": kind})


CATALOG = [
    # Laptops
    laptop("Lenovo", "Lenovo LOQ 15 RTX 5050", 49500, 4.5, "Intel Core i5-13450HX", 24, 512, "RTX 5050", 8, 15.6),
    laptop("Lenovo", "Lenovo LOQ 15 RTX 4060", 58900, 4.6, "Intel Core i7-13650HX", 16, 1024, "RTX 4060", 8, 15.6),
    laptop("Lenovo", "Lenovo Legion 5 RTX 5060", 72000, 4.7, "AMD Ryzen 7 7745HX", 32, 1024, "RTX 5060", 8, 16),
    laptop("ASUS", "ASUS TUF Gaming F15 RTX 4050", 46500, 4.4, "Intel Core i5-12500H", 16, 512, "RTX 4050", 6, 15.6),
    laptop("ASUS", "ASUS TUF Gaming A16 RTX 5060", 69900, 4.6, "AMD Ryzen 7 7735HS", 16, 1024, "RTX 5060", 8, 16),
    laptop("ASUS", "ASUS ROG Strix G16 RTX 5070", 98000, 4.8, "Intel Core i9-14900HX", 32, 1024, "RTX 5070", 8, 16),
    laptop("ASUS", "ASUS Vivobook 15", 21500, 4.1, "Intel Core i5-1335U", 16, 512, "Intel Iris Xe", 0, 15.6),
    laptop("ASUS", "ASUS Zenbook 14 OLED", 42000, 4.6, "Intel Core Ultra 7 155H", 16, 1024, "Intel Arc", 0, 14),
    laptop("HP", "HP Victus 15 RTX 4050", 44000, 4.3, "AMD Ryzen 5 8645HS", 16, 512, "RTX 4050", 6, 15.6),
    laptop("HP", "HP Pavilion 15", 24500, 4.0, "Intel Core i5-1335U", 8, 512, "Intel Iris Xe", 0, 15.6),
    laptop("HP", "HP Omen 16 RTX 5060", 76000, 4.6, "Intel Core i7-14700HX", 32, 1024, "RTX 5060", 8, 16),
    laptop("Dell", "Dell G15 RTX 4050", 45500, 4.2, "AMD Ryzen 5 7640HS", 16, 512, "RTX 4050", 6, 15.6),
    laptop("Dell", "Dell Inspiron 15", 22500, 3.9, "Intel Core i5-1334U", 8, 512, "Intel Iris Xe", 0, 15.6),
    laptop("Dell", "Dell XPS 13", 68000, 4.7, "Intel Core Ultra 7 258V", 32, 1024, "Intel Arc 140V", 0, 13.4),
    laptop("Acer", "Acer Nitro V 15 RTX 4050", 42500, 4.2, "Intel Core i5-13420H", 16, 512, "RTX 4050", 6, 15.6),
    laptop("Apple", "MacBook Air M3", 62000, 4.8, "Apple M3", 16, 512, "Integrated", 0, 13.6),
    # Phones
    phone("Apple", "iPhone 17", 54000, 4.7, 256, 8, 6.3),
    phone("Apple", "iPhone 17 Pro", 76000, 4.8, 256, 12, 6.3),
    phone("Apple", "iPhone 16", 46000, 4.6, 128, 8, 6.1),
    phone("Samsung", "Samsung Galaxy S25", 41000, 4.6, 256, 12, 6.2),
    phone("Samsung", "Samsung Galaxy S25 Ultra", 72000, 4.8, 256, 12, 6.9),
    phone("Samsung", "Samsung Galaxy A56", 18500, 4.3, 256, 8, 6.7),
    phone("Xiaomi", "Xiaomi Redmi Note 14 Pro", 14500, 4.4, 256, 8, 6.67),
    phone("Xiaomi", "Xiaomi 15", 33000, 4.5, 256, 12, 6.36),
    phone("Oppo", "Oppo Reno 13", 19900, 4.2, 256, 12, 6.59),
    phone("Realme", "Realme 14 Pro", 15500, 4.2, 256, 8, 6.77),
    phone("Google", "Google Pixel 9", 36000, 4.5, 128, 12, 6.3),
    # Headphones
    headphones("Sony", "Sony WH-1000XM5", 12500, 4.8, "over-ear", True, 30),
    headphones("Apple", "Apple AirPods Pro 2", 11500, 4.7, "in-ear", True, 6),
    headphones("Samsung", "Samsung Galaxy Buds3", 6500, 4.3, "in-ear", True, 6),
    headphones("JBL", "JBL Tune 770NC", 3200, 4.2, "over-ear", True, 44),
    headphones("Anker", "Anker Soundcore Q30", 2800, 4.4, "over-ear", True, 40),
    headphones("Logitech", "Logitech G435", 2300, 4.1, "over-ear", False, 18),
    # Monitors
    monitor("LG", "LG UltraGear 27 165Hz", 9500, 4.5, 27, "1920x1080", 165, "IPS"),
    monitor("Samsung", "Samsung Odyssey G5 27", 10500, 4.4, 27, "2560x1440", 144, "VA"),
    monitor("Dell", "Dell S2425H 24", 5200, 4.3, 24, "1920x1080", 100, "IPS"),
    monitor("ASUS", "ASUS TUF VG27AQ 27", 11800, 4.6, 27, "2560x1440", 165, "IPS"),
    monitor("Xiaomi", "Xiaomi A27i", 3800, 4.2, 27, "1920x1080", 100, "IPS"),
    # Accessories
    accessory("Logitech", "Logitech MX Master 3S", 4300, 4.8, "mouse"),
    accessory("Logitech", "Logitech G502 Hero", 2400, 4.6, "mouse"),
    accessory("Keychron", "Keychron K2", 3600, 4.5, "keyboard"),
    accessory("Anker", "Anker 65W GaN Charger", 1500, 4.6, "charger"),
    accessory("Samsung", "Samsung T7 1TB SSD", 4200, 4.7, "external storage"),
    accessory("Cooler Master", "Cooler Master Notepal Cooling Pad", 1100, 4.1, "cooling pad"),
]

FIRST = ["Ahmed", "Mohamed", "Mahmoud", "Omar", "Youssef", "Ali", "Hassan", "Karim",
         "Mostafa", "Khaled", "Sara", "Nour", "Mona", "Fatma", "Aya", "Hana",
         "Salma", "Mariam", "Dina", "Rania"]
LAST = ["Hassan", "Ibrahim", "Mansour", "Saleh", "Farouk", "Nasser", "Salem",
        "Zaki", "Fahmy", "Gaber", "Soliman", "Khalil"]


def describe(brand, name, specs):
    details = ", ".join(f"{k}: {v}" for k, v in specs.items())
    return f"{name} by {brand}. {details}."


def main():
    with SessionLocal() as db:
        db.execute(text(
            "TRUNCATE order_items, orders, customers, products, categories "
            "RESTART IDENTITY CASCADE"))

        # categories
        categories = {n: Category(name=n) for n in dict.fromkeys(c[0] for c in CATALOG)}
        db.add_all(categories.values())

        # products
        products = []
        for cat, brand, name, price, rating, specs in CATALOG:
            stock = 0 if name in OUT_OF_STOCK else random.choice([2, 5, 8, 12, 20, 35, 50])
            products.append(Product(
                name=name, brand=brand, category=categories[cat],
                price=Decimal(price), stock_quantity=stock, specifications=specs,
                rating=rating, description=describe(brand, name, specs)))
        db.add_all(products)

        # customers
        customers = []
        for i in range(N_CUSTOMERS):
            first, last = random.choice(FIRST), random.choice(LAST)
            customers.append(Customer(
                name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}{i}@example.com"))
        db.add_all(customers)

        # orders: cheaper and boosted products sell more
        weights = [
            (1 / float(p.price) ** 0.5) * random.uniform(0.6, 1.6) * POPULARITY_BOOST.get(p.name, 1)
            for p in products
        ]
        now = datetime.now()
        for _ in range(N_ORDERS):
            picked = {p.id or id(p): p for p in random.choices(products, weights, k=random.randint(1, 3))}
            items = []
            for p in picked.values():
                qty = random.choice([1, 1, 1, 2]) if p.category.name in ("Accessories", "Headphones") else 1
                items.append(OrderItem(product=p, quantity=qty, unit_price=p.price))
            db.add(Order(
                customer=random.choice(customers),
                items=items,
                total_price=sum(i.unit_price * i.quantity for i in items),
                status=random.choices(["completed", "pending", "cancelled"], [88, 5, 7])[0],
                created_at=now - timedelta(
                    days=random.randint(0, DAYS_BACK), seconds=random.randint(0, 86_399)),
            ))

        db.commit()
        print(f"Seeded {len(categories)} categories, {len(products)} products, "
              f"{len(customers)} customers, {N_ORDERS} orders.")


if __name__ == "__main__":
    main()