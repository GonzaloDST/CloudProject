import os
import json
from datetime import datetime, timedelta
import random
import boto3
import psycopg2


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def ensure_table(cur) -> None:
    # Las tablas ya existen según init.sql: ingrediente, maki, maki_ingrediente
    pass


def generate_fake_ingredientes(num_rows: int) -> list[tuple]:
    nombres_ingredientes = [
        "Salmón", "Atún", "Pollo", "Carne", "Huevo",
        "Lechuga", "Tomate", "Cebolla", "Ajo", "Perejil",
        "Sal", "Pimienta", "Aceite", "Vinagre", "Salsa",
        "Queso", "Leche", "Yogurt", "Mantequilla", "Crema",
        "Arroz", "Trigo", "Avena", "Quinoa", "Cebada",
        "Palta", "Tampico", "Queso crema", "Cangrejo", "Pepino"
    ]
    
    rows: list[tuple] = []
    for i in range(1, num_rows + 1):
        nombre = f"{random.choice(nombres_ingredientes)} {i}"
        stock = random.randint(10, 200)
        rows.append((nombre, stock))
    return rows

def generate_fake_makis(num_rows: int) -> list[tuple]:
    nombres_makis = [
        "California Roll", "Acevichado", "Philadelphia Roll",
        "Dragon Roll", "Spicy Tuna Roll", "Salmon Roll",
        "Eel Roll", "Crab Roll", "Tempura Roll", "Rainbow Roll"
    ]
    
    descripciones = [
        "Maki clásico con palta, cangrejo y pepino",
        "Maki relleno de pescado y cubierto con salsa acevichada", 
        "Maki con salmón y queso crema",
        "Maki especial con ingredientes premium",
        "Maki picante con atún fresco",
        "Maki tradicional con salmón",
        "Maki con anguila y salsa especial",
        "Maki de cangrejo con mayonesa",
        "Maki frito con tempura",
        "Maki colorido con múltiples ingredientes"
    ]
    
    rows: list[tuple] = []
    for i in range(1, num_rows + 1):
        nombre = f"{random.choice(nombres_makis)} {i}"
        descripcion = random.choice(descripciones)
        precio = round(random.uniform(15.50, 35.99), 2)
        rows.append((nombre, descripcion, precio))
    return rows

def generate_fake_maki_ingredientes(num_makis: int, num_ingredientes: int) -> list[tuple]:
    rows: list[tuple] = []
    for maki_id in range(1, num_makis + 1):
        # Cada maki tendrá entre 2-5 ingredientes
        num_ingredientes_por_maki = random.randint(2, 5)
        ingredientes_usados = set()
        
        for _ in range(num_ingredientes_por_maki):
            ingrediente_id = random.randint(1, num_ingredientes)
            if ingrediente_id not in ingredientes_usados:
                ingredientes_usados.add(ingrediente_id)
                rows.append((maki_id, ingrediente_id))
    return rows


def seed_postgres(conn, num_rows: int) -> int:
    with conn.cursor() as cur:
        ensure_table(cur)
        
        # Limpiar tablas existentes
        cur.execute("DELETE FROM maki_ingrediente")
        cur.execute("DELETE FROM maki")
        cur.execute("DELETE FROM ingrediente")
        
        # Insertar ingredientes
        ingrediente_rows = generate_fake_ingredientes(min(num_rows, 100))
        for row in ingrediente_rows:
            cur.execute("INSERT INTO ingrediente (nombre, stock) VALUES (%s, %s)", row)
        
        # Obtener IDs de ingredientes insertados
        cur.execute("SELECT id FROM ingrediente")
        ingrediente_ids = [row[0] for row in cur.fetchall()]
        
        # Insertar makis
        maki_rows = generate_fake_makis(min(num_rows, 50))
        for row in maki_rows:
            cur.execute("INSERT INTO maki (nombre, descripcion, precio) VALUES (%s, %s, %s)", row)
        
        # Obtener IDs de makis insertados
        cur.execute("SELECT id FROM maki")
        maki_ids = [row[0] for row in cur.fetchall()]
        
        # Insertar relaciones maki-ingrediente
        maki_ingrediente_rows = generate_fake_maki_ingredientes(len(maki_ids), len(ingrediente_ids))
        for row in maki_ingrediente_rows:
            cur.execute("INSERT INTO maki_ingrediente (maki_id, ingrediente_id) VALUES (%s, %s)", row)
        
    conn.commit()
    return len(ingrediente_rows) + len(maki_rows) + len(maki_ingrediente_rows)


def export_to_s3(conn, bucket: str, key_prefix: str) -> dict:
    json_lines = []
    
    with conn.cursor() as cur:
        # Exportar ingredientes (one-line JSON)
        cur.execute("SELECT row_to_json(t) FROM (SELECT * FROM ingrediente) t")
        for row in cur.fetchall():
            json_lines.append(json.dumps(row[0], default=str))
        
        # Exportar makis (one-line JSON)
        cur.execute("SELECT row_to_json(t) FROM (SELECT * FROM maki) t")
        for row in cur.fetchall():
            json_lines.append(json.dumps(row[0], default=str))
        
        # Exportar relaciones maki-ingrediente (one-line JSON)
        cur.execute("SELECT row_to_json(t) FROM (SELECT * FROM maki_ingrediente) t")
        for row in cur.fetchall():
            json_lines.append(json.dumps(row[0], default=str))

    body = "\n".join(json_lines)
    s3 = boto3.client("s3")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H")
    key = f"postgres/postgres_{timestamp}.json"
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"), ContentType="application/json")
    
    return {"bucket": bucket, "key": key, "records": len(json_lines)}


def main() -> None:
    mode = os.getenv("MODE", "seed_and_export")  # seed | export | seed_and_export

    host = get_env("DB_HOST")
    port = int(get_env("DB_PORT", "5432"))
    user = get_env("DB_USER")
    password = get_env("DB_PASSWORD")
    database = get_env("DB_NAME")

    s3_bucket = os.getenv("S3_BUCKET")
    s3_prefix = os.getenv("S3_PREFIX", "postgres/ingredientes")
    num_rows = int(os.getenv("FAKE_COUNT", "20000"))

    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database)

    if mode in ("seed", "seed_and_export"):
        inserted = seed_postgres(conn, num_rows)
        print(f"Seeded PostgreSQL: inserted {inserted} rows")

    if mode in ("export", "seed_and_export"):
        if not s3_bucket:
            raise RuntimeError("S3_BUCKET is required for export")
        result = export_to_s3(conn, s3_bucket, s3_prefix)
        print(f"Exported to s3://{result['bucket']}/{result['key']} ({result['records']} records)")

    conn.close()


if __name__ == "__main__":
    main()


