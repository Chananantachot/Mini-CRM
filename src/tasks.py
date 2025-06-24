import datetime
import uuid
from flask import Blueprint, jsonify, redirect, request, url_for
from flask_jwt_extended import jwt_required

from Db import Db
from audit import AuditAction, log_audit
from decorators import role_required

tasks = Blueprint('tasks', __name__, template_folder='templates')

@tasks.route('/tasks', methods=['GET'])
@jwt_required()
def get_due_tasks():
    today = datetime.date.today()
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id,
            title,
            description,        
            due_date, 
            assigned_to,
            due_date,
            priority,
            relatedTo_id        
        FROM tasks 
        WHERE due_date <= ? AND status = 'Pending' AND notified = 0
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
        LEFT JOIN sales s on l.salesPersonId = s.id AND l.salesPersonId IS NOT NULL
        WHERE s.id = ? OR ? IS NULL
    ''', (saleId,saleId,))
    leads = cursor.fetchall()
    leads = [dict(lead) for lead in leads if lead ]
    return leads


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

@tasks.route('/task/<task_id>', methods=['PUT'])    
@jwt_required()  
def mark_task_as_notified(task_id):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task_id,))
    db.commit()
