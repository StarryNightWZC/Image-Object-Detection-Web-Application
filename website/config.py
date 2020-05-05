import os
basedir = os.path.abspath(os.path.dirname(__file__))

def get_instanceId():
    return os.popen('ec2metadata --instance-id').read().strip()

class Config(object):
    SECRET_KEY = 'ece1779-a2-secretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql://ece1779database:ece1779database@ece1779database.cpt3hodccygr.us-east-1.rds.amazonaws.com/testtable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = basedir + '/static/images'
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
    BUCKET_NAME = 'ece1779-s3-images'
    # INSTANCE_ID = get_instanceId()
    INSTANCE_ID = 'ece1779finalproject'
    ZONE = 'Canada/Eastern'