import os
import tempfile

class Config(object):
    DEBUG = True
    LANGUAGES = ['en', 'te', 'fr', 'hi']

AWS_REGION = "us-east-1"
S3_BUCKET = "farmsync"

# S3 directories
S3_IMAGE_DIR = "images"

# Temp dir
TEMP_DIR = tempfile.gettempdir()

# Database
DB_USER_NAME = "root"
DB_PASSWORD = ""
DB_ENDPOINT = "localhost:3306"
DB_NAME = "fsdata"

# SQLAlchemy properties
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Temporary using AWS Credentials. Not a good practice
AWS_ACCESS_KEY_ID = "AKIA2VPIMYYQEA62UVJZ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "ap-south-1"
S3_BUCKET = "milan-project-data"
