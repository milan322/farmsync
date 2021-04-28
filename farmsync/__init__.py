import os
from datetime import datetime
from flask import Flask

def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug

    return app

app = create_app(debug=os.getenv('DEBUG', False))

__title__ = 'HyperTracker'
__version__ = '0.0.1'
__author__ = 'Corteva'
__author_email__ = ''
__license__ = 'Proprietary, (c) Corteva'
__copyright__ = '(c) {}'.format(datetime.now().year)
__url__ = ''
__description__ = """
A Flask-based API
"""
