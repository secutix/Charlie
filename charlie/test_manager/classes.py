from suds.client import Client, WebFault
import config

class Jiraconnection(object):
    def __init__(self, visa, password):
        self.jirauser = visa
        self.passwd = password
        client = Client(config.jira_server_url)
        self.success = False
        try:
            self.auth = client.service.login(self.jirauser, self.passwd)
            self.success = True
        except Exception as detail:
            self.success = False
