import datetime
from flask import Blueprint, Response, jsonify, make_response, request, url_for
import xml.etree.ElementTree as ET
from Db import Db
from audit import AuditAction, log_audit
from decorators import role_required

products = Blueprint('products', __name__, template_folder='templates')

# --- Helper Function to Convert Python Dictionary/List to XML ---
def dict_to_xml(tag, d):
    """
    Converts a dictionary or a list of dictionaries to an XML ElementTree element.
    This is a recursive function to handle nested structures.

    Args:
        tag (str): The root tag name for the XML element.
        d (dict or list): The data to convert.

    Returns:
        xml.etree.ElementTree.Element: The created XML element.
    """
    elem = ET.Element(tag)
    if isinstance(d, dict):
        for key, val in d.items():
            if isinstance(val, (dict, list)):
                # If value is a dictionary or list, recursively create a child element
                elem.append(dict_to_xml(key, val))
            else:
                # Otherwise, set as text content of a child element
                child = ET.SubElement(elem, key)
                child.text = str(val)
    elif isinstance(d, list):
        # If it's a list, create multiple child elements with a generic name (e.g., 'item')
        # You might want to customize this based on the list's content
        for item in d:
            elem.append(dict_to_xml("item", item)) # Using 'item' as a generic tag for list items
    return elem

@products.route('/products/rs')
def productsFeed():
    prods = Db.getProducts()
    products = [dict(p) for p in prods if p]
    feed = Rss201rev2Feed(
        title='Products',
        link='https://mini-crm.xyz',
        description='Our Products',
    )

    for prodcut in products:
        feed.add_item(
            title=prodcut['name'],
            link=f'https://mini-crm.xyz/{prodcut['sku']}',
            description=prodcut['description'],
            pubdate=datetime.date.today(),
            author_email='atip.cha22@gmail.com',
            author_name="Chananantachot,ATIP ",
            categories=prodcut['category']
        )
    
    # Generate the raw RSS XML string
    # ET.tostring provides a clean XML declaration.
    raw_xml_string = feed.writeString('utf-8')

    # Construct the URL for your XSLT stylesheet.
    # url_for('static', filename='rss_style.xsl') will generate a URL like /static/rss_style.xsl
    # You need to ensure your Flask app correctly serves static files.
    xslt_url = url_for('static', filename='rss_style.xsl', _external=True) 

    # _external=True for full URL if needed by client
    # Insert the processing instruction right after the XML declaration
    # The xml_declaration is <?xml version="1.0" encoding="utf-8"?>
    # The processing instruction must come immediately after it.
    xslt_processing_instruction = f'<?xml-stylesheet type="text/xsl" href="{xslt_url}"?>\n'

    # Find the position to insert the PI (after the XML declaration)
    # The XML declaration typically ends with '?>'
    xml_declaration_end_index = raw_xml_string.find('?>')
    if xml_declaration_end_index != -1:
        # Insert the PI after the XML declaration and its newline
        insert_index = xml_declaration_end_index + len('?>') + 1 # +1 for potential newline
        modified_xml_string = raw_xml_string[:insert_index] + xslt_processing_instruction + raw_xml_string[insert_index:]
    else:
        # Fallback if XML declaration not found (unlikely for feedgen)
        modified_xml_string = xslt_processing_instruction + raw_xml_string

    response = make_response(modified_xml_string)
    
    # It's better to stick to one Content-Type, 'application/rss+xml' is specific
    # 'text/xml' is also valid, but 'application/rss+xml' is more precise.
    response.headers.set('Content-Type', 'application/rss+xml')
    response.headers.set('Content-Type', 'text/xml') # Remove this if you prefer application/rss+xml
    response.headers.set('X-Content-Type-Options', 'nosniff') # Good practice

    return response

@products.route('/api/products', methods=['GET'])
@role_required('Admin')
def getProducts():
    prods = Db.getProducts()
    products = [dict(p) for p in prods if p]
    return jsonify(products)

@products.route('/api/xml/products', methods=['GET'])
@role_required('Admin')
def getXMLProducts():
    prods = Db.getProducts()
    products = [dict(p) for p in prods if p]
     # Create the root element for the XML response
    root = ET.Element("rows")

    for product in products:
    # Create a 'product' element for each item in the list
        product_elem = dict_to_xml("row", product)
        root.append(product_elem)
   
    # Convert the ElementTree to a string
    xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

    # Return the XML string with the appropriate Content-Type header
    return Response(xml_string, mimetype='application/xml')

@products.route('/api/products/lead/interested', defaults={'id': None} , methods=['GET'])
@products.route('/api/products/lead/<id>/interested', methods=['GET'])
@role_required('Admin')
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
@role_required('Admin')
def postPorductsInterested():
    ids = request.form.getlist('ids[]')
    leadId = request.form.get('leadId')
    currents = Db.getleadProdsInterested(leadId)

    currents =  [c['id'] for c in currents if c['interested'] == 1]
    addIDs = [id for id in ids if id not in currents]
    removeIDs = [id for id in currents if id not in ids]           
   
    if ids and leadId:
        for prodId in removeIDs:
            Db.deleteLeadProdsInterested(leadId,prodId)
    
        for prodId in addIDs:
           id = Db.createLeadProdsInterested(leadId,prodId)

        log_audit(action=AuditAction.INSERT,
            table_name='leadProdsInterested',
            record_id= leadId,
            old_value=jsonify(currents),
            new_value=jsonify(addIDs))   
        if id:
            return jsonify({ 'error': False, 'message': 'created' }),201
        else:
            return jsonify({ 'error': True, 'message': 'Failed' }),400
    return jsonify({ 'error': True, 'message': 'Bad Request' }),400
        
@products.route('/api/product/new', methods=['POST'])
@role_required('Admin')
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

        log_audit(action=AuditAction.INSERT,
            table_name='products',
            record_id= id,
            old_value=None,
            new_value=jsonify({'name': name, 'description': description, 'price': price, 'sku': sku, 'category': category, 'isActive': isActive })) 
        if id:
            return jsonify({ 'error': False, 'message': 'Created' }), 201
        return jsonify({ 'error': True, 'message': 'Falied' }), 400
    return jsonify({ 'error': True, 'message': 'Bad Request' }), 400

@products.route('/api/product/<id>/edit', methods=['POST'])
@role_required('Admin')
def putProduct(id):
    name  = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    sku = request.form.get('sku')
    category = request.form.get('category')
    isActive = request.form.get('isActive')

    if id and name:
        prod = Db.getProduct(id)
        prod =dict(prod)
        if prod:
            return jsonify({ 'error': True, 'message': f'Not Found' }), 404
        
        skuPord = Db.getProductBy(sku)
        if skuPord:
            return jsonify({ 'error': True, 'message': f'Product {sku} already exist.' }), 400
        
        id = Db.updateProduct(id,name,description,price,sku,category,isActive)
        log_audit(action=AuditAction.UPDATE,
            table_name='products',
            record_id= id,
            old_value=jsonify(prod),
            new_value=jsonify({'name': name, 'description': description, 'price': price, 'sku': sku, 'category': category, 'isActive': isActive }))   
              
        if id:
            return jsonify({ 'error': False, 'message': 'Updated.' }), 204
        return jsonify({ 'error': True, 'message': 'Failed.' }), 400
    return jsonify({ 'error': True, 'message': f'Bad Request.' }), 400     
