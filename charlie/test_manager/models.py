from django.db import models
import datetime

class Tester(models.Model):
    visa = models.CharField(max_length=3)
    privileged = models.BooleanField()
    teams = models.ManyToManyField('Team', through='TesterTeams')
    def __unicode__(self):
        return self.visa

class Team(models.Model):
    name = models.CharField(max_length=200)
    testers = models.ManyToManyField('Tester', through='TesterTeams')
    def __unicode__(self):
        return self.name
    def get_testers(self):
        return self.testers.all()

class TesterTeams(models.Model):
    tester = models.ForeignKey(Tester)
    team = models.ForeignKey(Team)
    class Meta:
        db_table = 'test_manager_team_testers'
        auto_created = Tester

class TestCase(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    creation_date = models.DateField('date created')
    author = models.ForeignKey(Tester)
    environment = models.CharField(max_length=200)
    os = models.CharField(max_length=200)
    browser = models.CharField(max_length=200)
    release = models.CharField(max_length=20)
    version = models.CharField(max_length=20)
    module = models.CharField(max_length=200)
    sub_module = models.CharField(max_length=200)
    criticity = models.IntegerField()
    precondition = models.CharField(max_length=2500)
    testcasesets = models.ManyToManyField('TestCaseSet', through = 'CasesAndSteps')
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.creation_date = datetime.date.today()
    def __unicode__(self):
        return self.title
    def get_tags(self):
        return self.tag_set.all()
    def get_steps(self):
        return self.testcasestep_set.all()

class TestCaseSet(models.Model):
    title = models.CharField(max_length=200)
    testcases = models.ManyToManyField('TestCase', through = 'CasesAndSteps')
    def __unicode__(self):
        return self.title
    def get_testcases(self):
        return self.testcases.all()

class CasesAndSteps(models.Model):
    testcase = models.ForeignKey(TestCase)
    testcaseset = models.ForeignKey(TestCaseSet)

    class Meta:
        db_table = 'test_manager_testcaseset_testcases'
        auto_created = TestCase

class Tag(models.Model):
    testcase = models.ForeignKey(TestCase)
    name = models.CharField(max_length=200)

class TestCaseStep(models.Model):
    num = models.IntegerField()
    testcase = models.ForeignKey(TestCase)
    action = models.CharField(max_length=2500)
    expected = models.CharField(max_length=2500)

class Jira(models.Model):
    testcase = models.ForeignKey(TestCase)
    url = models.CharField(max_length=200)
