
from flask import Blueprint, current_app, json, render_template

from vlasisku.extensions import database

opensearch = Blueprint('opensearch', __name__, template_folder='templates') 

@opensearch.route('/opensearch/')
def opensearch_render():
    return render_template('opensearch.xml')


@opensearch.route('/suggest/<prefix>')
def suggest(prefix):
    cls = current_app.response_class
    return cls(json.dumps(database.root.suggest(prefix)),
               mimetype='application/json')
