-- One-time seed for PostgreSQL: 20k ingredientes
-- Usage example:
--   psql "host=127.0.0.1 port=8010 dbname=menu user=postgres password=utec" -f seed_postgres.sql

CREATE TABLE IF NOT EXISTS ingredientes (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT,
  categoria TEXT,
  unidad TEXT,
  stockActual INT,
  stockMinimo INT,
  precioUnitario NUMERIC(10,2),
  activo BOOLEAN,
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);

INSERT INTO ingredientes (nombre,categoria,unidad,stockActual,stockMinimo,precioUnitario,activo,createdAt,updatedAt)
SELECT
  (ARRAY['Salmón','Atún','Pollo','Carne','Huevo','Lechuga','Tomate','Cebolla','Ajo','Perejil','Sal','Pimienta','Aceite','Vinagre','Salsa','Queso','Leche','Yogurt','Mantequilla','Crema','Arroz','Trigo','Avena','Quinoa','Cebada'])[1+floor(random()*25)] || ' ' || g as nombre,
  (ARRAY['Proteína','Vegetal','Condimento','Lácteo','Cereal'])[1+floor(random()*5)] as categoria,
  (ARRAY['kg','g','l','ml','unidad'])[1+floor(random()*5)] as unidad,
  1+floor(random()*1000)::int as stockActual,
  1+floor(random()*100)::int as stockMinimo,
  round((random()*100+1)::numeric,2) as precioUnitario,
  (random()>0.1) as activo,
  NOW() - (random()*interval '365 days') as createdAt,
  NOW() as updatedAt
FROM generate_series(1,20000) g;


