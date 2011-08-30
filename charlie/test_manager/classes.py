from suds.client import Client, WebFault
import config
from django.contrib.auth.models import User, Permission
import logging
import datetime

class Jiraconnection(object):
    """
        opens a connection to jira using suds client
    """
    def __init__(self, visa, password):
        self.jirauser = visa
        self.passwd = password
        client = Client(config.jira_server_url)
        self.success = False
        try:
            self.auth = client.service.login(self.jirauser, self.passwd)
            self.success = True
        except Exception:
            self.success = False

class CustomAuthBackend:
    """
        manages user authentication on charlie.
        users don't store their password on charlie. the password is only used to authenticate them on jira.
    """
    supports_object_permissions = True
    supports_anonymous_user = False
    def get_user(self, uid):
        """
            compulsory method for an authentication backend. used to retrieve a user whose id is provided.
        """
        try:
            return User.objects.get(pk = uid)
        except User.DoesNotExist:
            return None
    def authenticate(self, user_name=None, password=None):
        """
            check if the password is good by authenticating on jira
        """
        jc = Jiraconnection(user_name, password)
        if jc.success:
            try:
                user = User.objects.get(username = user_name, is_active = True)
                try:
                    user.cust_auth = jc.auth
                except Exception:
                    pass
                return user
            except User.DoesNotExist:
                user = User(username=user_name)
                user.set_unusable_password()
                user.save()
                u_permissions = [
                    'change_availability',
                    'add_jira',
                    'change_jira',
                    'change_testcaserun',
                    'change_testcasesteprun',
                ]
                for p in u_permissions:
                    pm = Permission.objects.get(codename = p)
                    user.user_permissions.add(pm)
                user.save()
                u = User.objects.get(username = user_name)
                u.cust_auth = jc.auth
                return u
        else:
            try:
                user = User.objects.get(username = user_name, is_active = True)
                if user.check_password(password):
                    return user
                else:
                    return None
            except Exception as detail:
                logging.error('an error occured : %s' % detail)
                return None
