from datetime import datetime
from flask import Blueprint, jsonify
from Db import Db
from decorators import role_required

orders = Blueprint('orders', __name__, template_folder='templates')

@orders.route('/invoice/<custId>/orderItems', methods=['GET'])
@role_required('Admin')
def getOrderItems(custId):
    if custId:
        items = Db.getCustProdsOrders(custId)
        items = [dict(item) for item in items if item]
        return jsonify(items)
    return jsonify({ 'error': True, 'message': 'Bad Request' })

@orders.route('/invoice/<custId>/order', methods=['GET'])
@role_required('Admin')
def getOrderSipping(custId):
    if custId:
        client = Db.getCustomerSipping(custId)
        client = dict(client)
        client['invNumber'] = generateInvoiceNumber(custId)

        return jsonify(client)
    return jsonify({ 'error': True, 'message': 'Bad Request' })

def generateInvoiceNumber(custId):
    length = custId.index("-") - 1 
    custId = custId[0:length]

    now = datetime.datetime.now()
    return f"INV-{now.strftime('%Y%m%d')}-{custId:03d}" 