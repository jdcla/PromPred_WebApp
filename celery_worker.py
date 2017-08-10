#!/home/jim/.conda/envs/flask/bin/python

import os
from app import celery, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()