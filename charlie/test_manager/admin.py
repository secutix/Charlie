from django.contrib import admin
from test_manager.models import *
from test_manager.config import Config

admin.site.register(TestCase)
admin.site.register(TestCaseStep)
admin.site.register(TestCasesTestSets)
admin.site.register(TestSet)
admin.site.register(TestSetRun)
admin.site.register(TestCaseRun)
admin.site.register(TestCaseStepRun)
admin.site.register(Jira)
admin.site.register(Tag)
admin.site.register(Availability)
admin.site.register(Config)
