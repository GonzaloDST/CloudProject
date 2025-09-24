from mysql.connector import Error
from app.models.models import ORDER_QUERIES
from app.models.schemas import OrderStatus

class OrderCRUD:
    @staticmethod
    def create_order(conn, order):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(ORDER_QUERIES["create"], 
                         (order.user_id, order.product_id, order.status, 
                          order.total_price, order.payment_method))
            conn.commit()
            
            # Obtener el pedido creado con detalles
            cursor.execute("SELECT id FROM orders WHERE user_id = %s ORDER BY order_date DESC LIMIT 1", 
                         (order.user_id,))
            new_order_id = cursor.fetchone()['id']
            
            cursor.execute(ORDER_QUERIES["get_by_id"], (new_order_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def get_orders(conn):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(ORDER_QUERIES["get_all"])
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise e

    @staticmethod
    def get_order_by_id(conn, order_id: str):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(ORDER_QUERIES["get_by_id"], (order_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            raise e

    @staticmethod
    def get_orders_by_user(conn, user_id: str):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(ORDER_QUERIES["get_by_user"], (user_id,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise e

    @staticmethod
    def get_orders_by_status(conn, status: OrderStatus):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(ORDER_QUERIES["get_by_status"], (status,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise e

    @staticmethod
    def update_order(conn, order_id: str, order):
        try:
            current_order = OrderCRUD.get_order_by_id(conn, order_id)
            if not current_order:
                return None

            update_data = {
                'status': order.status or current_order['status'],
                'total_price': order.total_price or current_order['total_price'],
                'payment_method': order.payment_method or current_order['payment_method']
            }

            cursor = conn.cursor(dictionary=True)
            cursor.execute(ORDER_QUERIES["update"], 
                         (update_data['status'], update_data['total_price'], 
                          update_data['payment_method'], order_id))
            conn.commit()
            
            cursor.execute(ORDER_QUERIES["get_by_id"], (order_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def delete_order(conn, order_id: str):
        try:
            cursor = conn.cursor()
            cursor.execute(ORDER_QUERIES["delete"], (order_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except Error as e:
            conn.rollback()
            raise e