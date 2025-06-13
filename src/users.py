import secrets
import uuid
from flask import Blueprint, jsonify, make_response, redirect, render_template, request, url_for
from flask_jwt_extended import jwt_required

from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt, jwt_required,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies
)


from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.security import generate_password_hash, check_password_hash

from TokenUsedError import TokenUsedError
from Db import Db
from decorators import role_required
users = Blueprint('users', __name__, template_folder='templates')

revoked_tokens = set()

@users.route('/logout', methods=['POST', 'GET'])
def logout():
    response = make_response(redirect(url_for('login'))) # or render_template(...)
    unset_jwt_cookies(response)
    return response

@users.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    if not email or not password:
        # Redirect to login with error
        response = redirect(url_for("login", error="Invalid username or password!"))
        response = make_response(response)
        unset_jwt_cookies(response)
        return response

    user = Db.getCurrentActiveUser(email)
    if not user or not check_password_hash(user['password'], password + user['salt']):
        # Login failed — clear any old tokens and redirect with error
        response = redirect(url_for("login", error="Invalid username or password!"))
        response = make_response(response)
        unset_jwt_cookies(response)
        return response

    # Login successful — issue new tokens
    access_token = create_access_token(identity=user['fullname'], additional_claims={"roles": user['roles']})
    refresh_token = create_refresh_token(identity=user['fullname'], additional_claims={"jti": str(uuid.uuid4()), "roles": user['roles']})
    # Set the tokens in cookies
    response = make_response(redirect(request.args.get("next") or url_for("home")))
    _set_jwt_cookies(response, 'access_token_cookie', access_token)
    _set_jwt_cookies(response, 'refresh_token_cookie', refresh_token)

    return response

@users.route('/register', methods=['POST'])
def register():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
   
    if not fullname or not email or not password:
        return redirect(url_for('newUser', error="Please fill in all fields."),200)

    user = Db.getCurrentUser(email)
    if not user:
      salt = secrets.token_urlsafe(16)
      hashed_password = generate_password_hash(password + salt)
      userid = Db.createUser(fullname,email,salt,hashed_password)
    else:
        return redirect(url_for('newUser',userid = None ,email=email))   

    return redirect(url_for('newUser',userid = userid ,email=None))

@users.route('/active', methods=['POST'])
def activateUser():
    userid = request.form['userid']
    if not userid:
        return redirect(url_for('newUser', error="Sorry, We can't find this user in the system."),200)

    user = Db.getCurrentUser(userid)
    if not user:
        return redirect(url_for('newUser', error="User not found."), 200)

    Db.activeUser(userid)
    return redirect(url_for('login'))

@users.route('/api/user', methods=['GET'])
@users.route('/api/user/edit', methods=['POST'])
@role_required('Admin')
def getUser():
    if request.method == 'GET':
        users = Db.getCurrentUsers()
        data = [dict(user) for user in users]
        return jsonify(data)
    else:
        if request.method == 'POST':
            id = request.form.get('id')
            user = Db.getCurrentUser(id)
            if user: 
                active = 0
                fullname = request.form.get('fullname')
                email = request.form.get('email')
                _active = request.form.get('active') 
                if _active == 'true': active = 1

                if fullname and email and active:
                    Db.UpdateUser(id,fullname,email,active)
                    return jsonify({'id': id})
                
            return jsonify({'id': id}), 404

@users.route('/api/roles', methods=['GET'])
@users.route('/api/roles/create', methods=['POST'])
@users.route('/api/roles/edit', methods=['POST'])
@role_required('Admin')
def getRoles():
    if request.method == 'GET':
            roles = Db.getRoles()
            jsonData = [dict(role) for role in roles]
            return jsonify(jsonData)
    else:
         if request.method == 'POST':
             active = 0
             if request.path == '/api/roles/create':
                roleName = request.form.get('roleName')
                description = request.form.get('description')
                _active = request.form.get('active')
                if roleName and description and _active:
                    if _active == 'true':
                        active = 1
                    id = Db.createRole(roleName,description,active)
                    return jsonify({'id': id}) ,201
             else:
                if request.path == '/api/roles/edit':    
                    id = request.form.get('id')
                    roleName = request.form.get('roleName')
                    description = request.form.get('description')
                    _active = request.form.get('active')
                    if id and roleName and description and _active:
                        if _active == 'true':
                            active = 1
                        role = Db.getRoles(id) 
                        if role:
                            Db.UpdateRole(id,roleName,description,active)
                    else:
                        return jsonify({'id': id}) ,404
                    
@users.route('/api/roles/<roleId>/assignment', methods=['GET','POST'])
@role_required('Admin')
@jwt_required()
def rolesAssignment(roleId):
    users = []
    if roleId:
        users = Db.getAssignedUserRoles(roleId)
    
    if request.method == 'GET':
        jsonResponse = [dict(u) for u in users]
        return jsonify(jsonResponse),200
    
    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids[]')  # List of user IDs to assign
        for user in users:
            if user['id'] not in user_ids and user['assigned'] == 1:
                Db.deleteUserRoles(roleId, user['id'])
                
            for userid in user_ids:
                if user['id'] == userid and user['assigned'] == 0: # Will skip the ids that already assigned
                    Db.addUserInRoles(roleId,userid)
                
        return jsonify({"status": "success"}),200
  
  

@users.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]  # Get unique token identifier
    roles = get_jwt()["roles"]  
    if jti in revoked_tokens and roles in revoked_tokens:
        raise handle_token_used()

    revoked_tokens.add(jti)
    revoked_tokens.add(roles)
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, additional_claims={"roles": roles})
    refresh_token = create_refresh_token(identity=identity, additional_claims={"jti": str(uuid.uuid4()), "roles": roles})
    response = make_response(redirect(request.args.get("next") or url_for("home")))
    set_access_cookies(response, access_token)
    set_access_cookies(response, refresh_token)
    return response

@users.errorhandler(NoAuthorizationError)
def handle_missing_token(e):
    return render_template('error.html', status_code=401, msg="You are not authorized to access this page."), 401

@users.errorhandler(TokenUsedError)
def handle_token_used(e):
    return render_template("error.html", status_code=401, msg="Your refresh token has already been used."), 401

def _set_jwt_cookies(response, key ,token):
    response.set_cookie(
        key,
        token,
        httponly=True,
        secure=False,  # set to True if using HTTPS
        samesite='Strict'
    )
