CREATE DATABASE IF NOT EXISTS maki_orders;
USE maki_orders;

-- 1. Tabla de USUARIOS
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de PRODUCTOS
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    calories INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de PEDIDOS
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    status ENUM('pending', 'confirmed', 'preparing', 'delivered', 'cancelled') DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'card', 'transfer') DEFAULT 'cash',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- =============================================================================
-- DATOS DE EJEMPLO
-- =============================================================================

-- Usuario: Gonzalo Suárez Torres
INSERT INTO users (name, email, phone_number, address) VALUES
('Gonzalo Suárez Torres', 'gonzalo.suarez@utec.edu.pe', '+51987654321', 'Jr. Medrano Silva 165');

-- Productos de sushi
INSERT INTO products (name, price, calories) VALUES
('California Roll Premium', 18.99, 320),
('Dragon Roll Especial', 22.99, 450),
('Tempura de Camarón', 16.99, 380),
('Sashimi Mixto', 24.99, 280),
('Ramen Maki Deluxe', 20.99, 520),
('Green Dragon Roll', 19.99, 410);

INSERT INTO orders (user_id, product_id, status, total_price, payment_method)
SELECT u.id, p.id, 'delivered', 18.99, 'card'
FROM users u
JOIN products p ON p.name = 'California Roll Premium'
WHERE u.email = 'gonzalo.suarez@utec.edu.pe';

INSERT INTO orders (user_id, product_id, status, total_price, payment_method)
SELECT u.id, p.id, 'preparing', 22.99, 'transfer'
FROM users u
JOIN products p ON p.name = 'Dragon Roll Especial'
WHERE u.email = 'gonzalo.suarez@utec.edu.pe';

INSERT INTO orders (user_id, product_id, status, total_price, payment_method)
SELECT u.id, p.id, 'confirmed', 16.99, 'cash'
FROM users u
JOIN products p ON p.name = 'Tempura de Camarón'
WHERE u.email = 'gonzalo.suarez@utec.edu.pe';