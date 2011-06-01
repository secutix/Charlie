# wsdl page for logging in to jira
jira_server_url = 'http://jira-stx.elca.ch/jira/rpc/soap/jirasoapservice-v2?wsdl'

# test case creation data (dropdown menus)
tc_data = { 'os':[
        {'name': 'ArchLinux', 'value': 'archlinux'},
        {'name': 'Debian', 'value': 'debian'},
        {'name': 'Fedora', 'value': 'fedora'},
    ], 'module':[
        {'name': 'Module 1', 'value': 'mod1'},
        {'name': 'Module 2', 'value': 'mod2'},
    ], 'envir':[
        {'name': 'Environment 1', 'value': 'env1'},
        {'name': 'Environment 2', 'value': 'env2'},
    ], 'browser':[
        {'name': 'Firefox', 'value': 'firefox'},
        {'name': 'Google Chrome', 'value': 'chrome'},
    ], 'release':[
        {'name': 'Release 1', 'value': 'rel1'},
        {'name': 'Release 2', 'value': 'rel2'},
    ], 'version':[
        {'name': 'Version 1', 'value': 'ver1'},
        {'name': 'Version 2', 'value': 'ver2'},
    ], 'smodule':[
        {'name': 'Choose a module first !', 'value': None},
    ], 'submodules':{'mod1': [
            {'name': 'Sub Module A', 'value': 'smoda'},
            {'name': 'Sub Module B', 'value': 'smodb'},
        ], 'mod2': [
            {'name': 'Sub Module C', 'value': 'smodc'},
            {'name': 'Sub Module D', 'value': 'smodd'},
    ]}
}

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
            {'text': 'Teams', 'value': 'teams', 'leaf': True},
            {'text': 'Users', 'value': 'users', 'leaf': True},
        ]
    },{
        'text': 'Models',
        'expanded': True,
        'children':
        [
            {'text': 'Test Cases', 'value': 'testcases', 'leaf': True},
            {'text': 'Test Sets', 'value': 'testsets', 'leaf': True},
        ]
    },{
        'text': 'Sessions',
        'expanded': True,
        'children':
        [
            {'text': 'Current session', 'value': 'currentsession', 'leaf': True},
            {'text': 'Create new session', 'value': 'newsession', 'leaf': True},
            {'text': 'Browse previous sessions', 'value': 'history', 'leaf': True},
        ],
    }
]
