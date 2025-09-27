# Usar Node.js 18 Alpine como imagen base
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Compilar la aplicación
RUN npm run build

# Exponer puerto 4000
EXPOSE 4000

# Variables de entorno por defecto
ENV PORT=4000
ENV MONGODB_URI=mongodb://mongo:27017/inventory

# Comando para ejecutar la aplicación
CMD ["npm", "run", "start:prod"]
