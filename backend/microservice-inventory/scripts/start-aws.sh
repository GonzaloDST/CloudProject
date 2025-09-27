#!/bin/bash

# Script para levantar el microservicio con MongoDB en AWS

echo "🚀 Iniciando Microservicio de Inventario con MongoDB en AWS..."

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "📝 Copia env.example a .env y configura las variables:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Cargar variables de entorno
source .env

# Verificar que MONGODB_URI esté configurada
if [ -z "$MONGODB_URI" ]; then
    echo "❌ Error: MONGODB_URI no está configurada en .env"
    exit 1
fi

echo "📡 Conectando a MongoDB: ${MONGODB_URI}"

# Crear red si no existe
docker network create inventory-network 2>/dev/null || true

# Construir y levantar el servicio
echo "🔨 Construyendo imagen..."
docker-compose build inventory-service

echo "🚀 Levantando servicio..."
docker-compose up -d inventory-service

echo "✅ Microservicio iniciado en puerto ${PORT:-4000}"
echo "📊 Ver logs: docker-compose logs -f inventory-service"
echo "🛑 Detener: docker-compose down"
