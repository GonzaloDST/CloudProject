# 🚀 Configuración para AWS MongoDB

## 📋 **Opciones de MongoDB en AWS**

### **Opción 1: Amazon DocumentDB (Recomendado)**
```bash
# URL de conexión típica:
MONGODB_URI=mongodb://username:password@your-cluster.cluster-xxxxx.us-east-1.docdb.amazonaws.com:27017/inventory
```

### **Opción 2: MongoDB Atlas**
```bash
# URL de conexión típica:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/inventory
```

### **Opción 3: EC2 con MongoDB**
```bash
# URL de conexión típica:
MONGODB_URI=mongodb://username:password@your-ec2-ip:27017/inventory
```

## 🔧 **Configuración Paso a Paso**

### **1. Crear archivo .env**
```bash
# Copiar el archivo de ejemplo
cp env.example .env

# Editar con tus datos
nano .env
```

### **2. Configurar variables en .env**
```env
# Puerto del microservicio
PORT=4000

# URL de tu MongoDB en AWS
MONGODB_URI=mongodb://username:password@your-aws-host:27017/inventory

# Base de datos
MONGO_INITDB_DATABASE=inventory
```

### **3. Comandos para levantar**

#### **Para AWS MongoDB:**
```bash
# Hacer ejecutable el script
chmod +x scripts/start-aws.sh

# Ejecutar
./scripts/start-aws.sh
```

#### **Para MongoDB local (desarrollo):**
```bash
# Hacer ejecutable el script
chmod +x scripts/start-local.sh

# Ejecutar
./scripts/start-local.sh
```

#### **Comandos manuales:**
```bash
# Crear red
docker network create inventory-network

# Construir imagen
docker-compose build

# Levantar solo el microservicio (sin MongoDB local)
docker-compose up -d inventory-service

# Ver logs
docker-compose logs -f inventory-service

# Detener
docker-compose down
```

## 🐳 **Docker Commands**

### **Construir imagen:**
```bash
docker build -t microservice-inventory .
```

### **Ejecutar con variables de entorno:**
```bash
docker run -d \
  --name inventory-service \
  --network inventory-network \
  -p 4000:4000 \
  -e PORT=4000 \
  -e MONGODB_URI="mongodb://username:password@your-aws-host:27017/inventory" \
  microservice-inventory
```

### **Con archivo .env:**
```bash
docker run -d \
  --name inventory-service \
  --network inventory-network \
  -p 4000:4000 \
  --env-file .env \
  microservice-inventory
```

## 🔍 **Verificación**

### **Verificar conexión:**
```bash
# Ver logs del servicio
docker-compose logs inventory-service

# Probar endpoint
curl http://localhost:4000/ingredientes
```

### **Verificar MongoDB:**
```bash
# Conectar a MongoDB (si es local)
docker exec -it $(docker ps -q --filter "name=mongo") mongosh

# Verificar base de datos
use inventory
show collections
```

## 🛠️ **Troubleshooting**

### **Error de conexión a MongoDB:**
1. Verificar que la URL de MongoDB sea correcta
2. Verificar que el usuario y contraseña sean correctos
3. Verificar que la red permita conexiones desde tu IP
4. Verificar que el puerto esté abierto

### **Error de red:**
```bash
# Crear red manualmente
docker network create inventory-network

# Verificar redes
docker network ls
```

### **Ver logs detallados:**
```bash
# Logs del microservicio
docker-compose logs -f inventory-service

# Logs de MongoDB (si es local)
docker-compose logs -f mongo-local
```

## 📊 **Monitoreo**

### **Estado de contenedores:**
```bash
docker-compose ps
```

### **Uso de recursos:**
```bash
docker stats
```

### **Logs en tiempo real:**
```bash
docker-compose logs -f
```
