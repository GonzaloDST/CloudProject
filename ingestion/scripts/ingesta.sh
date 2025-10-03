#!/usr/bin/env bash
set -euo pipefail

# Unified batch export to S3 (MongoDB, MySQL, PostgreSQL)
# Runs once; intended for cron hourly scheduling outside real-time needs.

# Required env vars:
#   S3_BUCKET            e.g. my-bucket
# Optional overrides with sensible defaults:
#   MONGO_URI            default mongodb://172.31.17.96:27017/inventory
#   MYSQL_HOST           default 172.31.17.96
#   MYSQL_PORT           default 8005
#   MYSQL_USER           default utecino
#   MYSQL_PASSWORD       default utec
#   MYSQL_DB             default maki_orders
#   PG_HOST              default 127.0.0.1
#   PG_PORT              default 8010
#   PG_DB                default menu
#   PG_USER              default postgres
#   PG_PASSWORD          default utec

timestamp_path() {
  date +%Y%m%d%H
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required env var: $name" >&2
    exit 1
  fi
}

require_env S3_BUCKET

: "${MONGO_URI:=mongodb://172.31.17.96:27017/inventory}"
: "${MYSQL_HOST:=172.31.17.96}"
: "${MYSQL_PORT:=8005}"
: "${MYSQL_USER:=utecino}"
: "${MYSQL_PASSWORD:=utec}"
: "${MYSQL_DB:=maki_orders}"
: "${PG_HOST:=127.0.0.1}"
: "${PG_PORT:=8010}"
: "${PG_DB:=menu}"
: "${PG_USER:=postgres}"
: "${PG_PASSWORD:=utec}"

OUT_DIR="/tmp"
TS=$(timestamp_path)

echo "Exporting MongoDB ingredientes..."
MONGO_OUT="$OUT_DIR/mongo_ingredientes.json"
mongosh "$MONGO_URI" --eval 'config.set("displayBatchSize", 50000); db.ingredientes.find({}).forEach(doc => print(JSON.stringify(doc)))' --quiet 2>/dev/null > "$MONGO_OUT"
aws s3 cp "$MONGO_OUT" "s3://$S3_BUCKET/mongo/mongo_$TS.json"

echo "Exporting MySQL data (users, products, orders)..."
MYSQL_OUT="$OUT_DIR/mysql_data.json"
# Exportar cada tabla por separado en formato one-line JSON
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -D "$MYSQL_DB" -B -N \
  -e "SELECT JSON_OBJECT('id',id,'name',name,'email',email,'phone_number',phone_number,'address',address,'created_at',created_at) FROM users;" > "$MYSQL_OUT"
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -D "$MYSQL_DB" -B -N \
  -e "SELECT JSON_OBJECT('id',id,'name',name,'price',price,'calories',calories,'created_at',created_at) FROM products;" >> "$MYSQL_OUT"
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -D "$MYSQL_DB" -B -N \
  -e "SELECT JSON_OBJECT('id',id,'user_id',user_id,'product_id',product_id,'status',status,'order_date',order_date,'total_price',total_price,'payment_method',payment_method) FROM orders;" >> "$MYSQL_OUT"
aws s3 cp "$MYSQL_OUT" "s3://$S3_BUCKET/mysql/mysql_$TS.json"

echo "Exporting PostgreSQL data (ingrediente, maki, maki_ingrediente)..."
PG_OUT="$OUT_DIR/pg_data.json"
# Exportar cada tabla por separado en formato one-line JSON
PGPASSWORD="$PG_PASSWORD" psql "host=$PG_HOST port=$PG_PORT dbname=$PG_DB user=$PG_USER" -t -c "SELECT row_to_json(t) FROM (SELECT * FROM ingrediente) t;" > "$PG_OUT"
PGPASSWORD="$PG_PASSWORD" psql "host=$PG_HOST port=$PG_PORT dbname=$PG_DB user=$PG_USER" -t -c "SELECT row_to_json(t) FROM (SELECT * FROM maki) t;" >> "$PG_OUT"
PGPASSWORD="$PG_PASSWORD" psql "host=$PG_HOST port=$PG_PORT dbname=$PG_DB user=$PG_USER" -t -c "SELECT row_to_json(t) FROM (SELECT * FROM maki_ingrediente) t;" >> "$PG_OUT"
aws s3 cp "$PG_OUT" "s3://$S3_BUCKET/postgres/postgres_$TS.json"

echo "All exports uploaded to s3://$S3_BUCKET/"
echo "Files created:"
echo "  - s3://$S3_BUCKET/mongo/mongo_$TS.json"
echo "  - s3://$S3_BUCKET/mysql/mysql_$TS.json" 
echo "  - s3://$S3_BUCKET/postgres/postgres_$TS.json"


