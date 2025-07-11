from gevent import monkey; monkey.patch_all()
import os
import random
import datetime
import threading
from dotenv import load_dotenv
from decorators import role_required
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import date
import requests
import ssl
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

load_dotenv()
from Db import Db
from users import users
from customers import customers
from leads import leads
from sales import sales
from products import products
from opportunities import opportunities
from orders import orders
from tasks import tasks
from interactions import interactions

from flask import (
    Flask, jsonify, make_response, url_for, send_from_directory ,render_template, request, redirect, g
)
from flask_jwt_extended import (
    get_jwt, jwt_required, JWTManager,
    get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
)

from flask.cli import with_appcontext
import click

from datetime import date, timedelta

app = Flask(__name__)
app.register_blueprint(users)
app.register_blueprint(customers)
app.register_blueprint(leads)
app.register_blueprint(sales)
app.register_blueprint(opportunities)
app.register_blueprint(products)
app.register_blueprint(orders)
app.register_blueprint(tasks)
app.register_blueprint(interactions)

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True  # Set to False in development if not using HTTPS
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie' 
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False 
jwt = JWTManager(app)

socketio = SocketIO(app, cors_allowed_origins='*')
# Dictionary to keep track of locked leads
lead_lock = {}
lock = threading.Lock()

@click.command(name='seed')
def seed():
    Db.seedAccount()
    Db.seedLeads()
    Db.seedSales()
    Db.SeedProducts()
    print("Database seeded!")

# Automatically seed the database when Flask starts
with app.app_context():
    Db.init_db()
 
def register_commands(app):
    app.cli.add_command(seed)

register_commands(app)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def before_request():
    if request.endpoint in ['sw','user', 'roles','newUser','users.register', 'users.signin','login','users.activateUser' ,'static']:
        return
    try:
        verify_jwt_in_request()
    except:
        return redirect(url_for('login', next=request.url))

@app.route("/customers", methods=['GET'])
@jwt_required()
def customer():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"] or [] 
    isAdminRole = 'Admin' in roles
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    
    return render_template('customer.html',current_user = user)

@app.route("/leads", defaults = {'custId' : None},  methods=['GET'])
@app.route("/customers/<custId>" , methods=['GET'])
@jwt_required()
def lead(custId):
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"] or [] 
    isAdminRole = 'Admin' in roles
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    return render_template('lead.html',current_user = user)

@app.route("/lead/call/answer/<room>", defaults={ id: None } , methods=['GET'])
@app.route("/user/subscribe/<id>", defaults={'room': None}, methods=['GET'])
def calling_handler(room,id):
    response = requests.get('https://randomuser.me/api/')
    data = response.json()
    contacts = data['results']
    if len(contacts) > 1:
        c = random.choice(contacts)
    else:
        c = contacts[0]

    random_latitude = round(float(random.uniform(-90.0, 90.0)), 1)
    random_longitude = round(float(random.uniform(-180.0, 180.0)),1)     
    contact ={
        'fullName': f"{c['name']['first']} {c['name']['last']}",
        'picture' : c['picture']['thumbnail'],
        'latitude': c['location']['coordinates']['latitude'],
        'longitude': c['location']['coordinates']['longitude']
    }
    return render_template('handlerCall.html',subscriberId = id ,room = room,contact=contact, GAID=os.getenv("GA_MEASUREMENT_ID"))

@app.route("/subscriber/<id>" , methods=['GET'])
def getUserSubscriber(id):
    db = Db.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM subscriptions WHERE user_id = ?", (id,))
    Subscriber = cursor.fetchone()

    if Subscriber:
        return jsonify({'Subscriber': id }), 200
    return jsonify({'Subscriber': None}), 200

@app.route("/sale", methods=['GET'])
@role_required(['Admin'])
def sale():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"] or [] 
    isAdminRole = 'Admin' in roles
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    
    return render_template('sale.html', current_user=user)


@app.route("/products", methods=['GET'])
@jwt_required()
def product():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"] or [] 
    isAdminRole = 'Admin' in roles
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    
    return render_template('product.html',current_user = user) 

@app.route('/users', methods=['GET'])
@role_required(['Admin'])
def user():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"]  

    isAdminRole = 'Admin' in roles
   
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    return render_template('user.html',current_user = user) 

@app.route('/roles', methods=['GET'])
@role_required(['Admin'])
def roles():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"]  

    isAdminRole = 'Admin' in roles
   
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    return render_template('role.html',current_user = user) 

@app.route('/api/userRoles', methods=['GET'])
@jwt_required()
def getUserRoles():
    roles = get_jwt()["roles"] 
    isAdminRole = 'Admin' in roles
    user = {
        'isAdminRole': isAdminRole
    }

    return jsonify(user), 200


