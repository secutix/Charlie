from django.db import models
from django.contrib.auth.models import User, Group
from suds.client import Client
import datetime
import config

##############
# Test Cases #
##############
class TestCaseAbstract(models.Model):
    title = models.CharField(max_length = 200)
    description = models.CharField(max_length = 200)
    creation_date = models.DateField('date created', default = datetime.date.today())
    author = models.ForeignKey(User)
    environment = models.CharField(max_length = 200)
    os = models.CharField(max_length = 200)
    browser = models.CharField(max_length = 200)
    release = models.CharField(max_length = 20)
    version = models.CharField(max_length = 20)
    module = models.CharField(max_length = 200)
    sub_module = models.CharField(max_length = 200)
    criticity = models.IntegerField(default = 3)
    precondition = models.CharField(max_length = 2500)
    def __unicode__(self):
        return self.title
    class Meta:
        abstract = True


class TestCase(TestCaseAbstract):
    test_sets = models.ManyToManyField('TestSet', through = 'TestCasesTestSets')
    length = models.IntegerField(default = 15)
    def get_tags(self):
        return list(self.tag_set.all())
    def get_sets(self):
        return list(test_sets.all())
    def get_steps(self):
        return list(self.test_case_step_set.all())


class TestCaseRun(TestCaseAbstract):
    test_set_run = models.ForeignKey('TestSetRun')
    test_case = models.ForeignKey('TestCase')
    execution_date = models.DateField('Date of execution')
    tester = models.ForeignKey(User, related_name = '%(app_label)s_%(class)s_related')
    done = models.BooleanField(default = False)
    length = models.IntegerField(default = 15)
    def get_tags(self):
        return self.test_case.get_tags()
    def get_steps(self):
        return list(self.test_case_step_run_set.all())


#############
# Test Sets #
#############
class TestSetAbstract(models.Model):
    name = models.CharField(max_length = 200)
    def __unicode__(self):
        return self.name
    class Meta:
        abstract = True


class TestSet(TestSetAbstract):
    test_cases = models.ManyToManyField('TestCase', through = 'TestCasesTestSets')
    def get_test_cases(self):
        return list(self.test_cases.all())
    def get_set_runs(self):
        return list(self.testsetrun_set.all())


class TestSetRun(TestSetAbstract):
    from_date = models.DateField('Starting Date')
    to_date = models.DateField('Ending Date')
    group = models.ForeignKey(Group)
    test_set = models.ForeignKey(TestSet)
    def get_test_cases(self):
        return list(self.testcaserun_set.all())


# link between test cases and test sets
class TestCasesTestSets(models.Model):
    test_case = models.ForeignKey(TestCase)
    test_set = models.ForeignKey(TestSet)
    class Meta:
        db_table = 'test_manager_cases_sets'
        auto_created = TestCase


###################
# Test Case Steps #
###################
class TestCaseStepAbstract(models.Model):
    num = models.IntegerField(default = 0)
    action = models.CharField(max_length = 2500)
    expected = models.CharField(max_length = 2500)
    def __unicode__(self):
        if len(self.action) > 20:
            return self.action[:15] + '...'
        else:
            return self.action


class TestCaseStep(TestCaseStepAbstract):
    test_case = models.ForeignKey(TestCase)


class TestCaseStepRun(TestCaseStepAbstract):
    test_case = models.ForeignKey(TestCaseRun)
    test_case_step = models.ForeignKey(TestCaseStep)
    def get_jiras(self):
        return list(self.jira_set.all())


#################
# Miscellaneous #
#################
class Jira(models.Model):
    test_case_step = models.ForeignKey(TestCaseStepRun)
    url = models.CharField(max_length = 200)
    status = models.CharField(max_length = 200)
    def __unicode__(self):
        return self.test_case_step.__unicode__() + self.url[:20]


class Tag(models.Model):
    name = models.CharField(max_length = 200)
    test_case = models.ForeignKey(TestCase)
    def __unicode__(self):
        return self.name

class Availability(models.Model):
    day = models.DateField()
    user = models.ForeignKey(User)
    avail = models.IntegerField(default = config.default_availability)
    def __unicode__(self):
        return "%s-%s" % (self.user, self.day.isoformat())

    class Meta:
        verbose_name_plural = 'availabilities'
