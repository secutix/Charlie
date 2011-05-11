from suds.client import Client, WebFault
from django.core import serializers
import config
import models
from django.contrib.auth.models import User
from django.conf import settings

class Jiraconnection(object):
    def __init__(self, visa, password):
        self.jirauser = visa
        self.passwd = password
        client = Client(config.jira_server_url)
        self.success = False
        try:
            self.auth = client.service.login(self.jirauser, self.passwd)
            self.success = True
        except WebFault as detail:
            self.success = False

class CustomAuthBackend:
    supports_object_permissions = True
    supports_anonymous_user = False
    def get_user(self, uid):
        try:
            return User.objects.get(pk = uid)
        except User.DoesNotExist:
            return None
    def authenticate(self, user_name=None, password=None):
        jc = Jiraconnection(user_name, password)
        if jc.success:
            try:
                user = User.objects.get(username = user_name, is_active = True)
                return user
            except User.DoesNotExist:
                user = User(username=user_name)
                user.set_unusable_password()
                user.save()
                u = User.objects.get(username = user_name)
                return u
        else:
            return None

class FormIsOk(object):
    def __init__(self, ok):
        self.success = ok
    class Meta:
        pass

class JsonCreator(object):
    def __init__(self, obj):
        self.data = serializers.serialize("json", [obj])
    def get_data(self):
        return self.data
