from django.contrib import admin
from test_manager.models import *

class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('', {'fields': ['visa', 'privileged']}),
    ]
    model = User

class TestCaseStepInline(admin.TabularInline):
    fieldsets = [
        ('Number', {'fields': ['num']}),
        ('Instruction', {'fields': ['action']}),
        ('Expected result', {'fields': ['expected']}),
    ]
    model = TestCaseStep
    extra = 3

class TestCaseAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {'fields': ['title', 'description', 'creation_date', 'author', 'precondition']}),
        ('Details', {'fields': ['environment', 'os', 'browser', 'release', 'version', 'module', 'sub_module', 'criticity']}),
    ]
    inlines = [TestCaseStepInline]

class TestSetRunAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Set Run Name', {'fields': ['name']}),
        ('Choose a test case set', {'fields' : ['test_set']}),
        ('Assign to team', {'fields': ['team']}),
        ('Test Set Run Duration', {'fields' : ['from_date', 'to_date']}),
    ]

class TestCaseRunAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Test Case Run', {'fields': ['test_case', 'test_set_run', 'tester', 'execution_date']}),
        ('Basic Information', {'fields': ['title', 'description', 'creation_date', 'author', 'precondition']}),
        ('Details', {'fields': ['environment', 'os', 'browser', 'release', 'version', 'module', 'sub_module', 'criticity']}),
    ]

class TestCaseStepRunAdmin(admin.ModelAdmin):
    fields = ('test_case', 'test_case_step', 'num', 'action', 'expected')

admin.site.register(Team)
admin.site.register(User, UserAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestSet)
admin.site.register(TestSetRun, TestSetRunAdmin)
admin.site.register(TestCaseRun, TestCaseRunAdmin)
admin.site.register(TestCaseStepRun, TestCaseStepRunAdmin)
admin.site.register(Jira)
admin.site.register(Tag)
