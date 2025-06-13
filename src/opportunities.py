import uuid
from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required
from Db import Db
from decorators import role_required

opportunities = Blueprint('opportunities', __name__, template_folder='templates')

@opportunities.route('/api/opportunities/<leadId>', methods=['GET'])
@role_required('Admin')
def getOpportunities(leadId):
    opportunities = Db.getOpportunities(leadId)
    responses =  [dict(opportunity) for opportunity in opportunities if opportunity]
    return jsonify(responses)

@opportunities.route('/api/<lead_id>/opportunities/new', methods=['POST'])
@role_required('Admin')
def create(lead_id):
    leadId = lead_id #request.form.get('lead_id')
    current_stage = request.form.get('current_stage')
    expected_value = request.form.get('expected_value')
    closure_date = request.form.get('closure_date')
    converted = request.form.get('converted')

    if leadId: 
      id =  Db.createOpportunities(leadId,current_stage,expected_value,closure_date,converted)
      if id:
          if converted == 'Yes':
              Db.updateLeadStatus(leadId,'Converted')  

          return jsonify({ 'error': False, 'message': 'Created' }), 201  
    return jsonify({ 'error': True, 'message': 'Bad Request' }), 400   

@opportunities.route('/api/opportunities/edit', methods=['POST'])
@role_required('Admin')
def edit():
    id = request.form.get('id')
    leadId = request.form.get('lead_id')
    current_stage = request.form.get('current_stage')
    expected_value = request.form.get('expected_value')
    closure_date = request.form.get('closure_date')
    converted = request.form.get('converted')
    if id:
       lead =  Db.getLead(id)
       if lead:
           Db.updateOpportunities(id,leadId,current_stage,expected_value,closure_date,converted)
           return jsonify({ 'error': False, 'message': 'Created' }), 204  
       else:
        return jsonify({ 'error': True, 'message': 'Not Found' }), 404
    else:   
        return jsonify({ 'error': True, 'message': 'Bad Request' }), 400      