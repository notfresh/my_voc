from flask import Blueprint

voc = Blueprint('voc', __name__, url_prefix='/voc')
from . import views