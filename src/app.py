import os
from dotenv import load_dotenv
from decorators import role_required

load_dotenv()
from Db import Db
from users import users
from customers import customers
from leads import leads
from products import products
from opportunities import opportunities
from orders import orders

from flask import (
    Flask, jsonify, make_response, url_for, render_template, request, redirect, g
)
from flask_jwt_extended import (
    get_jwt, jwt_required, JWTManager,
    get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
)

from flask.cli import with_appcontext
import click

from datetime import timedelta

app = Flask(__name__)
app.register_blueprint(users)
app.register_blueprint(customers)
app.register_blueprint(leads)
app.register_blueprint(opportunities)
app.register_blueprint(products)
app.register_blueprint(orders)

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

@click.command(name='seed')
@with_appcontext
def seed():
    Db.init_db()
    Db.seedAccount()
    Db.seedLeads()
    Db.SeedProducts()
    print("Database seeded!")
 
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
    if request.endpoint in ['customer', 'lead', 'product' ,'user', 'roles','newUser','users.register', 'users.signin','login','users.activateUser','static']:
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

@app.route("/leads", methods=['GET'])
@jwt_required()
def lead():
    current_user = get_jwt_identity() 
    roles = get_jwt()["roles"] or [] 
    isAdminRole = 'Admin' in roles
    user = {
        'name': current_user,
        'isAdminRole': isAdminRole
    }
    
    return render_template('lead.html',current_user = user)

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
@role_required('Admin')
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
@role_required('Admin')
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
    return render_template('home.html',current_user = user)

@app.route("/order")
@jwt_required()
def order():  
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

if __name__ == '__main__':
   app.run(ssl_context="adhoc", host='0.0.0.0' , port=5000)  # Use SSL context for HTTPS