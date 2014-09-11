
from flask import Module, current_app
from flaskext.genshi import render_response

from vlasisku.utils import etag

pages = Module(__name__)


@pages.route('/help')
@etag
def help():
    return render_response('help.html', {'website': current_app.config['WEBSITE']})
