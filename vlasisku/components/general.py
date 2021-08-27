
from flask import Blueprint, send_file, render_template


general = Blueprint('general', __name__, template_folder='templates') 

@general.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')


@general.route('/custom.js')
def javascript():
    return render_template('custom.js')
