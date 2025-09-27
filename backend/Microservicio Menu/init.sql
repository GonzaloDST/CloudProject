-- Crear tabla de ingredientes
CREATE TABLE IF NOT EXISTS ingrediente (
                                           id SERIAL PRIMARY KEY,
                                           nombre VARCHAR(100) NOT NULL,
    stock INT NOT NULL
    );

-- Crear tabla de makis
CREATE TABLE IF NOT EXISTS maki (
                                    id SERIAL PRIMARY KEY,
                                    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10,2) NOT NULL
    );

-- Crear tabla intermedia para la relación muchos a muchos
CREATE TABLE IF NOT EXISTS maki_ingrediente (
                                                maki_id INT NOT NULL,
                                                ingrediente_id INT NOT NULL,
                                                PRIMARY KEY (maki_id, ingrediente_id),
    FOREIGN KEY (maki_id) REFERENCES maki(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingrediente(id) ON DELETE CASCADE
    );

-- ==========================
-- Insertar ingredientes
-- ==========================
INSERT INTO ingrediente (nombre, stock) VALUES
                                            ('Salmón', 100),
                                            ('Palta', 50),
                                            ('Queso crema', 80),
                                            ('Pollo', 60),
                                            ('Tampico', 40);

-- ==========================
-- Insertar makis
-- ==========================
INSERT INTO maki (nombre, descripcion, precio) VALUES
                                                   ('California Roll', 'Maki clásico con palta, cangrejo y pepino', 18.50),
                                                   ('Acevichado', 'Maki relleno de pescado y cubierto con salsa acevichada', 22.00),
                                                   ('Philadelphia Roll', 'Maki con salmón y queso crema', 20.00);

-- ==========================
-- Relacionar makis con ingredientes
-- ==========================
-- California Roll -> Palta, Tampico
INSERT INTO maki_ingrediente (maki_id, ingrediente_id) VALUES (1, 2), (1, 5);

-- Acevichado -> Pescado (Pollo como placeholder), Palta
INSERT INTO maki_ingrediente (maki_id, ingrediente_id) VALUES (2, 4), (2, 2);

-- Philadelphia Roll -> Salmón, Queso crema
INSERT INTO maki_ingrediente (maki_id, ingrediente_id) VALUES (3, 1), (3, 3);
