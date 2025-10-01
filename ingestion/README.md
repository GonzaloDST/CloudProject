## Ingesta: seed de datos y export batch a S3

### 1) Seed de datos fake (20k) - ejecutar una sola vez

MongoDB:

```bash
MONGO_URI="mongodb://172.31.17.96:27017/inventory" bash scripts/seed_mongo.sh
```

MySQL (8+):

```bash
mysql -h 172.31.17.96 -P 8005 -u utecino -putec -D maki_orders < mysql/seed_mysql.sql
```

PostgreSQL (Docker rápido si no lo tienes):

```bash
docker run -d --name pg_c -e POSTGRES_PASSWORD=utec -e POSTGRES_USER=postgres -e POSTGRES_DB=menu -p 8010:5432 postgres:15
psql "host=127.0.0.1 port=8010 dbname=menu user=postgres password=utec" -f postgres/seed_postgres.sql
```

### 2) Export batch a S3 (no tiempo real)

Script unificado `scripts/ingesta.sh` exporta MongoDB, MySQL y PostgreSQL a rutas con timestamp y sube a S3.

Requisitos: tener `awscli`, `mongosh`, `mysql` y `psql` instalados y en PATH.

Variables:

- `S3_BUCKET` (obligatorio)
- `MONGO_URI` (opcional, default `mongodb://172.31.17.96:27017/inventory`)
- `MYSQL_HOST` `MYSQL_PORT` `MYSQL_USER` `MYSQL_PASSWORD` `MYSQL_DB`
- `PG_HOST` `PG_PORT` `PG_DB` `PG_USER` `PG_PASSWORD`

Ejemplo manual:

```bash
export S3_BUCKET=my-bucket
bash scripts/ingesta.sh
```

Cron cada hora en Linux:

```bash
crontab -e
# añadir línea:
0 * * * * S3_BUCKET=my-bucket /bin/bash /path/to/ingestion/scripts/ingesta.sh >> /var/log/ingesta.log 2>&1
```

### 3) Glue y Athena (una vez)

Glue: crear `inventory_db` y 3 crawlers a:

- s3://<bucket>/mongo/ingredientes/
- s3://<bucket>/mysql/ingredientes/
- s3://<bucket>/postgres/ingredientes/

Athena (luego de correr el crawler):

```sql
SELECT COUNT(*) FROM mongo_ingredientes;
SELECT COUNT(*) FROM mysql_ingredientes;
SELECT COUNT(*) FROM postgres_ingredientes;
```


