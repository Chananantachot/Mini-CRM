from flask import Blueprint, jsonify,request
from Db import Db
from decorators import role_required

products = Blueprint('products', __name__, template_folder='templates')

@products.route('/api/products', methods=['GET'])
def getProducts():
    prods = Db.getProducts()
    products = [dict(p) for p in prods if p]
    return jsonify(products)

@products.route('/api/product/new', methods=['POST'])
def postProduct():
    name  = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    sku = request.form.get('sku')
    category = request.form.get('category')
    isActive = request.form.get('isActive')

    if name:
        skuPord = Db.getProductBy(sku)
        if skuPord:
            return jsonify({ 'error': True, 'message': f'Product {sku} already exist.' }), 400
        id = Db.createProduct(name,description,price,sku,category,isActive)
        if id:
            return jsonify({ 'error': False, 'message': 'Created' }), 201
        return jsonify({ 'error': True, 'message': 'Falied' }), 400
    return jsonify({ 'error': True, 'message': 'Bad Request' }), 400

@products.route('/api/product/<id>/edit', methods=['POST'])
def putProduct(id):
    name  = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    sku = request.form.get('sku')
    category = request.form.get('category')
    isActive = request.form.get('isActive')

    if id and name:
        prod = Db.getProduct(id)
        if prod:
            return jsonify({ 'error': True, 'message': f'Not Found' }), 404
        
        skuPord = Db.getProductBy(sku)
        if skuPord:
            return jsonify({ 'error': True, 'message': f'Product {sku} already exist.' }), 400
        
        id = Db.updateProduct(id,name,description,price,sku,category,isActive)
        if id:
            return jsonify({ 'error': False, 'message': 'Updated.' }), 204
        return jsonify({ 'error': True, 'message': 'Failed.' }), 400
    return jsonify({ 'error': True, 'message': f'Bad Request.' }), 400     
