from django.db import models

##########
# Config #
##########
class Config(models.Model):
    ctype = models.CharField(max_length = 200)
    name = models.CharField(max_length = 200)
    value = models.CharField(max_length = 200, unique = True)
    def __unicode__(self):
        return self.value



# wsdl page for logging in to jira
jira_server_url = 'http://jira-stx.elca.ch/jira/rpc/soap/jirasoapservice-v2?wsdl'

# test case creation data (dropdown menus)
def get_tc_data():
    res = {}
    myVars = ['os', 'module', 'envir', 'browser', 'release', 'version']
    for v in myVars:
        res.update({v: []})
        for i in list(Config.objects.filter(ctype = v)):
            res[v].append({'name': i.name, 'value': i.value})
    res.update({'smodule': [{'name': 'Choose a module first !', 'value': None}]})
    res.update({'submodules': {}})
    for m in list(Config.objects.filter(ctype = 'module')):
        res['submodules'].update({m.value: []})
        for s in list(Config.objects.filter(ctype = m.value)):
            res['submodules'][m.value].append({'name': s.name, 'value': s.value})

    return res


# default % of the day that a tester is available to perform tests
default_availability = 60

# scheduling algorithm : 0 is naive, 1 will be a more efficient one
scheduling_algorithm = 0

# main menu of manage page
main_menu = [
    {
        'text': 'Users',
        'expanded': True,
        'children':
        [
            {'text': 'Teams and Users', 'value': 'teams', 'leaf': True, 'id': 'teamsMenu'},
        ],
    }, {
        'text': 'Models',
        'expanded': True,
        'children':
        [
            {'text': 'Test Cases and Test Sets', 'value': 'testSets', 'leaf': True, 'id': 'testSetsMenu'},
        ],
    }, {
        'text': 'Sessions',
        'expanded': True,
        'children':
        [
            {'text': 'Current sessions', 'value': 'currentSession', 'leaf': True, 'id': 'currentSessionMenu'},
            {'text': 'Create new session', 'value': 'newSession', 'leaf': True, 'id': 'newSessionMenu'},
            {'text': 'Browse sessions', 'value': 'history', 'leaf': True, 'id': 'historyMenu'},
        ],
    },
]
