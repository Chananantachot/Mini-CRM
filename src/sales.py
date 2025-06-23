import uuid
from flask import Blueprint, jsonify, request
from Db import Db
from decorators import role_required

sales = Blueprint('sales', __name__, template_folder='templates')

@sales.route('/sales', methods=['GET'])
@role_required('Admin')
def get_sales():
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT 
                    id,
                    name
                    email,
                    phone,
                    active
                   FROM sales 
                   ''')
    sales_data = cursor.fetchall()
    sales_data = [sale for sale in sales_data if sale['id'] is not None]
    return jsonify(sales_data)
    

@sales.route('/sales', methods=['POST'])
@role_required('Admin')
def add_sale():
    db = Db.get_db()
    cursor = db.cursor()
    data = request.get_json()
    
    id = str(uuid.uuid4())
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    active = request.form.get('active', 'true').lower() == 'true'
    
    cursor.execute('''INSERT INTO sales (id, name, email, phone, active) 
                      VALUES (%s, %s, %s, %s, %s)''', 
                   (id, name, email, phone,active))
    db.commit()
    
    return jsonify({'id': id}), 201

@sales.route('/sales', methods=['PUT'])
@role_required('Admin')
def update_sale():
    db = Db.get_db()
    cursor = db.cursor()
    data = request.get_json()
    sale_id = request.form.get('id')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    active = request.form.get('active', 'true').lower() == 'true'
    
    cursor.execute('''UPDATE sales 
                      SET name = %s, email = %s, phone = %s ,active = %s
                      WHERE id = %s''', 
                   (name, email, phone, active,sale_id))
    db.commit()
    
    return jsonify({'id': sale_id}), 204