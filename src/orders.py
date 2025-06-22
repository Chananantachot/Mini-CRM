from datetime import datetime
import hashlib
import time
import uuid
from flask import Blueprint, jsonify, request
from Db import Db
from decorators import role_required

orders = Blueprint('orders', __name__, template_folder='templates')

@orders.route('/invoice/<custId>/orderItems', defaults ={'orderId': None } , methods=['GET'])
@orders.route('/invoice/<custId>/orderItems/<orderId>', methods=['GET'])
@role_required('Admin')
def getOrderItems(custId, orderId):
    if custId:
        items = Db.getCustProdsOrders(custId, orderId)
        items = [dict(item) for item in items if item]
        return jsonify(items)
    return jsonify({ 'error': True, 'message': 'Bad Request' })


@orders.route('/invoice/<custId>/orderDetails', methods=['GET'])
@role_required('Admin')
def getOrderDetails(custId):
    orderDetails =  Db.getCustomerInvoiceDetail(custId)
    orderDetails = [dict(order) for order in orderDetails if order]
    return jsonify(orderDetails)

@orders.route('/invoice/<custId>/order', defaults = {'orderId' : None} , methods=['GET'])
@orders.route('/invoice/<custId>/order/<orderId>', methods=['GET'])
@role_required('Admin')
def getOrder(custId,orderId):
    if custId:
        address = Db.getCustomerPrimaryAddress(custId)
        if address:
            orders = Db.getCustomerOrder(custId,orderId)
            orders = [dict(order) for order in orders if order]
            order = orders[0]
            if not order['invNumber']:
                order['invNumber'] = generateInvoiceNumber(custId)

            return jsonify(orders)
        return jsonify({ 'error': True, 'message': 'Not Found' }), 404   
    return jsonify({ 'error': True, 'message': 'Bad Request' }), 400

@orders.route('/check/<custId>/orderLeft', methods=['GET'])
@role_required('Admin')
def getOrderLeft(custId):
    if not custId:
        return jsonify({ 'error': True, 'message': 'Bad Request' }), 400
    
    getOrderLeft = Db.getCustomerInvoiceLeftInProdInterested(custId)
    getOrderLeft = [dict(order) for order in getOrderLeft if order]
    return jsonify(getOrderLeft),200


@orders.route('/invoice', methods = ['POST'])
@role_required('Admin')
def postOrder():
    if request.is_json: 
        invoice = request.get_json() 
        order = invoice.get('order')
        orderItems = invoice.get('orderItems')

        orderId = str(uuid.uuid4())
        order_value = (orderId,
            order['invNumber'],
            order['customerId'],
            float(order['amount']),
            float(order['tax']),
            float(order['total']),
            order['status'],
            order['shippingAddress'],
            order['billingAddress']
        )

        orderItems_value = [
            (str(uuid.uuid4()), 
             orderId, 
             item["productId"], 
             int(float(item["quantity"])), 
             float(item["unitPrice"]))
            for item in orderItems
        ]
        id = Db.createOrder(order_value,orderItems_value)
        if id:
            return jsonify({ 'error': False, 'message': 'Created' , 'id': orderId }), 201 
        return jsonify({ 'error': True, 'message': 'Failed' }), 400   
    else:    
        return jsonify({ 'error': True, 'message': 'Bad Request' }), 400    

@orders.route('/invoice', methods = ['PUT'])
@role_required('Admin')
def putOrder():
    if request.is_json: 
        invoice = request.get_json() 
        order = invoice.get('order')
        orderItems = invoice.get('orderItems')

        order_value = (
            float(order['amount']),
            float(order['tax']),
            float(order['total']),
            order['status'],
            order['shippingAddress'],
            order['billingAddress'],
            order['orderId'],
            order['customerId']
        )

        orderItems_value = [
            (int(float(item["quantity"])), 
             float(item["unitPrice"]),
             order['orderId'], 
             item["productId"])
            for item in orderItems
        ]
        
        id =  Db.updateOrder(order_value,orderItems_value)
        if id:
            return jsonify({ 'error': False, 'message': 'Updated', 'id': id}), 204
        return jsonify({ 'error': True, 'message': 'Failed' }), 400   
    else:    
        return jsonify({ 'error': True, 'message': 'Bad Request' }), 400    

@orders.route('/invoice/<orderID>/updateOrderStatus', methods=['PUT'])
@role_required('Admin')
def updateOrderStatus(orderID):
    if request.is_json:
        data = request.get_json()
        status = data.get('status')
        if not status:
            return jsonify({'error': True, 'message': 'Status is required'}), 400
        
        updated = Db.updateOrderStatus(orderID, status)
        if updated:
            return jsonify({'error': False, 'message': 'Order status updated successfully'}), 200
        return jsonify({'error': True, 'message': 'Failed to update order status'}), 400
    return jsonify({'error': True, 'message': 'Bad Request'}), 400

def generateInvoiceNumber(custId):    
    base = f"{custId}-{time.time()}"
    return "INV-" + hashlib.md5(base.encode()).hexdigest()[:10]