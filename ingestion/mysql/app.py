import os
import json
from datetime import datetime, timedelta
import random
import boto3
import mysql.connector


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def ensure_table(cursor) -> None:
    # Las tablas ya existen según init.sql: users, products, orders
    pass


def generate_fake_users(num_rows: int) -> list[tuple]:
    nombres = ["Ana", "Carlos", "María", "José", "Laura", "Pedro", "Sofia", "Diego", "Elena", "Miguel"]
    apellidos = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"]
    dominios = ["gmail.com", "hotmail.com", "yahoo.com", "utec.edu.pe", "outlook.com"]
    
    rows: list[tuple] = []
    for i in range(1, num_rows + 1):
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)} {i}"
        email = f"user{i}@{random.choice(dominios)}"
        phone = f"+51{random.randint(900000000, 999999999)}"
        address = f"Dirección {i}, Lima, Perú"
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
        rows.append((nombre, email, phone, address, created_at))
    return rows

def generate_fake_products(num_rows: int) -> list[tuple]:
    nombres_productos = [
        "California Roll Premium", "Dragon Roll Especial", "Tempura de Camarón", 
        "Sashimi Mixto", "Ramen Maki Deluxe", "Green Dragon Roll",
        "Spicy Tuna Roll", "Salmon Roll", "Eel Roll", "Crab Roll"
    ]
    
    rows: list[tuple] = []
    for i in range(1, num_rows + 1):
        nombre = f"{random.choice(nombres_productos)} {i}"
        precio = round(random.uniform(15.99, 35.99), 2)
        calorias = random.randint(250, 600)
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
        rows.append((nombre, precio, calorias, created_at))
    return rows

def generate_fake_orders(num_rows: int, user_ids: list, product_ids: list) -> list[tuple]:
    statuses = ['pending', 'confirmed', 'preparing', 'delivered', 'cancelled']
    payment_methods = ['cash', 'card', 'transfer']
    
    rows: list[tuple] = []
    for i in range(1, num_rows + 1):
        user_id = random.choice(user_ids)
        product_id = random.choice(product_ids)
        status = random.choice(statuses)
        order_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        total_price = round(random.uniform(15.99, 35.99), 2)
        payment_method = random.choice(payment_methods)
        rows.append((user_id, product_id, status, order_date, total_price, payment_method))
    return rows


def seed_mysql(conn, num_rows: int) -> int:
    with conn.cursor() as cursor:
        ensure_table(cursor)
        
        # Limpiar tablas existentes
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM products") 
        cursor.execute("DELETE FROM users")
        
        # Insertar usuarios
        user_rows = generate_fake_users(min(num_rows, 1000))
        cursor.executemany(
            "INSERT INTO users (name, email, phone_number, address, created_at) VALUES (%s,%s,%s,%s,%s)",
            user_rows
        )
        
        # Obtener IDs de usuarios insertados
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # Insertar productos
        product_rows = generate_fake_products(min(num_rows, 500))
        cursor.executemany(
            "INSERT INTO products (name, price, calories, created_at) VALUES (%s,%s,%s,%s)",
            product_rows
        )
        
        # Obtener IDs de productos insertados
        cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        # Insertar órdenes
        order_rows = generate_fake_orders(min(num_rows, 2000), user_ids, product_ids)
        cursor.executemany(
            "INSERT INTO orders (user_id, product_id, status, order_date, total_price, payment_method) VALUES (%s,%s,%s,%s,%s,%s)",
            order_rows
        )
        
    conn.commit()
    return len(user_rows) + len(product_rows) + len(order_rows)


def export_to_s3(conn, bucket: str, key_prefix: str) -> dict:
    all_data = {}
    
    with conn.cursor(dictionary=True) as cursor:
        # Exportar usuarios
        cursor.execute("SELECT * FROM users")
        all_data['users'] = cursor.fetchall()
        
        # Exportar productos
        cursor.execute("SELECT * FROM products")
        all_data['products'] = cursor.fetchall()
        
        # Exportar órdenes
        cursor.execute("SELECT * FROM orders")
        all_data['orders'] = cursor.fetchall()

    body = json.dumps(all_data, default=str)
    s3 = boto3.client("s3")
    timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
    key = f"{key_prefix}/{timestamp}/data.json"
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"), ContentType="application/json")
    
    total_records = len(all_data['users']) + len(all_data['products']) + len(all_data['orders'])
    return {"bucket": bucket, "key": key, "records": total_records}


def main() -> None:
    mode = os.getenv("MODE", "seed_and_export")  # seed | export | seed_and_export

    host = get_env("DB_HOST")
    port = int(get_env("DB_PORT", "3306"))
    user = get_env("DB_USER")
    password = get_env("DB_PASSWORD")
    database = get_env("DB_NAME")

    s3_bucket = os.getenv("S3_BUCKET")
    s3_prefix = os.getenv("S3_PREFIX", "mysql/ingredientes")
    num_rows = int(os.getenv("FAKE_COUNT", "20000"))

    conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)

    if mode in ("seed", "seed_and_export"):
        inserted = seed_mysql(conn, num_rows)
        print(f"Seeded MySQL: inserted {inserted} rows")

    if mode in ("export", "seed_and_export"):
        if not s3_bucket:
            raise RuntimeError("S3_BUCKET is required for export")
        result = export_to_s3(conn, s3_bucket, s3_prefix)
        print(f"Exported to s3://{result['bucket']}/{result['key']} ({result['records']} records)")

    conn.close()


if __name__ == "__main__":
    main()


