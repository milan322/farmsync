import os
import logging
import shutil
import farmsync.config as cfg
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from farmsync import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


basedir = os.path.abspath(os.path.dirname(__file__))
fs_db = SQLAlchemy(app, session_options={"expire_on_commit": False})

def create_app_mysql(debug=False):
    app.debug = debug
    conn_params = ['mysql+pymysql://',
                   cfg.DB_USER_NAME, ':',
                   cfg.DB_PASSWORD, '@',
                   cfg.DB_ENDPOINT, '/',
                   cfg.DB_NAME]
    conn_str = ''.join(conn_params)
    print(conn_str)
    app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = \
                cfg.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = cfg.SQLALCHEMY_ECHO
    fs_db.init_app(app)
    return app

def create_json_response(message, data, status_code=None):
    if data and isinstance(data, Exception):
        data = ' : '.join([str(data.__class__.__name__), str(data)])
    json_response = jsonify({
                                'status': {'message': message},
                                'data': data
                            })

    if not status_code:
        if message == "Error":
            status_code = 500
        else:
            status_code = 200

    return json_response, status_code

def init_mysql_db():
    """
    Get access to mysql db and create tables using models
    """
    try:
        from farmsync.models import FSUser, FSActivity, FSComments, \
            FSImages, FSFeedback
        fs_db.create_all()
        return "Successfully created DB tables"
    except Exception as e:

        return jsonify({"status": "error", "message": str(e)})

def add_query(query):
    fs_db.session.add(query)

def commit_query():
    fs_db.session.commit()
    fs_db.session.close()

def create_dir(dir):
    try:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)
    except OSError as e:
        raise Exception("Failed to create dir: {} with error: {}" \
            .format(dir, str(e)))

def remove_dir(dir):
    try:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    except OSError as e:
        raise Exception("Failed to remove dir: {} with error: {}" \
            .format(dir, str(e)))

def create_app():
    print("base dr========================", basedir)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
            + os.path.join(basedir, f"{cfg.DB_NAME}.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = \
                cfg.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = cfg.SQLALCHEMY_ECHO
    fs_db.init_app(app)
    
    return app

#create_app_mysql()
create_app()
