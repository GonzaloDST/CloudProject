#!/usr/bin/env bash
set -euo pipefail

# One-time seed for MongoDB: 20k ingredientes
# Usage:
#   MONGO_URI="mongodb://172.31.17.96:27017/inventory" ./seed_mongo.sh

: "${MONGO_URI:=mongodb://172.31.17.96:27017/inventory}"

echo "Seeding MongoDB once at ${MONGO_URI}..."

mongosh "${MONGO_URI}" --eval '
db.ingredientes.deleteMany({});
const categorias=["Proteína","Vegetal","Condimento","Lácteo","Cereal"];
const unidades=["kg","g","l","ml","unidad"];
const nombres=["Salmón","Atún","Pollo","Carne","Huevo","Lechuga","Tomate","Cebolla","Ajo","Perejil","Sal","Pimienta","Aceite","Vinagre","Salsa","Queso","Leche","Yogurt","Mantequilla","Crema","Arroz","Trigo","Avena","Quinoa","Cebada"];
let batch=[];
for (let i=1;i<=20000;i++){
  const doc={
    nombre: `${nombres[Math.floor(Math.random()*nombres.length)]} ${i}`,
    categoria: categorias[Math.floor(Math.random()*categorias.length)],
    unidad: unidades[Math.floor(Math.random()*unidades.length)],
    stockActual: Math.floor(Math.random()*1000)+1,
    stockMinimo: Math.floor(Math.random()*100)+1,
    precioUnitario: Math.round((Math.random()*100+1)*100)/100,
    activo: Math.random()>0.1,
    createdAt: new Date(Date.now()-Math.random()*31536000000),
    updatedAt: new Date()
  };
  batch.push(doc);
  if (batch.length===1000){ db.ingredientes.insertMany(batch); batch=[]; }
}
if (batch.length) db.ingredientes.insertMany(batch);
print("OK 20k");
'

echo "MongoDB seed completed."


