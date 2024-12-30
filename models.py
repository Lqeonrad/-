import mysql.connector
from datetime import datetime

# 获取数据库连接
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='520ZHQ1314@',  # 数据库密码
        database='rental_system'
    )
    return conn

# 车辆信息管理
def add_vehicle(vehicle_model, vehicle_type, registration_number, rent_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO vehicles (vehicle_model, vehicle_type, registration_number, rent_price, status)
        VALUES (%s, %s, %s, %s, 'available')
    """
    values = (vehicle_model, vehicle_type, registration_number, rent_price)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def update_vehicle(vehicle_id, vehicle_model, vehicle_type, registration_number, rent_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE vehicles 
        SET vehicle_model = %s, vehicle_type = %s, registration_number = %s, rent_price = %s 
        WHERE vehicle_id = %s
    """
    values = (vehicle_model, vehicle_type, registration_number, rent_price, vehicle_id)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def delete_vehicle(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM vehicles WHERE vehicle_id = %s"
    cursor.execute(query, (vehicle_id,))
    conn.commit()
    cursor.close()
    conn.close()

def search_vehicles(search_query):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM vehicles WHERE vehicle_model LIKE %s OR vehicle_type LIKE %s"
    values = ('%' + search_query + '%', '%' + search_query + '%')
    cursor.execute(query, values)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_vehicle_type(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT vehicle_type FROM vehicles WHERE vehicle_id = %s"
    cursor.execute(query, (vehicle_id,))
    vehicle_type = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return vehicle_type

def update_vehicle_status(vehicle_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE vehicles SET status = %s WHERE vehicle_id = %s"
    cursor.execute(query, (status, vehicle_id))
    conn.commit()
    cursor.close()
    conn.close()

# 租赁操作
def rent_vehicle(vehicle_id, customer_id, rental_start_date, rental_end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 更新车辆状态为租出
    update_vehicle_status(vehicle_id, 'rented')

    # 记录租赁信息
    query = """
        INSERT INTO rental_records (vehicle_id, customer_id, rental_start_date, rental_end_date)
        VALUES (%s, %s, %s, %s)
    """
    values = (vehicle_id, customer_id, rental_start_date, rental_end_date)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def return_vehicle(vehicle_id, rental_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 更新车辆状态为可用
    update_vehicle_status(vehicle_id, 'available')

    # 记录归还时间
    query = "UPDATE rental_records SET return_date = NOW() WHERE rental_id = %s"
    cursor.execute(query, (rental_id,))
    conn.commit()
    cursor.close()
    conn.close()

def calculate_rental_fee(vehicle_id, rental_start_date, rental_end_date):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取车辆租金
    query = "SELECT rent_price FROM vehicles WHERE vehicle_id = %s"
    cursor.execute(query, (vehicle_id,))
    rent_price = cursor.fetchone()[0]

    # 计算租赁天数
    rental_start_date = datetime.strptime(rental_start_date, "%Y-%m-%d")
    rental_end_date = datetime.strptime(rental_end_date, "%Y-%m-%d")
    rental_days = (rental_end_date - rental_start_date).days

    # 计算租金
    rental_fee = rental_days * rent_price
    cursor.close()
    conn.close()

    return rental_fee

# 统计功能
def get_total_rental_income():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT SUM(rent_price * DATEDIFF(return_date, rental_start_date)) 
        FROM rental_records 
        JOIN vehicles ON rental_records.vehicle_id = vehicles.vehicle_id
        WHERE return_date IS NOT NULL
    """
    cursor.execute(query)
    total_income = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_income

def get_most_popular_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT vehicle_model, COUNT(*) AS rental_count 
        FROM rental_records
        JOIN vehicles ON rental_records.vehicle_id = vehicles.vehicle_id
        GROUP BY vehicle_model
        ORDER BY rental_count DESC
        LIMIT 5
    """
    cursor.execute(query)
    popular_vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return popular_vehicles

def get_available_vehicles_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM vehicles WHERE status = 'available'"
    cursor.execute(query)
    available_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return available_count

# 客户权限管理
def get_customer_rental_limit(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT rental_limit FROM rental_limits WHERE customer_id = %s"
    cursor.execute(query, (customer_id,))
    rental_limit = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return rental_limit

def rent_vehicle_with_limit(vehicle_id, customer_id, rental_start_date, rental_end_date):
    rental_limit = get_customer_rental_limit(customer_id)
    vehicle_type = get_vehicle_type(vehicle_id)

    if rental_limit == 'admin' or rental_limit == vehicle_type:
        rent_vehicle(vehicle_id, customer_id, rental_start_date, rental_end_date)
        return "Vehicle rented successfully"
    else:
        return "Customer does not have permission to rent this vehicle"

