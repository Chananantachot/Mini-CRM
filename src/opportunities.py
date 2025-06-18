from flask import Blueprint, jsonify,request
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
    leadId = lead_id
    current_stage = request.form.get('current_stage')
    expected_value = request.form.get('expected_value')
    closure_date = request.form.get('closure_date')
    converted = request.form.get('converted')

    if leadId: 
      id =  Db.createOpportunities(leadId,current_stage,expected_value,closure_date)
      if id:
        if converted == 'Yes':
            lead = Db.getLead(lead_id)
            #lead = dict(lead)
            Db.covertLeadToCustomer(leadId,lead['firstName'], lead['lastName'], lead['email'], lead['mobile'])
        
        return jsonify({ 'error': False, 'message': 'Created' }), 201  
    return jsonify({ 'error': True, 'message': 'Bad Request' }), 400   

@opportunities.route('/api/<lead_id>/opportunities/edit', methods=['POST'])
@role_required('Admin')
def edit(lead_id):
    leadId = lead_id
    opportunityId  = request.form.get('id')
    current_stage = request.form.get('current_stage')
    expected_value = request.form.get('expected_value')
    closure_date = request.form.get('closure_date')
    converted = request.form.get('converted')
    if opportunityId and leadId:
        opportunity = Db.getOpportunity(opportunityId,lead_id)
        opportunity = dict(opportunity)
        if opportunity:
            lead =  Db.getLead(lead_id)
            if lead:
                if converted == 'Yes':
                    #lead = dict(lead)
                    custId = Db.covertLeadToCustomer(leadId, lead['firstName'], lead['lastName'], lead['email'], lead['mobile'])
                else:  
                    custId = Db.updateOpportunities(opportunityId,leadId,current_stage,expected_value,closure_date)
                    
                if custId:
                    return jsonify({ 'error': False, 'message': 'Updated' }), 204  
                else:
                    return jsonify({ 'error': True, 'message': 'Failed' }), 400  
            else:
                return jsonify({ 'error': True, 'message': 'Not Found' }), 404         
        else:
            return jsonify({ 'error': True, 'message': 'Not Found' }), 404
    else:   
        return jsonify({ 'error': True, 'message': 'Bad Request' }), 400      