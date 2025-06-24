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
                    name,
                    email,
                    phone,
                    active
                   FROM sales 
                   ''')
    sales_data = cursor.fetchall()
    sales_data = [dict(sale) for sale in sales_data if sale]
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
                    l.mobile as phone,
                    CASE 
                        WHEN l.salesPersonId IS NULL THEN 0
                        ELSE 1
                    END AS isMyLead
                   FROM sales s 
                   LEFT JOIN leads l ON s.id = l.salesPersonId OR l.salesPersonId IS NULL
                   WHERE s.id = ? OR l.salesPersonId IS NULL ''', (id,))
    leads_data = cursor.fetchall()
    leads_data = [dict(lead) for lead in leads_data if lead]
    return jsonify(leads_data)

@sales.route('/sales', methods=['POST'])
@role_required('Admin')
def add_sale():
    db = Db.get_db()
    cursor = db.cursor()
    
    id = str(uuid.uuid4())
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    cursor.execute('''INSERT INTO sales (id, name, email, phone) 
                      VALUES (?, ?, ?, ?)''', 
                   (id, name, email, phone,))
    db.commit()
    
    return jsonify({"message": "Created successfully"}), 201

@sales.route('/sales', methods=['PUT'])
@role_required('Admin')
def update_sale():
    db = Db.get_db()
    cursor = db.cursor()

    sale_id = request.form.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    #active = request.form.get('active', 'true').lower() == 'true'
    
    cursor.execute('''UPDATE sales 
                      SET name = ?, email = ?, phone = ?
                      WHERE id = ?''', 
                   (name, email, phone,sale_id,))
    db.commit()
    
    return jsonify({"message": "Updated successfully"}), 201

@sales.route('/sale/<id>/leads', methods=['POST'])
@role_required('Admin')
def update_sale_leads(id):
    db = Db.get_db()
    cursor = db.cursor()
    
    lead_ids = request.form.getlist('ids[]')
    sales_person_id =id
    
    for lead_id in lead_ids:
        cursor.execute('''UPDATE leads 
                        SET salesPersonId = ? 
                        WHERE id = ?''', 
                    (sales_person_id, lead_id,))
        db.commit()
    
    return jsonify({"message": "Lead updated successfully"}), 201