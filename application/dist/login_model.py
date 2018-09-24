from flask_login import UserMixin
from ldap_utils import authenticate


class User(UserMixin):

    def __init__(self, login):
        self.login = login

    def get_id(self):
        return self.login

    def check_password(self, password):
        return authenticate(self.login, password)

