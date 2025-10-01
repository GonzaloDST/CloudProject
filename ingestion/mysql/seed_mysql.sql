-- One-time seed for MySQL: 20k ingredientes
-- Usage example:
--   mysql -h 172.31.17.96 -P 8005 -u utecino -putec -D maki_orders < seed_mysql.sql

CREATE TABLE IF NOT EXISTS ingredientes (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(100),
  categoria VARCHAR(50),
  unidad VARCHAR(10),
  stockActual INT,
  stockMinimo INT,
  precioUnitario DECIMAL(10,2),
  activo BOOLEAN,
  createdAt DATETIME,
  updatedAt DATETIME
);

WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n < 20000
)
INSERT INTO ingredientes (nombre,categoria,unidad,stockActual,stockMinimo,precioUnitario,activo,createdAt,updatedAt)
SELECT
  CONCAT(ELT(FLOOR(1+RAND()*25),
    "Salmón","Atún","Pollo","Carne","Huevo","Lechuga","Tomate","Cebolla","Ajo","Perejil","Sal","Pimienta","Aceite","Vinagre","Salsa","Queso","Leche","Yogurt","Mantequilla","Crema","Arroz","Trigo","Avena","Quinoa","Cebada"), " ", n) as nombre,
  ELT(FLOOR(1+RAND()*5),"Proteína","Vegetal","Condimento","Lácteo","Cereal") as categoria,
  ELT(FLOOR(1+RAND()*5),"kg","g","l","ml","unidad") as unidad,
  FLOOR(RAND()*1000)+1 as stockActual,
  FLOOR(RAND()*100)+1 as stockMinimo,
  ROUND(RAND()*100+1,2) as precioUnitario,
  IF(RAND()>0.1, TRUE, FALSE) as activo,
  FROM_UNIXTIME(UNIX_TIMESTAMP() - FLOOR(RAND()*31536000)) as createdAt,
  NOW() as updatedAt
FROM seq;


