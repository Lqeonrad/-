# db.py
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',       # MySQL数据库主机地址
        user='root',            # 数据库用户名
        password='520ZHQ1314@',  # 数据库密码
        database='rental_system'    # 创建的数据库名称
    )
    return conn
