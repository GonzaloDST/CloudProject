# Queries para usuarios
USER_QUERIES = {
    "create": """
        INSERT INTO users (name, email, phone_number, address) 
        VALUES (%s, %s, %s, %s)
    """,
    "get_all": "SELECT * FROM users",
    "get_by_id": "SELECT * FROM users WHERE id = %s",
    "get_by_email": "SELECT * FROM users WHERE email = %s",
    "update": """
        UPDATE users SET name = %s, email = %s, phone_number = %s, address = %s 
        WHERE id = %s
    """,
    "delete": "DELETE FROM users WHERE id = %s"
}

# Queries para productos
PRODUCT_QUERIES = {
    "create": """
        INSERT INTO products (name, price, calories) 
        VALUES (%s, %s, %s)
    """,
    "get_all": "SELECT * FROM products",
    "get_by_id": "SELECT * FROM products WHERE id = %s",
    "update": """
        UPDATE products SET name = %s, price = %s, calories = %s 
        WHERE id = %s
    """,
    "delete": "DELETE FROM products WHERE id = %s"
}

# Queries para pedidos
ORDER_QUERIES = {
    "create": """
        INSERT INTO orders (user_id, product_id, status, total_price, payment_method) 
        VALUES (%s, %s, %s, %s, %s)
    """,
    "get_all": """
        SELECT o.*, u.name as user_name, p.name as product_name 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
    """,
    "get_by_id": """
        SELECT o.*, u.name as user_name, p.name as product_name 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        WHERE o.id = %s
    """,
    "get_by_user": """
        SELECT o.*, u.name as user_name, p.name as product_name 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        WHERE o.user_id = %s
    """,
    "get_by_status": """
        SELECT o.*, u.name as user_name, p.name as product_name 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        WHERE o.status = %s
    """,
    "update": """
        UPDATE orders SET status = %s, total_price = %s, payment_method = %s 
        WHERE id = %s
    """,
    "delete": "DELETE FROM orders WHERE id = %s"
}