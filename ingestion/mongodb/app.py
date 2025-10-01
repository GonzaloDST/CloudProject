import os
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
import boto3


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def generate_fake_documents(num_docs: int) -> list[dict]:
    import random

    categorias = ["Proteína", "Vegetal", "Condimento", "Lácteo", "Cereal"]
    unidades = ["kg", "g", "l", "ml", "unidad"]
    nombres = [
        "Salmón", "Atún", "Pollo", "Carne", "Huevo",
        "Lechuga", "Tomate", "Cebolla", "Ajo", "Perejil",
        "Sal", "Pimienta", "Aceite", "Vinagre", "Salsa",
        "Queso", "Leche", "Yogurt", "Mantequilla", "Crema",
        "Arroz", "Trigo", "Avena", "Quinoa", "Cebada",
    ]

    documents: list[dict] = []
    for i in range(1, num_docs + 1):
        nombre = random.choice(nombres)
        categoria = random.choice(categorias)
        unidad = random.choice(unidades)
        stock_actual = random.randint(1, 1000)
        stock_minimo = max(1, int(stock_actual * 0.1))
        precio_unitario = round(random.random() * 100 + 1, 2)
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))

        documents.append(
            {
                "nombre": f"{nombre} {i}",
                "categoria": categoria,
                "unidad": unidad,
                "stockActual": stock_actual,
                "stockMinimo": stock_minimo,
                "precioUnitario": precio_unitario,
                "activo": random.random() > 0.1,
                "createdAt": created_at,
                "updatedAt": datetime.utcnow(),
            }
        )
    return documents


def seed_mongodb(uri: str, database: str, collection: str, num_docs: int) -> int:
    client = MongoClient(uri)
    coll = client[database][collection]
    coll.deleteMany({}) if hasattr(coll, "deleteMany") else coll.delete_many({})
    docs = generate_fake_documents(num_docs)
    result = coll.insert_many(docs)
    return len(result.inserted_ids)


def export_to_s3(uri: str, database: str, collection: str, bucket: str, key_prefix: str) -> dict:
    client = MongoClient(uri)
    coll = client[database][collection]
    data = list(coll.find())

    # Convert ObjectId and datetime to strings
    def default_serializer(o):
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return str(o)

    body = json.dumps(data, default=default_serializer)

    s3 = boto3.client("s3")
    timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
    key = f"{key_prefix}/{timestamp}/data.json"
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"), ContentType="application/json")
    return {"bucket": bucket, "key": key, "records": len(data)}


def main() -> None:
    mode = os.getenv("MODE", "seed_and_export")  # seed | export | seed_and_export

    mongo_uri = get_env("MONGO_URI", "mongodb://172.31.17.96:27017")
    mongo_db = get_env("MONGO_DB", "inventory")
    mongo_collection = get_env("MONGO_COLLECTION", "ingredientes")

    s3_bucket = os.getenv("S3_BUCKET")
    s3_prefix = os.getenv("S3_PREFIX", "mongo/ingredientes")

    num_docs = int(os.getenv("FAKE_COUNT", "20000"))

    if mode in ("seed", "seed_and_export"):
        inserted = seed_mongodb(mongo_uri, mongo_db, mongo_collection, num_docs)
        print(f"Seeded MongoDB: inserted {inserted} docs")

    if mode in ("export", "seed_and_export"):
        if not s3_bucket:
            raise RuntimeError("S3_BUCKET is required for export")
        result = export_to_s3(mongo_uri, mongo_db, mongo_collection, s3_bucket, s3_prefix)
        print(f"Exported to s3://{result['bucket']}/{result['key']} ({result['records']} records)")


if __name__ == "__main__":
    main()


