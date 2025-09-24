import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import time

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '3306')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'utec')
        self.database = os.getenv('DB_NAME', 'maki_orders')
        self.connection = None

    def get_connection(self, retries=5, delay=5):
        for attempt in range(retries):
            try:
                if self.connection is None or not self.connection.is_connected():
                    self.connection = mysql.connector.connect(
                        host=self.host,
                        port=int(self.port),
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        auth_plugin='mysql_native_password'
                    )
                return self.connection
            except Error as e:
                if attempt < retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Error connecting to MySQL after {retries} attempts: {e}")
                    raise

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

# Dependency
def get_db():
    db = Database()
    try:
        connection = db.get_connection()
        yield connection
    finally:
        db.close_connection()