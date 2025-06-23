import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from Db import Db
from decorators import role_required

interactions = Blueprint('interactions', __name__, template_folder='templates')

@interactions.route('/<custId>/interactions/<prodsId>', methods=['GET'])
@role_required('Admin')
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
    interactions_list =  [dict(activity) for activity in rows if activity is not None]
    return jsonify(interactions_list), 200  

@interactions.route('/interactions', methods=['POST'])
@role_required('Admin')
def add_interaction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400



    required_fields = ['customer_id', 'interaction_type', 'product_id', 'note']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''
                    INSERT INTO interactions (id,customer_id, interaction_type, product_id, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id , data['customer_id'], data['interaction_type'], data['product_id'], data['note']))
    db.commit()

    return jsonify({"message": "Interaction added successfully"}), 201