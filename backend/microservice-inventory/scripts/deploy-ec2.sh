#!/bin/bash

# Script para desplegar en EC2 con MongoDB

echo "🚀 Desplegando Microservicio de Inventario en EC2..."

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    exit 1
fi

# Crear red si no existe
echo "📡 Creando red Docker..."
docker network create inventory-network 2>/dev/null || echo "Red ya existe"

# Crear volumen para MongoDB si no existe
echo "💾 Creando volumen para MongoDB..."
docker volume create mongo_data 2>/dev/null || echo "Volumen ya existe"

# Levantar MongoDB
echo "🗄️ Levantando MongoDB..."
docker run -d --rm --name mongo_c \
  --network inventory-network \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  mongo:latest

# Esperar a que MongoDB esté listo
echo "⏳ Esperando a que MongoDB esté listo..."
sleep 10

# Construir imagen del microservicio
echo "🔨 Construyendo imagen del microservicio..."
docker build -t microservice-inventory .

# Verificar que la imagen se construyó correctamente
if [ $? -ne 0 ]; then
    echo "❌ Error al construir la imagen"
    exit 1
fi

# Ejecutar el microservicio
echo "🚀 Levantando microservicio..."
docker run -d --rm --name inventory-service \
  --network inventory-network \
  -e PORT=4000 \
  -e MONGODB_URI="mongodb://mongo_c:27017/inventory" \
  -p 4000:4000 \
  microservice-inventory

# Esperar a que el microservicio esté listo
echo "⏳ Esperando a que el microservicio esté listo..."
sleep 15

# Verificar que todo esté funcionando
echo "🔍 Verificando servicios..."
docker ps

# Probar la API
echo "🧪 Probando API..."
curl -f http://localhost:4000/ingredientes > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ ¡Microservicio desplegado exitosamente!"
    echo "📡 API disponible en: http://localhost:4000"
    echo "🗄️ MongoDB disponible en: localhost:27017"
    echo ""
    echo "📊 Comandos útiles:"
    echo "   Ver logs: docker logs -f inventory-service"
    echo "   Detener: docker stop inventory-service mongo_c"
    echo "   Estado: docker ps"
else
    echo "❌ Error: La API no responde correctamente"
    echo "📋 Ver logs: docker logs inventory-service"
    exit 1
fi
