import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from Db import Db
from decorators import role_required

interactions = Blueprint('interactions', __name__, template_folder='templates')

@interactions.route('/<custId>/interactions/<prodsId>', methods=['GET'])
@role_required('admin')
def get_interactions(custId, prodsId):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''
                    SELECT  id,
                            user_id,
                            customer_id,
                            interaction_type,
                            product_id,
                            note,
                            strftime('%D-%m-%Y', timestamp) AS activity_date,
                    FROM interactions
                    WHERE product_id = ? AND customer_id = ?
                    ORDER BY timestamp DESC
                ''', (prodsId,custId,))
    rows = cursor.fetchall()
    interactions_list =  [dict(activity) for activity in rows if activity is not None]
    return jsonify(interactions_list), 200  

@interactions.route('/interactions', methods=['POST'])
@role_required('admin')
def add_interaction():
    email = get_jwt_identity() 
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    id = str(uuid.uuid4())
    user = Db.getCurrentActiveUser(email)
    data['user_id'] = user['id'] 

    required_fields = ['user_id', 'customer_id', 'interaction_type', 'product_id', 'note']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''
                    INSERT INTO interactions (id ,user_id, customer_id, interaction_type, product_id, note)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id ,data['user_id'], data['customer_id'], data['interaction_type'], data['product_id'], data['note']))
    db.commit()

    return jsonify({"message": "Interaction added successfully"}), 201