@app.route("/")
@jwt_required()
def home():  
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"]  

    isAdminRole = 'Admin' in roles
   
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    db = Db.get_db()
    cursor = db.cursor()

    # cursor.execute("SELECT * FROM subscriptions WHERE user_id = 1")
    # subs = cursor.fetchall()
    # subs = [dict(s) for s in subs if s]
    # print(f'subscription: {subs}')


    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM opportunities WHERE current_stage NOT IN ('Closed Won', 'Closed Lost')")
    open_opps = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'")
    completed_orders = cursor.fetchone()[0]

    cursor.execute("SELECT IFNULL(SUM(total), 0) FROM orders WHERE status = 'Completed'")
    total_revenue = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE active = 1")
    active_users = cursor.fetchone()[0]

    # Lead Table
    cursor.execute("""
        SELECT firstName, lastName, email, mobile, source, status, created_at
        FROM leads
        ORDER BY created_at DESC
        LIMIT 5
    """)
    lead_rows = cursor.fetchall()
    metrics = {
        'leads': total_leads,
        'opportunities': open_opps,
        'orders': completed_orders,
        'revenue': round(total_revenue, 2),
        'users': active_users
    }

    return render_template('home.html',current_user = user, metrics=metrics, 
                           lead_rows=lead_rows,)

@app.route("/lead/dashboard", methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"]  
    db = Db.get_db()
    cursor = db.cursor()
    # Chart: Leads per Month
    #cursor.execute("SELECT strftime('%Y-%m', created_at) AS month, COUNT(*) FROM leads GROUP BY month ORDER BY month")
    #rows = cursor.fetchall()
# Get today's date
    today = date.today()

# Create an empty list to store the dates
    labels = []

# Loop to generate the next 7 days
    for i in range(7):
        # Calculate the date for the current iteration
        current_date = today + timedelta(days=i)
        # Format the date as 'YYYY-MM-DD' and add it to the list
        labels.append(current_date.strftime('%Y-%m-%d'))

    chart_labels =labels #[row[0] for row in rows]
    chart_data = [round(random.uniform(10, 900),2) for _ in range(7)]  #[row[1] for row in rows]
    weekly_leads_data= [round(random.uniform(1, 100),2) for _ in range(7)]
    data = {
        'labels': chart_labels,
        'data': chart_data,
        'weekly_leads': weekly_leads_data
    }    
    return jsonify(data), 200


@app.route('/myTasks', methods=['GET'])
@jwt_required()
def myTasks():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"] 
    isAdminRole = 'Admin' in roles
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }

    return  render_template('task.html',current_user = user)

@app.route("/<id>/order/", defaults = { 'orderId' : None} , methods=['GET'])
@app.route("/<id>/order/<orderId>", methods=['GET'])
@jwt_required()
def order(id,orderId):  
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"]  

    isAdminRole = 'Admin' in roles
   
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    return render_template('order.html',current_user = user)

@app.route('/register', methods=['GET'])
def newUser():
    userid = request.args.get('userid')
    email = request.args.get('email')
    return render_template('register.html', userid = userid, existedUser = email)

@app.route('/signin', methods=['GET'])
def login():
    error = request.args.get('error','')
    return render_template('login.html', error = error)

def get_page(data, page_number, page_size):
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    return data[start_index:end_index] 

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = make_response(redirect(request.args.get("next") or url_for("home")))
    unset_jwt_cookies(response)
    return response, 401

@jwt.unauthorized_loader
def missing_token_callback(err):
    response = make_response(redirect(request.args.get("next") or url_for("home")))
    unset_jwt_cookies(response)
    return response, 401

@app.context_processor
def inject_notification_count():
    today = datetime.date.today()
    task_count = 0
    db = Db.get_db()
    cursor = db.cursor()
  
    cursor.execute('''
        SELECT id, title, assigned_to 
        FROM tasks 
        WHERE due_date <= ? AND status = 'Pending' AND notified = 0
        ''', (today,))
    tasks = cursor.fetchall()

    # Group tasks by salesperson
    from collections import defaultdict
    from gevent import pywsgi

    user_tasks = defaultdict(list)
    for task_id, title, user_id in tasks:
        user_tasks[user_id].append((task_id, title))

    # Fetch subscription info per salesperson
    for _, task_list in user_tasks.items():
        task_count = len(task_list)

    return dict(notification_count=task_count, GAID=os.getenv("GA_MEASUREMENT_ID"))

@app.route('/GAMEASUREMENTID')
def getGA_MEASUREMENT_ID():
    id= os.getenv("GA_MEASUREMENT_ID")
    return jsonify({'GAID': id })

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)

@socketio.on('signal')
def handle_signal(data):
    emit('signal', data, room=data['room'], include_self=False)

@socketio.on('decline')
def handle_decline(data):
    room = data['room']
    emit('call-declined', {'room': room}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)    

@app.route('/start_call', methods=['POST'])
@jwt_required()
def start_call():
    current_user = get_jwt_identity() 
    lead_id = request.json['lead_id']
    rep_name = current_user

    with lock:
        if lead_lock.get(lead_id):
            return {"status": "busy"}, 409  # Conflict: lead already in call
        lead_lock[lead_id] = rep_name
        socketio.emit('lead:locked', {"lead_id": lead_id, "rep_name": rep_name})
        return {"status": "locked"}

@app.route('/end_call', methods=['POST'])
@jwt_required()
def end_call():
    lead_id = request.json['lead_id']

    with lock:
        if lead_lock.pop(lead_id, None):
            socketio.emit('lead:released', {"lead_id": lead_id})
            return {"status": "released"},200
        return {"status": "not_found"}, 404
    

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

if __name__ == '__main__':
   # Directly use Gevent's WSGIServer with SSL and WebSocket
   http_server = WSGIServer(
    ('0.0.0.0', 5000),  # ✅ Use port 5000
    app,
    handler_class=WebSocketHandler
    )
   http_server.serve_forever()