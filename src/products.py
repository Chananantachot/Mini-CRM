from flask import Blueprint, jsonify,request
from Db import Db
from decorators import role_required

products = Blueprint('products', __name__, template_folder='templates')

@products.route('/api/products', methods=['GET'])
def getProducts():
    prods = Db.getProducts()
    products = [dict(p) for p in prods if p]
    return jsonify(products)

@products.route('/api/products/lead/interested', defaults={'id': None} , methods=['GET'])
@products.route('/api/products/lead/<id>/interested', methods=['GET'])
def getProductsLeadInterested(id):
    searchField = request.args.get('searchField')
    searchString = request.args.get('searchString')
    searchOper = request.args.get('searchOper')

    prodsIntested = Db.getleadProdsInterested(id)
    products = [dict(p) for p in prodsIntested if p]

    if searchField and searchOper:
        results  = []
        match searchOper:
            case 'eq':
                results = list(filter(lambda p: str(p[searchField]) == searchString, products))
            case 'ne':
                results = list(filter(lambda p: str(p[searchField]) != searchString, products))
            case 'bw':
                results = list(filter(lambda p: str(p[searchField]).startswith(searchString), products))
            case 'bn':
                results = list(filter(lambda p: not str(p[searchField]).startswith(searchString), products))
            case 'ew':
                results = list(filter(lambda p: str(p[searchField]).endswith(searchString), products))
            case 'en':
                results = list(filter(lambda p: not str(p[searchField]).endswith(searchString), products))
            case 'cn':
                results = list(filter(lambda p: searchString in str(p[searchField]), products))
            case 'nc':
                results = list(filter(lambda p: searchString not in str(p[searchField]), products))
            case 'nu': # is null case
                results = list(filter(lambda p: str(p[searchField]) == None, products))
            case _:
                results = products
    else:           
        results = products

    return jsonify(results)

@products.route('/api/product/interested', methods=['POST'])
def postPorductsInterested():
    ids = request.form.getlist('ids[]')
    leadId = request.form.get('leadId')

    Db.deleteLeadProdsInterested(leadId)
    
    if ids and leadId:
        for prodId in ids:
           id = Db.createLeadProdsInterested(leadId,prodId)
        if id:
            return jsonify({ 'error': False, 'message': 'created' }),201
        else:
            return jsonify({ 'error': True, 'message': 'Failed' }),400
    return jsonify({ 'error': True, 'message': 'Bad Request' }),400
        

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
