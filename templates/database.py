import mysql.connector
from mysql.connector import Error

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vai_shn@vi1234',  # <--- UPDATE YOUR MYSQL PASSWORD HERE!
    'database': 'campusos_db'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"❌ DATABASE ERROR: {e}")
        return None

def query_db(query, args=(), fetchone=False, fetchall=False, commit=False):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
        if fetchone:
            res = cursor.fetchone()
            cursor.close()
            conn.close()
            return res
        if fetchall:
            res = cursor.fetchall()
            cursor.close()
            conn.close()
            return res
    except Error as err:
        print(f"❌ QUERY EXECUTION ERROR: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()