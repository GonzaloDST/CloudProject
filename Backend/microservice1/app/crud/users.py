from mysql.connector import Error
from app.models.models import USER_QUERIES
from app.models.schemas import User, UserCreate, UserUpdate

class UserCRUD:
    @staticmethod
    def create_user(conn, user: UserCreate):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(USER_QUERIES["create"], 
                         (user.name, user.email, user.phone_number, user.address))
            conn.commit()
            
            # Obtener el usuario creado
            cursor.execute(USER_QUERIES["get_by_email"], (user.email,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def get_users(conn):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(USER_QUERIES["get_all"])
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise e

    @staticmethod
    def get_user_by_id(conn, user_id: str):
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(USER_QUERIES["get_by_id"], (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            raise e

    @staticmethod
    def update_user(conn, user_id: str, user: UserUpdate):
        try:
            # Obtener usuario actual primero
            current_user = UserCRUD.get_user_by_id(conn, user_id)
            if not current_user:
                return None

            # Actualizar solo los campos proporcionados
            update_data = {
                'name': user.name or current_user['name'],
                'email': user.email or current_user['email'],
                'phone_number': user.phone_number or current_user['phone_number'],
                'address': user.address or current_user['address']
            }

            cursor = conn.cursor(dictionary=True)
            cursor.execute(USER_QUERIES["update"], 
                         (update_data['name'], update_data['email'], 
                          update_data['phone_number'], update_data['address'], 
                          user_id))
            conn.commit()
            
            cursor.execute(USER_QUERIES["get_by_id"], (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def delete_user(conn, user_id: str):
        try:
            cursor = conn.cursor()
            cursor.execute(USER_QUERIES["delete"], (user_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except Error as e:
            conn.rollback()
            raise e