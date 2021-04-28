import os
import re
import uuid

from farmsync.config import *
from farmsync.s3_helper import *
from farmsync import utility as util
from farmsync import models

class User(object):
    def __init__(self, params={}):
        self.username = params.get('username')
        self.phone = params.get('phone')
        self.email = params.get('email')
        self.state = params.get('state')
        self.region = params.get('region')
        self.country = params.get('country')
        self.password = params.get('password')
        self.role = params.get('role')
	
    def register(self):
        msg = ""
        try:
            # Check if account exists using MySQL
            user_exist = self._user_exist()
            if user_exist:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', self.email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', self.username):
                msg = 'Username must contain only characters and numbers!'
            elif not self.username or not self.password or not self.email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into users table
                user_params = {
                            'username': self.username,
                            'user_phone': self.phone,
                            'user_email': self.email,
                            'state': self.state,
                            'region': self.region,
                            'user_password': self.password,
                            'user_uuid': str(uuid.uuid4()),
                            'user_role': self.role
                        }
                user_obj = models.FSUser(**user_params)
                util.add_query(user_obj)
                util.commit_query()
                util.logging.info("Successfully registered user: {}".format(self.username))
                msg = 'You have successfully registered!'
        except Exception as e:
            raise Exception("Failed to register user with error: {}".format(str(e)))
        return msg

    def login(self):
        try:
            user = models.FSUser.query \
                    .filter(models.FSUser.username==self.username) \
                    .filter(models.FSUser.user_password==self.password).one()
            if not user:
                return {'message': 'Failed to get user: {}'.format(self.username)}
            return user
        except Exception as e:
            raise Exception("Failed to get user with error: {}".format(str(e)))

    def get_user_by_id(self, user_pk_id):
        try:
            user = models.FSUser.query.filter_by(user_id=int(user_pk_id)).one()
            if not user:
                return {'message': 'User record for id :{} not available'.format(str(user_pk_id))}
            return user
        except Exception as e:
            raise Exception("Failed to get user record with error: {}".format(str(e)))

    def _user_exist(self):
        try:
            user = models.FSUser.query.filter(models.FSUser.username==self.username).one_or_none()
            return user
        except Exception as e:
            raise Exception("Failed to get user with error: {}".format(str(e)))
