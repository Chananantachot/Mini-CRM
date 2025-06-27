import datetime
import os
import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from dotenv import load_dotenv

from audit import AuditAction, log_audit
load_dotenv()

from Db import Db

tasks = Blueprint('tasks', __name__, template_folder='templates')

@tasks.route('/tasks', methods=['GET'])
@jwt_required()
def get_due_tasks():
    today = datetime.date.today()
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT t.id,
            t.title,
            t.description,        
            t.due_date, 
            COALESCE(s.name, '') as assigned_to,
            t.priority,
            COALESCE(c.firstName || ' ' || c.lastName, l.firstName || ' ' || l.lastName) as relatedTo_id,
            CASE WHEN t.due_date <= ? AND t.status = 'Pending' AND t.notified = 0 THEN 1 ELSE 0 END as isNotify
        FROM tasks t
        LEFT JOIN leads l ON l.id = t.relatedTo_id
        LEFT JOIN customers c ON c.id = t.relatedTo_id
        LEFT JOIN sales s ON s.id = t.assigned_to
       WHERE t.status = 'Pending' AND t.notified = 0
    """, (today,))
    tasks = cursor.fetchall()
    tasks = [dict(task) for task in tasks if task]
    return jsonify(tasks)

@tasks.route('/tasks/leads/<saleId>', methods=['GET'])
@jwt_required()
def getLeadsOrCustsBySaleId(saleId):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT l.id,
               l.firstName || ' ' || l.lastName as name
        FROM leads l 
        LEFT JOIN customers c on c.id = l.id OR c.id IS NOT NULL
        LEFT JOIN sales s on l.salesPersonId = s.id AND l.salesPersonId IS NOT NULL
        WHERE s.id = ? OR ? IS NULL
    ''', (saleId,saleId,))
    leads = cursor.fetchall()
    leads = [dict(lead) for lead in leads if lead ]
    return leads

@tasks.route('/tasks/publicKey', methods=['GET'])
def getpublicKey():
    key = os.getenv("VAPID_PUBLIC_KEY")
    return jsonify({'publicKey': key })

@tasks.route('/tasks', methods=['POST'])
@jwt_required()
def createTask():
    db = Db.get_db()
    cursor = db.cursor()

    id = str(uuid.uuid4())
    title = request.form.get('title')
    description = request.form.get('description')
    assigned_to = request.form.get('assigned_to') #sale person Ids
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')
    relatedTo_id = request.form.get('relatedTo_id') #lead or customer Ids

    cursor.execute(''' INSERT INTO tasks (id,title,description,assigned_to,due_date,priority,relatedTo_id)
                         VALUES (?,?,?,?,?,?,?) ''', 
                        (id,title,description,assigned_to,due_date,priority,relatedTo_id,))
    
    db.commit()
    
    log_audit(action=AuditAction.INSERT,
            table_name='tasks',
            record_id= id,
            old_value=None,
            new_value=jsonify({'id': id, 'title':title, 'description': description,'assigned_to': assigned_to, 'due_date': due_date, 'priority':priority, 'relatedTo_id':relatedTo_id }))  
    return jsonify({'message': 'Task created successfully.', 'assigned_to': assigned_to})

@tasks.route('/tasks/subscription', methods=['POST'])
def task_subscription():
   if request.is_json: 
        subscription = request.get_json()
        user_id = subscription.get('user_id')
        subscription_json = subscription.get('subscription_json')

        db = Db.get_db()
        cursor = db.cursor()
        id = str(uuid.uuid4())

        cursor.execute(''' INSERT INTO subscriptions (id,user_id,subscription_json) VALUES (?,?,?)''',(id,user_id, subscription_json,))
        db.commit()

        log_audit(action=AuditAction.INSERT,
            table_name='subscriptions',
            record_id= id,
            old_value=None,
            new_value=jsonify({'id': id, 'user_id': user_id, 'subscription_json': subscription_json }))  
        return jsonify({'message': 'Task created successfully.'}) , 201
   return jsonify({'message': 'Bad Request.'}) , 400

@tasks.route('/task/<task_id>', methods=['PUT'])    
@jwt_required()  
def mark_task_as_notified(task_id):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task_id,))
    db.commit()
    return jsonify({'message': 'Updated task successfully'}), 204
