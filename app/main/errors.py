from flask import render_template
from . import err

@err.app_errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@err.app_errorhandler(403)
def forbidden(error):
    return "<h1>Unauthorized Access</h1>", 403
