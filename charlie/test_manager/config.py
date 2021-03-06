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

def get_tc_tree():
    res = []
    myVars = ['os', 'envir', 'browser', 'release', 'version']
    type_name = {'os': 'OS', 'module': 'Modules', 'envir': 'Environments', 'browser': 'Browsers', 'release': 'Releases', 'version': 'Versions'}
    for v in myVars:
        children = []
        for c in list(Config.objects.filter(ctype = v)):
            children.append({'text': c.name, 'value': c.value, 'leaf': True, 'id': c.value, 'menu': 2})
        res.append({'text': type_name[v], 'value': v, 'expanded': True, 'iconCls': 'folder', 'leaf': False, 'children': children, 'menu': 1})
    mods = []
    for mod in Config.objects.filter(ctype = 'module'):
        s_mods = []
        for smod in Config.objects.filter(ctype = mod.value):
            s_mods.append({'text': smod.name, 'value': smod.value, 'leaf': True, 'id': smod.value, 'menu': 2})
        mods.append({'text': mod.name, 'value': mod.value, 'expanded': True, 'leaf': False, 'iconCls': 'folder', 'children': s_mods, 'id': mod.value, 'menu': 3})
    res.append({'text': 'Modules', 'expanded': True, 'value': '__rootmods', 'children': mods, 'menu': 1})
    return res


# default % of the day that a tester is available to perform tests
default_availability = 60

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
    }, {
        'text': 'Configuration',
        'expanded': True,
        'children':
        [
            {'text': 'Test Case Configuration', 'value': 'config', 'leaf': True, 'id': 'configMenu'},
        ],
    },
]
