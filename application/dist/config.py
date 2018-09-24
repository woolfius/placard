import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'hr_portal-secret')

DC_SERVER = os.environ.get('DC_SERVER', '10.22.33.101')

BASE_DN = os.environ.get('BASE_DN', 'DC=busmarket,DC=ua')

DC_USERNAME = os.environ.get('DC_USERNAME', 'hrportal@busmarket.ua')
DC_PASSWORD = os.environ.get('DC_PASSWORD', '14789632Ss')

USERNAME = os.environ.get('MYSQL_ROOT_USER', 'hrportal_dev')

DB_NAME = os.environ.get('MYSQL_DB_NAME', 'db_hrportal_dev')
PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD', 'PhkSQd2?ln')
PORT = os.environ.get('MYSQL_PORT_3306_TCP_PORT', 3306)
SERVER = os.environ.get('MYSQL_PORT_3306_TCP_ADDR', 'mysql.busmarket.ua')

# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@{server}:{port}/{db_name}?charset=utf8'.format(
#     username=USERNAME, password=PASSWORD, server=SERVER, port=int(PORT), db_name=DB_NAME)
# SQLALCHEMY_POOL_SIZE = 5
# SQLALCHEMY_POOL_TIMEOUT = 3
# SQLALCHEMY_POOL_RECYCLE = 120
# SQLALCHEMY_MAX_OVERFLOW = 10
# SQLALCHEMY_ECHO = False

PFX_PASSWORD = os.environ.get('PFX_PASSWORD', '14789632Ss')

mail_server = os.environ.get('MAIL_SERVER', 'mail.busmarket.ua')
mail_port = os.environ.get('MAIL_PORT', 587)
mail_use_ssl = os.environ.get('MAIL_USE_SSL', True)
mail_username = os.environ.get('MAIL_USERNAME', 'hr@busmarket.ua')
mail_password = os.environ.get('MAIL_PASSWORD', '(y5An[UE<Y')

WSDL = os.environ.get('WSDL', 'http://10.22.33.29/busmarket_rusin/ws/hr_portal.1cws?wsdl')

Authorization_password = os.environ.get('AUTHORIZATION_PASSWORD', '+%8v%SrTr8bf3$ZH')
VIRTUAL_HOST = os.environ.get('VIRTUAL_HOST', '')

DEBUG = os.environ.get('DEBUG', False)
