from flask import Blueprint, jsonify,request
from Db import Db
from decorators import role_required

products = Blueprint('products', __name__, template_folder='templates')