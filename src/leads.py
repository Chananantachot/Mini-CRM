import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from Db import Db
from decorators import role_required

leads = Blueprint('leads', __name__, template_folder='templates')

@leads.route('/api/leads',methods=['GET'])
@role_required('Admin')
def getLeads():
    _leads = Db.getLeads()
    responses =  [dict(lead) for lead in _leads if lead]
    return jsonify(responses)

@leads.route('/api/lead/new',methods=['POST'])
@role_required('Admin')
def createLead():
    id = str(uuid.uuid4())
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    source = request.form.get('source')
    status = request.form.get('status')

    if firstName and lastName and email:
         lead = Db.getLeadBy(firstName,lastName)
         if lead:
             return jsonify({ 'error': True, 'message': f'{firstName} {lastName} already exists.' }), 400
         else:
            _id =  Db.createLead(id,firstName,lastName,email,source,status)
            if _id:
                return jsonify({ 'error': False, 'message': 'Created' }), 201
            return jsonify({ 'error': True, 'message': 'Failed' }), 400
    return jsonify({ 'error': True, 'message': 'Bad Request' }), 404   


@leads.route('/api/lead/edit',methods=['POST'])
@role_required('Admin')
def updateLead():
    id = request.form.get('id')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    source = request.form.get('source')
    status = request.form.get('status')

    skipCheckUniqeName = False
    if id:
        lead = Db.getLead(id)
        if lead:
            lead = dict(lead)
            if firstName and lastName and email and lead['firstName'] == firstName and lead['lastName'] == lastName:
                 skipCheckUniqeName =  lead['email'] != email or lead['source'] != source or lead['status'] != status 
        else:
            return jsonify({'error': True, 'message': 'Not Founded.'}),404          
    else:
        return jsonify({'error': True, 'message': 'Bad Request.'}),404   

    isFirstLastUniqe = True
    _lead = None
    if not skipCheckUniqeName:
        _lead = Db.getLeadBy(firstName,lastName)
        isFirstLastUniqe = not _lead

    if isFirstLastUniqe:
        _id =  Db.updateLead(id,firstName,lastName,email,source,status)
        if _id:
            return jsonify({ 'error': False, 'message': 'Updated' }), 204
        return jsonify({ 'error': True, 'message': 'Failed' }), 400
    return jsonify({ 'error': True, 'message': f'{firstName} {lastName} already exists.' }), 400    
