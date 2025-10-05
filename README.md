# CloudProject

# 🥢 Makis Cloud Project

Proyecto parcial sobre una tienda de makis construido con **microservicios** (FastAPI, NestJS, Spring Boot), **persistencia poliglota** (MySQL, MongoDB, PostgreSQL), **API Gateway + Load Balancer** y un **pipeline de datos** a **S3 → Glue → Athena**.

## Arquitectura

- **3 microservicios:**
  - Orders API (FastAPI + MySQL)
  - Inventory API (NestJS + MongoDB)
  - Menu API (Spring Boot + PostgreSQL)
- **API Gateway (HTTP API)** frente a un **Load Balancer**.
- **Pipeline de datos:** exportadores → **S3** → **Glue** (catálogo) → **Athena** (consultas).

---

## Servicios

| Servicio         | Tecnología  | Base de datos | Puerto | Endpoints principales                                  |
|------------------|-------------|---------------|--------|--------------------------------------------------------|
| Orders API       | FastAPI     | MySQL         | 8000   | `/api/orders`, `/api/users`, `/api/products`          |
| Inventory API    | NestJS      | MongoDB       | 4000   | `/api/ingredientes`                                   |
| Menu API         | Spring Boot | PostgreSQL    | 8080   | `/api/makis`, `/api/ingredientes-spring`              |

---

## Prerrequisitos

- Docker y docker compose
- LB
- Credenciales AWS con permisos **S3, Glue, Athena**

---

## Despliegue Rápido

### MongoDB + Inventario (NestJS)

```bash
# MongoDB
docker run -d --rm --name mongo_c \
  --network inventory-network \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  mongo:latest

# Build NestJS
docker build -t microservice-inventory .

# Inventory API (NestJS)
docker run -d --rm --name inventory-service \
  --network micro-net \
  -e PORT=4000 \
  -e MONGODB_URI="mongodb://172.31.17.96:27017/inventory" \
  -p 4000:4000 \
  microservice-inventory
```

---

### MySQL + Órdenes (FastAPI)

```bash
# MySQL
docker run -d --rm --name maki_mysql \
  -p 8005:3306 \
  -e MYSQL_ROOT_PASSWORD=utec \
  -e MYSQL_DATABASE=maki_orders \
  -e MYSQL_USER=utecino \
  -e MYSQL_PASSWORD=utec \
  -v mysql_data:/var/lib/mysql \
  -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql \
  mysql:8.0

# Build FastAPI
docker build -t microservice1-api .

# Orders API (FastAPI)
docker run -d --rm --name maki_api \
  --network micro-net \
  -e DB_HOST=172.31.17.96 \
  -e DB_PORT=8005 \
  -e DB_USER=utecino \
  -e DB_PASSWORD=utec \
  -e DB_NAME=maki_orders \
  -p 8000:8000 \
  microservice1-api
```

---

### PostgreSQL + Menú (Spring-boot)

```bash
# PostgreSQL
docker run -d --rm --name pg_menu \
  -p 8010:5432 \
  -e POSTGRES_DB=menu \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=utec \
  -v pg_data:/var/lib/postgresql/data \
  postgres:latest

# Build Spring Boot
docker build -t microservicio-menu .

# Menu API (Spring Boot)
docker run -d --rm --name menu_service \
  --network micro-net \
  -e DB_HOST=172.31.17.96 \
  -e DB_PORT=8010 \
  -e DB_USER=postgres \
  -e DB_PASSWORD=utec \
  -e DB_NAME=menu \
  -p 8080:8080 \
  microservicio-menu
```

---

### Red Docker y Orquestador

```bash
# Red para descubrimiento de servicios
docker network create micro-net

# Conectar servicios (si se iniciaron antes)
docker network connect micro-net maki_api
docker network connect micro-net inventory-service
docker network connect micro-net menu_service

# Orquestador
docker build -t orchestrador .
docker run -d --rm --name orchestrador \
  --network micro-net \
  -p 5000:5000 \
  orchestrador
```

---

## API Gateway

