from django.contrib import admin
from tmg.models import *

class TesterInline(admin.StackedInline):
    model = Tester
    extra = 1

class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Steps", {'fields': ['name']}),
    ]
    inlines = [TesterInline]

class TestCaseStepInline(admin.TabularInline):
    fieldsets = [
        ('Number', {'fields': ['num']}),
        ('Instruction', {'fields': ['action']}),
        ('Expected result', {'fields': ['expected']})
    ]
    model = TestCaseStep
    extra = 1

class TestCaseAdmin(admin.ModelAdmin):
    inlines = [TestCaseStepInline]

admin.site.register(Team, TeamAdmin)
admin.site.register(TestCase, TestCaseAdmin)
