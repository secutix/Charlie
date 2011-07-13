from suds.client import Client, WebFault
import config
from django.contrib.auth.models import User, Permission
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
        except WebFault as detail:
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
                return u
        else:
            try:
                user = User.objects.get(username = user_name, is_active = True)
                if user.check_password(password):
                    return user
                else:
                    return None
            except Exception:
                return None

class SContext(object):
    """
    Design pattern Strategy : context
    """
    def __init__(self, av, tc):
        strat = SStrategyNaive(tc, av)
        self.tr = strat.tr

class SStrategy(object):
    """
    Design pattern Strategy : abstract class of strategy
    """
    class Meta:
        abstract = True
    def solve(self):
        """
        Solve the scheduling problem
        """
        return

class SStrategyNaive(SStrategy):
    """
    Naive method
    """
    def __init__(self, test_runs, availabilities):
        self.tr = sorted(test_runs, key = lambda tr: tr['w'], reverse = True)
        av = sorted(availabilities, key = lambda a: a['d'])
        for t in self.tr:
            targets = []
            for a in av:
                if t['w'] < a['rem'] and t['g'] == False:
                    if len(targets) > 0:
                        if a['d'] == targets[0]['d']:
                            targets.append(a)
                        else:
                            pass
                    else:
                        targets.append(a)
                else:
                    pass
            try:
                min_occup = targets[0]
                for a in targets:
                    if a['rem'] > min_occup['rem']:
                        min_occup = a
                    else:
                        pass
                t['x'] = min_occup['d']
                t['u'] = min_occup['usr']
                min_occup['rem'] -= t['w']
                t['g'] = True
            except IndexError:
                pass
