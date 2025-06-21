from flask import Blueprint, jsonify, redirect, request, url_for
from flask_jwt_extended import jwt_required

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
        
@customers.route('/api/customer/<id>/address', methods=['GET'])
def getAddress(id):
    address = Db.getCustomerAddress(id)
    address = [dict(a) for a in address if a]
    return jsonify(address)
    return jsonify([])

@customers.route('/api/customer/<id>/address/new', methods=['POST'])
def postAddress(id):
    customerId = id
    addressLine1 = request.form.get('addressLine1')
    addressLine2 = request.form.get('addressLine2')
    city = request.form.get('city')
    state = request.form.get('state')
    postalCode = request.form.get('postalCode')
    country = request.form.get('country')
    addressType = request.form.get('addressType')
    isPrimary = request.form.get('isPrimary')
    isPrimary = 1 if isPrimary == 'Yes' else 0
    id = Db.createCustomerAddress(customerId,addressLine1,addressLine2,city,state,postalCode,country,addressType,isPrimary)
    if id:
        return jsonify({'error': False, 'message': 'Created.'}),201    
    else:
        return jsonify({'error': True, 'message': 'Bad Request'}),400

@customers.route('/api/customer/<custId>/address/edit', methods=['POST'])
def putAddress(custId):
    id = request.form.get('id')
    customerId = custId
    addressLine1 = request.form.get('addressLine1')
    addressLine2 = request.form.get('addressLine2')
    city = request.form.get('city')
    state = request.form.get('state')
    postalCode = request.form.get('postalCode')
    country = request.form.get('country')
    addressType = request.form.get('addressType')
    isPrimary = request.form.get('isPrimary')
    isPrimary = 1 if isPrimary == 'Yes' else 0

    if id and addressLine1 and addressLine2 and postalCode and city and country:
        address = Db.getCustomerAddressBy(id)
        if address:
            _id = Db.updateustomerAddress(id,customerId,addressLine1,addressLine2,city,state,postalCode,country,addressType,isPrimary)
            if _id:
                return jsonify({'error': False, 'message': 'Created.'}),201    
            else:
                return jsonify({'error': True, 'message': 'Bad Request'}),400        
        return jsonify({'error': True, 'message': 'Not Found'}),404    
    return jsonify({'error': True, 'message': 'Bad Request'}),400          

@customers.route('/api/customer/<custId>/address/delete', methods=['POST'])
def deleteAddress(custId):
    id = request.form.get('addressId')
    if custId and id:
        Db.deleteCustomerAddress(id,custId)
        return jsonify({'error': False, 'message': 'Deleted.'}),200   
    return jsonify({'error': True, 'message': 'Bad Request'}),400   
