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

@sales.route('/sale/<id>/leads', methods=['GET'])
@role_required('Admin')
def get_sale_leads(id):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT 
                    l.id,
                    s.id AS salesPersonId,
                    l.firstName || ' ' || l.lastName AS name,
                    l.email,
                    l.mobile,
                    CASE 
                        WHEN l.salesPersonId IS NULL THEN 0
                        ELSE 1
                    END AS isMyLead,
                   FROM sales s 
                   LEFT JOIN leads l ON s.id = l.salesPersonId OR l.salesPersonId IS NULL
                   WHERE s.id = %s''', (id,))
    leads_data = cursor.fetchall()
    leads_data = [lead for lead in leads_data if lead['id'] is not None]
    return jsonify(leads_data)

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
    
    return jsonify({{"message": "Created successfully"}}), 201

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
    
    return jsonify({{"message": "Updated successfully"}}), 201

@sales.route('/sale/<id>/leads', methods=['POST'])
@role_required('Admin')
def update_sale_leads(id):
    db = Db.get_db()
    cursor = db.cursor()
    
    lead_ids = request.form.getlist('ids[]')
    sales_person_id =id
    
    for lead_id in lead_ids:
        cursor.execute('''UPDATE leads 
                        SET salesPersonId = %s 
                        WHERE id = %s''', 
                    (sales_person_id, lead_id))
        db.commit()
    
    return jsonify({{"message": "Lead updated successfully"}}), 201