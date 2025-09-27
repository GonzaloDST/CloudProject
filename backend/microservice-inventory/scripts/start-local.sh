#!/bin/bash

# Script para levantar el microservicio con MongoDB local

echo "🚀 Iniciando Microservicio de Inventario con MongoDB local..."

# Crear red si no existe
docker network create inventory-network 2>/dev/null || true

# Levantar con perfil local (incluye MongoDB local)
echo "🔨 Construyendo y levantando servicios..."
docker-compose --profile local up -d --build

echo "✅ Servicios iniciados:"
echo "   📡 Microservicio: http://localhost:4000"
echo "   🗄️  MongoDB: localhost:27017"
echo ""
echo "📊 Ver logs: docker-compose logs -f"
echo "🛑 Detener: docker-compose down"
