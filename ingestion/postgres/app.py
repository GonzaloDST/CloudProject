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
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ingredientes (
          id BIGSERIAL PRIMARY KEY,
          nombre TEXT,
          categoria TEXT,
          unidad TEXT,
          stockActual INT,
          stockMinimo INT,
          precioUnitario NUMERIC(10,2),
          activo BOOLEAN,
          createdAt TIMESTAMP,
          updatedAt TIMESTAMP
        );
        """
    )


def generate_fake_rows(num_rows: int) -> list[tuple]:
    categorias = ["Proteína", "Vegetal", "Condimento", "Lácteo", "Cereal"]
    unidades = ["kg", "g", "l", "ml", "unidad"]
    nombres = [
        "Salmón", "Atún", "Pollo", "Carne", "Huevo",
        "Lechuga", "Tomate", "Cebolla", "Ajo", "Perejil",
        "Sal", "Pimienta", "Aceite", "Vinagre", "Salsa",
        "Queso", "Leche", "Yogurt", "Mantequilla", "Crema",
        "Arroz", "Trigo", "Avena", "Quinoa", "Cebada",
    ]

    rows: list[tuple] = []
    for i in range(1, num_rows + 1):
        nombre = random.choice(nombres)
        categoria = random.choice(categorias)
        unidad = random.choice(unidades)
        stock_actual = random.randint(1, 1000)
        stock_minimo = max(1, int(stock_actual * 0.1))
        precio_unitario = round(random.random() * 100 + 1, 2)
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
        rows.append(
            (
                f"{nombre} {i}",
                categoria,
                unidad,
                stock_actual,
                stock_minimo,
                precio_unitario,
                random.random() > 0.1,
                created_at,
                datetime.utcnow(),
            )
        )
    return rows


def seed_postgres(conn, num_rows: int) -> int:
    with conn.cursor() as cur:
        ensure_table(cur)
        cur.execute("DELETE FROM ingredientes")
        rows = generate_fake_rows(num_rows)
        args_str = ",".join(cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", r).decode("utf-8") for r in rows)
        cur.execute(
            "INSERT INTO ingredientes (nombre,categoria,unidad,stockActual,stockMinimo,precioUnitario,activo,createdAt,updatedAt) VALUES "
            + args_str
        )
    conn.commit()
    return len(rows)


def export_to_s3(conn, bucket: str, key_prefix: str) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT row_to_json(t) FROM (SELECT * FROM ingredientes) t")
        rows = [r[0] for r in cur.fetchall()]

    body = json.dumps(rows, default=str)
    s3 = boto3.client("s3")
    timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
    key = f"{key_prefix}/{timestamp}/data.json"
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"), ContentType="application/json")
    return {"bucket": bucket, "key": key, "records": len(rows)}


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