> **API ID:** `jiql4i2xy4`  
> **Base URL:** `https://jiql4i2xy4.execute-api.us-east-1.amazonaws.com/prod`

### Integraciones hacia el Load Balancer

```bash
# Spring Boot (Makis) - puerto 8080
aws apigatewayv2 create-integration \
  --api-id jiql4i2xy4 \
  --integration-type HTTP_PROXY \
  --integration-method ANY \
  --integration-uri "http://lb-prod-55563764.us-east-1.elb.amazonaws.com:8080/{proxy}" \
  --payload-format-version "1.0"

# NestJS (Inventario) - puerto 4000
aws apigatewayv2 create-integration \
  --api-id jiql4i2xy4 \
  --integration-type HTTP_PROXY \
  --integration-method ANY \
  --integration-uri "http://lb-prod-55563764.us-east-1.elb.amazonaws.com:4000/{proxy}" \
  --payload-format-version "1.0"

# FastAPI (Órdenes) - puerto 8000
aws apigatewayv2 create-integration \
  --api-id jiql4i2xy4 \
  --integration-type HTTP_PROXY \
  --integration-method ANY \
  --integration-uri "http://lb-prod-55563764.us-east-1.elb.amazonaws.com:8000/{proxy}" \
  --payload-format-version "1.0"

# Orquestador (opcional, puerto 5000)
aws apigatewayv2 create-integration \
  --api-id jiql4i2xy4 \
  --integration-type HTTP_PROXY \
  --integration-method ANY \
  --integration-uri "http://lb-prod-55563764.us-east-1.elb.amazonaws.com:5000/{proxy}" \
  --payload-format-version "1.0"
```

### Rutas, Stage y CORS

```bash
# Ejemplos de rutas (usa tus IntegrationIds devueltos)
aws apigatewayv2 create-route \
  --api-id jiql4i2xy4 \
  --route-key "ANY /api/makis/{proxy+}" \
  --target "integrations/INTEG_8080"

aws apigatewayv2 create-route \
  --api-id jiql4i2xy4 \
  --route-key "ANY /api/ingredientes/{proxy+}" \
  --target "integrations/INTEG_4000"

aws apigatewayv2 create-route \
  --api-id jiql4i2xy4 \
  --route-key "ANY /api/orders/{proxy+}" \
  --target "integrations/INTEG_8000"

# Ruta catch-all para orquestador (opcional)
aws apigatewayv2 create-route \
  --api-id jiql4i2xy4 \
  --route-key "ANY /{proxy+}" \
  --target "integrations/INTEG_5000"

# Stage
aws apigatewayv2 create-stage \
  --api-id jiql4i2xy4 \
  --stage-name "prod" \
  --auto-deploy

# CORS
aws apigatewayv2 update-api \
  --api-id jiql4i2xy4 \
  --cors-configuration '{
    "AllowOrigins": ["*"],
    "AllowMethods": ["GET","POST","PUT","DELETE","OPTIONS"],
    "AllowHeaders": ["Content-Type","Authorization"],
    "MaxAge": 300
  }'
```

### Base URL y ejemplos cURL

```bash
BASE="https://jiql4i2xy4.execute-api.us-east-1.amazonaws.com/prod"

# Índice orquestador
curl -i "$BASE/"

# Órdenes (FastAPI)
curl -i "$BASE/api/orders"
curl -i "$BASE/api/orders/1"

# Inventario (NestJS)
curl -i "$BASE/api/ingredientes"

# Menú (Spring Boot)
curl -i "$BASE/api/makis"
curl -i "$BASE/api/ingredientes-spring"
```

---

## Ingesta de Datos a S3

### Variables de entorno y ejecución

```bash
# Exportar variables
export S3_BUCKET=bucket-mv-ingesta
export MONGO_URI="mongodb://172.31.17.96:27017/inventory"
export MYSQL_HOST=172.31.17.96
export MYSQL_PORT=8005
export MYSQL_USER=utecino
export MYSQL_PASSWORD=utec
export MYSQL_DB=maki_orders
export PG_HOST=172.31.17.96
export PG_PORT=8010
export PG_DB=menu
export PG_USER=postgres
export PG_PASSWORD=utec

# Ejecutar script
bash ./ingesta.sh
```

