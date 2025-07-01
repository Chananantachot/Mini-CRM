import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from Db import Db
from audit import AuditAction, log_audit
from decorators import role_required

interactions = Blueprint('interactions', __name__, template_folder='templates')

@interactions.route('/<custId>/interactions/<prodsId>', methods=['GET'])
@role_required(['Admin'])
def get_interactions(custId, prodsId):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''
                    SELECT  id,
                            customer_id,
                            interaction_type,
                            product_id,
                            notes,
                            strftime('%d-%m-%Y', date_activity) AS date_activity
                    FROM interactions
                    WHERE product_id = ? AND customer_id = ? 
                    ORDER BY date_activity DESC
                ''', (prodsId, custId,))
    rows = cursor.fetchall()
    interactions_list =  [dict(activity) for activity in rows if activity ]
    return jsonify(interactions_list), 200  

@interactions.route('/<custId>/interactions/<prodsId>', methods=['POST'])
@role_required(['Admin'])
def add_interaction(custId, prodsId):
    id = str(uuid.uuid4())
    interaction_type = request.form.get('interaction_type')
    note = request.form.get('notes')
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''
                    INSERT INTO interactions (id,customer_id, interaction_type, product_id, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id , custId, interaction_type, prodsId , note,))
    log_audit(action=AuditAction.INSERT,
            table_name='interactions',
            record_id= id,
            old_value=None,
            new_value=jsonify({'id': id, 'interaction_type': interaction_type, 'note': note }))  
    db.commit()

    return jsonify({"message": "Interaction added successfully"}), 201