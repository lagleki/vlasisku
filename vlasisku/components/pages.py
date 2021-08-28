
from flask import Blueprint, current_app, render_template

from vlasisku.utils import etag

pages = Blueprint('pages', __name__, template_folder='templates') 

@pages.route('/help')
@etag
def help():
    return render_template('help.html', website=current_app.config['WEBSITE'])
