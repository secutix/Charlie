from django.contrib import admin
from test_manager.models import *

class TesterAdmin(admin.ModelAdmin):
    fieldsets = [
        ('', {'fields': ['visa', 'privileged']}),
    ]
    model = Tester
    extra = 3

class TeamAdmin(admin.ModelAdmin):
    pass

class TestCaseStepInline(admin.TabularInline):
    fieldsets = [
        ('Number', {'fields': ['num']}),
        ('Instruction', {'fields': ['action']}),
        ('Expected result', {'fields': ['expected']}),
    ]
    model = TestCaseStep
    extra = 3

class TestCaseSetAdmin(admin.ModelAdmin):
    pass

class TestCaseAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {'fields': ['title', 'description', 'creation_date', 'author', 'precondition']}),
        ('Details', {'fields': ['environment', 'os', 'browser', 'release', 'version', 'module', 'sub_module', 'criticity']}),
    ]
    inlines = [TestCaseStepInline]

admin.site.register(Team, TeamAdmin)
admin.site.register(Tester, TesterAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestCaseSet, TestCaseSetAdmin)
