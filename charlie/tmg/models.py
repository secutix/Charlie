from django.db import models
import datetime

class Team(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name
    def get_testers(self):
        return self.tester_set.all()

class Tester(models.Model):
    team = models.ForeignKey(Team)
    visa = models.CharField(max_length=3)
    privileged = models.BooleanField()
    def __unicode__(self):
        return self.visa

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
    precondition = models.CharField(max_length=200)
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.creation_date = datetime.date.today()
    def __unicode__(self):
        return self.title
    def get_tags(self):
        return self.tag_set.all()
    def get_steps(self):
        return self.testcasestep_set.all()

class Tag(models.Model):
    testcase = models.ForeignKey(TestCase)
    name = models.CharField(max_length=200)

class TestCaseStep(models.Model):
    num = models.IntegerField()
    testcase = models.ForeignKey(TestCase)
    action = models.CharField(max_length=2500)
    expected = models.CharField(max_length=2500)
