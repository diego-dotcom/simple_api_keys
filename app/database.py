import pymysql
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

MASTER_KEY = os.getenv("MASTER_KEY")

fernet = Fernet(MASTER_KEY)

def encrypt_api_key(api_key: str) -> str:
    """Encripta una API key."""
    return fernet.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    """Desencripta una API key."""
    return fernet.decrypt(encrypted_api_key.encode()).decode()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise

def insert_or_update_api_key(email: str, api_key: str):
    """
    Inserta un nuevo registro si el email no existe,
    o actualiza la API key encriptada si ya existe.
    """
    encrypted_api_key = encrypt_api_key(api_key)  # Encripta la API key

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM api_keys WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result:
                # Actualizar la API key encriptada si el email ya existe
                cursor.execute(
                    "UPDATE api_keys SET api_key = %s WHERE email = %s",
                    (encrypted_api_key, email)
                )
            else:
                # Insertar un nuevo registro si el email no existe
                cursor.execute(
                    "INSERT INTO api_keys (email, api_key) VALUES (%s, %s)",
                    (email, encrypted_api_key)
                )
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar/actualizar API key: {e}")
        raise
    finally:
        connection.close()

def get_api_key_by_email(email: str) -> str:
    """Obtiene y desencripta la API key asociada a un email."""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT api_key FROM api_keys WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result:
                return decrypt_api_key(result["api_key"])  # Desencripta la API key
            else:
                return None
    except pymysql.MySQLError as e:
        print(f"Error al obtener API key: {e}")
        raise
    finally:
        connection.close()