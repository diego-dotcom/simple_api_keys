import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise

def insert_or_update_api_key(email: str, api_key: str):
    """
    Inserta un nuevo registro si el email no existe,
    o actualiza la API key si ya existe.
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM api_keys WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result:
                # Actualizar la API key si el email ya existe
                cursor.execute(
                    "UPDATE api_keys SET api_key = %s WHERE email = %s",
                    (api_key, email)
                )
            else:
                # Insertar un nuevo registro si el email no existe
                cursor.execute(
                    "INSERT INTO api_keys (email, api_key) VALUES (%s, %s)",
                    (email, api_key)
                )
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar/actualizar API key: {e}")
        raise
    finally:
        connection.close()
