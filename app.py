from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# 配置数据库连接
def connect_to_db():
    conn = mysql.connector.connect(
        host="localhost",          # 数据库主机地址
        user="root",               # 数据库用户名
        password="520ZHQ1314@",   # 数据库密码
        database="rental_system"  # 数据库名称
    )
    return conn

# 获取所有车辆
def get_vehicles():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return vehicles

# 添加新车辆
def add_vehicle(vehicle_model, vehicle_type, registration_number, rent_price):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vehicles (vehicle_model, vehicle_type, registration_number, rent_price, status)
        VALUES (%s, %s, %s, %s, 'available')
    """, (vehicle_model, vehicle_type, registration_number, rent_price))
    conn.commit()
    cursor.close()
    conn.close()

# 更新车辆信息
def update_vehicle(vehicle_id, vehicle_model, vehicle_type, registration_number, rent_price):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vehicles
        SET vehicle_model = %s, vehicle_type = %s, registration_number = %s, rent_price = %s
        WHERE vehicle_id = %s
    """, (vehicle_model, vehicle_type, registration_number, rent_price, vehicle_id))
    conn.commit()
    cursor.close()
    conn.close()

# 删除车辆
def delete_vehicle(vehicle_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    conn.commit()
    cursor.close()
    conn.close()

# 获取车辆详情
def get_vehicle_by_id(vehicle_id):
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()
    cursor.close()
    conn.close()
    return vehicle

# 租赁车辆
def rent_vehicle(vehicle_id, customer_id, rental_start_date, rental_end_date):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE vehicles SET status = 'rented' WHERE vehicle_id = %s", (vehicle_id,))
    cursor.execute("""
        INSERT INTO rental_records (vehicle_id, customer_id, rental_start_date, rental_end_date)
        VALUES (%s, %s, %s, %s)
    """, (vehicle_id, customer_id, rental_start_date, rental_end_date))
    conn.commit()
    cursor.close()
    conn.close()

# 归还车辆
def return_vehicle_process(vehicle_id, return_date):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE vehicles SET status = 'available' WHERE vehicle_id = %s", (vehicle_id,))
    cursor.execute("""
        UPDATE rental_records
        SET return_date = %s
        WHERE vehicle_id = %s AND return_date IS NULL
    """, (return_date, vehicle_id))
    conn.commit()
    cursor.close()
    conn.close()

# 首页，显示所有车辆信息
@app.route('/')
def index():
    vehicles = get_vehicles()
    return render_template('index.html', vehicles=vehicles)

# 添加车辆页面
@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle_view():
    if request.method == 'POST':
        vehicle_model = request.form['vehicle_model']
        vehicle_type = request.form['vehicle_type']
        registration_number = request.form['registration_number']
        rent_price = request.form['rent_price']
        add_vehicle(vehicle_model, vehicle_type, registration_number, rent_price)
        return redirect(url_for('index'))
    return render_template('add_vehicle.html')

# 编辑车辆页面
@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    if request.method == 'POST':
        vehicle_model = request.form['vehicle_model']
        vehicle_type = request.form['vehicle_type']
        registration_number = request.form['registration_number']
        rent_price = request.form['rent_price']
        update_vehicle(vehicle_id, vehicle_model, vehicle_type, registration_number, rent_price)
        return redirect(url_for('index'))
    
    vehicle = get_vehicle_by_id(vehicle_id)
    return render_template('edit_vehicle.html', vehicle=vehicle)

# 删除车辆
@app.route('/delete_vehicle/<int:vehicle_id>')
def delete_vehicle_view(vehicle_id):
    delete_vehicle(vehicle_id)
    return redirect(url_for('index'))

# 租赁车辆页面
@app.route('/rent_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def rent_vehicle_view(vehicle_id):
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        rental_start_date = request.form['rental_start_date']
        rental_end_date = request.form['rental_end_date']
        rent_vehicle(vehicle_id, customer_id, rental_start_date, rental_end_date)
        return redirect(url_for('index'))
    return render_template('rent_vehicle.html', vehicle_id=vehicle_id)

# 归还车辆页面
@app.route('/return_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def return_vehicle_view(vehicle_id):
    if request.method == 'POST':
        return_date = request.form['return_date']
        return_vehicle_process(vehicle_id, return_date)
        return redirect(url_for('index'))
    return render_template('return_vehicle.html', vehicle_id=vehicle_id)
# 录入客户信息
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer_view():
    conn = connect_to_db()  # 获取数据库连接
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        try:
            cursor = conn.cursor()  # 创建游标
            cursor.execute("INSERT INTO customers (name, email) VALUES (%s, %s)", (name, email))
            conn.commit()  # 提交事务
        except Exception as e:
            print(f"Error: {e}")  # 打印错误信息
            conn.rollback()  # 回滚事务
        finally:
            cursor.close()  # 关闭游标
            conn.close()  # 关闭连接
        return redirect(url_for('index'))
    return render_template('add_customer.html')


# 查看客户信息
@app.route('/customers', methods=['GET'])
def view_customers():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()  # 获取所有客户信息
    cursor.close()
    conn.close()
    return render_template('view_customers.html', customers=customers)

# 查询车辆租赁记录及状态
@app.route('/rental_records', methods=['GET'])
def view_rental_records():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT r.rental_id, v.vehicle_model, v.registration_number, c.name, r.rental_start_date, r.rental_end_date, r.return_date, v.status "
                   "FROM rental_records r "
                   "JOIN vehicles v ON r.vehicle_id = v.vehicle_id "
                   "JOIN customers c ON r.customer_id = c.customer_id")
    rental_records = cursor.fetchall()  # 获取租赁记录
    cursor.close()
    conn.close()
    return render_template('view_rental_records.html', rental_records=rental_records)

# 查询租金高于平均租金的车辆
@app.route('/high_rent_vehicles', methods=['GET'])
def view_high_rent_vehicles():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles WHERE rent_price > (SELECT AVG(rent_price) FROM vehicles)")  # 子查询：查找高于平均租金的车辆
    high_rent_vehicles = cursor.fetchall()  # 获取租金高于平均值的车辆
    cursor.close()
    conn.close()
    return render_template('view_high_rent_vehicles.html', high_rent_vehicles=high_rent_vehicles)

#查询统计租赁总收入
@app.route('/total_revenue', methods=['GET'])
def view_total_revenue():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT SUM(p.amount) AS total_revenue FROM payment_records p")  # 统计总收入
    total_revenue = cursor.fetchone()['total_revenue']  # 获取总收入
    cursor.close()
    conn.close()
    return render_template('view_total_revenue.html', total_revenue=total_revenue)

# 查询空闲车辆
@app.route('/available_vehicles', methods=['GET'])
def view_available_vehicles():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles WHERE status = 'available'")  # 查询状态为“可用”的车辆
    available_vehicles = cursor.fetchall()  # 获取空闲车辆
    cursor.close()
    conn.close()
    return render_template('view_available_vehicles.html', available_vehicles=available_vehicles)


# 查询不同客户等级权限
@app.route('/customer_permissions', methods=['GET'])
def view_customer_permissions():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT c.name, r.rental_limit FROM rental_limits r JOIN customers c ON r.customer_id = c.customer_id")
    customer_permissions = cursor.fetchall()  # 获取客户及其对应权限
    cursor.close()
    conn.close()
    return render_template('view_customer_permissions.html', customer_permissions=customer_permissions)




if __name__ == '__main__':
    app.run(debug=True)
