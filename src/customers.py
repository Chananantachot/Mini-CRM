import uuid
from flask import Blueprint, jsonify, redirect, request, url_for
from flask_jwt_extended import get_jwt, jwt_required

from Db import Db
from decorators import role_required

customers = Blueprint('customers', __name__, template_folder='templates')

@customers.route('/api/customers', methods=['GET'])
@jwt_required()
def getCustomers():
    results = Db.getCustomers()
    customers = [dict(customer) for customer in results if customer]
    return jsonify(customers),200

@customers.route('/api/customer/<id>', methods=['GET'])
@jwt_required()
def getCustomer(id):
    result = Db.getCustomer(id)
    customer = dict(result)
    return jsonify(customer),200

@customers.route('/api/lead/new/customer', methods=['POST'])
@role_required('Admin')
def convertLeadToCustomer():
    leadId = request.form.get('leadId')
    if leadId:
        lead = Db.getLeadConverted(leadId)
        if lead:
            lead = dict(lead)
            id = Db.covertLeadToCustomer(lead['id'],lead['firstName'], lead['lastName'], lead['email'],lead['mobile'])
            if id:
                jsonify({'error': False, 'message': 'Cretated.'}), 201
            
    return jsonify({'error': True, 'message': 'Failed.'}), 400
            
@customers.route('/api/customer/new', methods=['POST'])
@role_required('Admin')
def postCustomer():
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    mobile = request.form.get('mobile')

    if firstName and lastName and email:
        customer = Db.getCustomerBy(firstName,lastName)
        if not customer:
            id = Db.createCustomer(firstName,lastName,email,mobile)
            if id:
                 return redirect(url_for('customer'))
            
        return jsonify({'error': True, 'message': f'{firstName} {lastName} already exists.'}), 400    
        
    return jsonify({'error': True, 'message': 'Failed.'}), 400

@customers.route('/api/customer/edit', methods=['POST'])
@role_required('Admin')
def putCustomer():
    id = request.form.get('id')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    mobile = request.form.get('mobile')

    skipCheckUniqeName = False
    if id:
        cust = Db.getCustomer(id)
        if cust:
            cust = dict(cust)
            if firstName and lastName and email and cust['firstName'] == firstName and cust['lastName'] == lastName:
                 skipCheckUniqeName =  cust['email'] != email or cust['mobile'] != mobile 
        else:
            return jsonify({'error': True, 'message': 'Not Founded.'}),404          
    else:
        return jsonify({'error': True, 'message': 'Not Founded.'}),404             

    customer = None
    isFirstLastUniqe = True
    if not skipCheckUniqeName:
        customer = Db.getCustomerBy(firstName,lastName)
        isFirstLastUniqe = not customer

    if isFirstLastUniqe:
        _id = Db.updateCustomer(id,firstName,lastName,email,mobile)
        if _id:
            return redirect(url_for('customer'))
        
    return jsonify({'error': True, 'message': f'{firstName} {lastName} already exists.'}), 400     
        
   