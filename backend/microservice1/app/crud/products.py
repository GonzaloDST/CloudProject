from mysql.connector import Error
from app.models.models import PRODUCT_QUERIES

class ProductCRUD:
    @staticmethod
    def create_product(conn, product):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(PRODUCT_QUERIES["create"], 
                         (product.name, product.price, product.calories))
            conn.commit()
            
            # Obtener el producto creado (por nombre)
            cursor.execute("SELECT * FROM products WHERE name = %s", (product.name,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def get_products(conn):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(PRODUCT_QUERIES["get_all"])
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise e

    @staticmethod
    def get_product_by_id(conn, product_id: str):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(PRODUCT_QUERIES["get_by_id"], (product_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            raise e

    @staticmethod
    def update_product(conn, product_id: str, product):
        try:
            current_product = ProductCRUD.get_product_by_id(conn, product_id)
            if not current_product:
                return None

            update_data = {
                'name': product.name or current_product['name'],
                'price': product.price or current_product['price'],
                'calories': product.calories or current_product['calories']
            }

            cursor = conn.cursor(dictionary=True)
            cursor.execute(PRODUCT_QUERIES["update"], 
                         (update_data['name'], update_data['price'], 
                          update_data['calories'], product_id))
            conn.commit()
            
            cursor.execute(PRODUCT_QUERIES["get_by_id"], (product_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def delete_product(conn, product_id: str):
        try:
            cursor = conn.cursor()
            cursor.execute(PRODUCT_QUERIES["delete"], (product_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except Error as e:
            conn.rollback()
            raise e