### Ingesta en contenedores (opcional)

```bash
# Exportador Mongo
docker run --rm \
  -e MONGO_URI="$MONGO_URI" \
  -e MONGO_DB="$MONGO_DB" \
  -e MONGO_COLLECTION="$MONGO_COLLECTION" \
  -e S3_BUCKET="$S3_BUCKET" \
  -e MODE=export \
  -v "$AWS_MOUNT":/root/.aws:ro -e AWS_PROFILE=default \
  ingesta-mongo:latest

# Exportador MySQL
docker run --rm \
  -e DB_HOST=172.31.17.96 -e DB_PORT=8005 \
  -e DB_USER=utecino -e DB_PASSWORD=utec \
  -e DB_NAME=maki_orders \
  -e S3_BUCKET=bucket-mv-ingesta \
  -e MODE=export \
  -v $HOME/.aws:/root/.aws:ro -e AWS_PROFILE=default \
  ingesta-mysql:latest

# Exportador PostgreSQL
docker run --rm \
  -e DB_HOST=172.31.17.96 -e DB_PORT=8010 \
  -e DB_USER=postgres -e DB_PASSWORD=utec \
  -e DB_NAME=menu \
  -e S3_BUCKET=bucket-mv-ingesta \
  -e MODE=export \
  -v $HOME/.aws:/root/.aws:ro -e AWS_PROFILE=default \
  ingesta-postgres:latest
```

---

## Glue y Athena

### Creación de crawlers

```bash
aws glue create-crawler \
  --name mongo-crawler \
  --role arn:aws:iam::938209751559:role/LabRole \
  --database-name inventory_db \
  --targets '{"S3Targets":[{"Path":"s3://bucket-mv-ingesta/mongo/"}]}'

aws glue create-crawler \
  --name mysql-crawler \
  --role arn:aws:iam::938209751559:role/LabRole \
  --database-name inventory_db \
  --targets '{"S3Targets":[{"Path":"s3://bucket-mv-ingesta/mysql/"}]}'

aws glue create-crawler \
  --name postgres-crawler \
  --role arn:aws:iam::938209751559:role/LabRole \
  --database-name inventory_db \
  --targets '{"S3Targets":[{"Path":"s3://bucket-mv-ingesta/postgres/"}]}'

# Iniciar crawlers
aws glue start-crawler --name mongo-crawler
aws glue start-crawler --name mysql-crawler
aws glue start-crawler --name postgres-crawler
```

---

## Resumen de Endpoints

**Orders API (FastAPI — 8000 / MySQL)**  
- `GET /api/orders`, `POST /api/orders`, `GET /api/orders/{id}`, `PUT /api/orders/{id}`, `DELETE /api/orders/{id}`  
- `GET /api/users`, `POST /api/users`, `GET /api/users/{id}`, `PUT /api/users/{id}`, `DELETE /api/users/{id}`  
- `GET /api/products`, `POST /api/products`, `GET /api/products/{id}`, `PUT /api/products/{id}`, `DELETE /api/products/{id}`

**Inventory API (NestJS — 4000 / MongoDB)**  
- `GET /api/ingredientes`, `POST /api/ingredientes`, `GET /api/ingredientes/{id}`, `PUT /api/ingredientes/{id}`, `DELETE /api/ingredientes/{id}`

**Menu API (Spring Boot — 8080 / PostgreSQL)**  
- `GET /api/makis`, `POST /api/makis`, `GET /api/makis/{id}`, `PUT /api/makis/{id}`, `DELETE /api/makis/{id}`  
- `GET /api/ingredientes-spring`, `POST /api/ingredientes-spring`, `GET /api/ingredientes-spring/{id}`, `PUT /api/ingredientes-spring/{id}`, `DELETE /api/ingredientes-spring/{id}`


