import os

app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    DEBUG = True
    POSTGRES_URL="techconferencedb.postgres.database.azure.com"  
    POSTGRES_USER="dbadmin@techconferencedb" 
    POSTGRES_PW="udacity123$"
    POSTGRES_DB="techconfdb"
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or DB_URL
    CONFERENCE_ID = 1
    SECRET_KEY = 'LWd2tzlprdGHCIPHTd4tp5SBFgDszm'
    SERVICE_BUS_CONNECTION_STRING ='Endpoint=sb://techconferenceservicebus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=AIcrJo8hsoBWZz+ic9rh1WnoPUvZp37MvFwl7ddhT2o='
    SERVICE_BUS_QUEUE_NAME ='notificationqueue'
    ADMIN_EMAIL_ADDRESS: 'nihithreddy9618@gmail.com'
    SENDGRID_API_KEY = '' #Configuration not required, required SendGrid Account
    REDIS_HOST = 'usersessioncache.redis.cache.windows.net'
    REDIS_PASSWORD = 'dnxBl88fPuGXR7lkvGU5n2ogY3n83schTAzCaPorlbA='

class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False