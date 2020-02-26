import os
from dotenv import load_dotenv
load_dotenv()


basedir = os.path.abspath(os.path.dirname(__file__))

##### backend url for development flask runs on port 5000.


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False



class DbEngine_config():
    DB_DIALECT = os.environ.get('DB_DIALECT') or 'postgresql'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASS = os.environ.get('DB_PASS') or 'postgres'
    DB_NAME = os.environ.get('DB_NAME') or 'ihomedb'
    if int(os.environ.get('APP_HEROKU')) == 1:
        DB_URL = "postgres://buqljeciiourcf:8d5e087dd3d2beb39803b56773ff0ab08967dab3e99a1dc3d40e23dc6bbe9bd8@ec2-107-21-101-177.compute-1.amazonaws.com:5432/db1deb1elaluet"
    if int(os.environ.get('SQLITE')) == 1:
        db_path = os.path.join(os.path.dirname(__file__), 'ihome.db')
        print(db_path)
        DB_URL = 'sqlite:///{}'.format(db_path)
        #DB_URL = "sqlite:///data/ihome.db"
    else:
        #DB_URL = "postgres://postgres:studypasszoom@studyzoom:5432/canteenzoom"
        DB_URL = f'{DB_DIALECT}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base