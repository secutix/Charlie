from django.db import models
from django.contrib.auth.models import User, Group
from suds.client import Client
import datetime
import config
from test_manager.classes import SContext

##############
# Test Cases #
##############
class TestCaseAbstract(models.Model):
    """
        Abstract class for both test cases (the "model" test cases) and the test case runs (the executions of these models by a tester)
    """
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
    length = models.IntegerField(default = 15)
    def __unicode__(self):
        return self.title
    class Meta:
        abstract = True


class TestCase(TestCaseAbstract):
    """
        model test case
    """
    test_sets = models.ManyToManyField('TestSet', through = 'TestCasesTestSets')
    def get_tags(self):
        """
            returns the tags associated to this test case
        """
        return list(self.tag_set.all())
    def get_sets(self):
        """
            returns the test sets in which this test case can be found
        """
        return list(self.test_sets.all())
    def get_steps(self):
        """
            returns the steps (actions & expected results) for this test case
        """
        return list(self.testcasestep_set.all())


class TestCaseRun(TestCaseAbstract):
    """
        execution by someone at a certain time of a test case model, in the context of a test set run
    """
    test_set_run = models.ForeignKey('TestSetRun')
    test_case = models.ForeignKey('TestCase')
    execution_date = models.DateField('Date of execution', default = datetime.date.today())
    tester = models.ForeignKey(User, related_name = '%(app_label)s_%(class)s_related')
    done = models.BooleanField(default = False)
    given = models.BooleanField(default = False)
    def __init__(self, *args, **kwargs):
        super(TestCaseRun, self).__init__(*args, **kwargs)
    def make_step_runs(self):
        """
            copy the steps from the test case model, save them, link them to this test case run
        """
        for s in self.test_case.get_steps():
            sr = TestCaseStepRun()
            sr.num = s.num
            sr.action = s.action
            sr.expected = s.expected
            sr.test_case = self
            sr.test_case_step = s
            sr.save()
    def get_tags(self):
        """
            returns the tags for this test case execution
        """
        return self.test_case.get_tags()
    def get_steps(self):
        """
            returns this test case execution steps
        """
        return list(self.testcasesteprun_set.all())
    def get_solvable_data(self):
        """
            returns a dict containing the formatted useful data for the scheduling algorithm
        """
        return {'id': self.id, 'w': self.length, 'p': self.criticity, 'x': self.execution_date, 'u': 0, 'g': self.given}


#############
# Test Sets #
#############
class TestSetAbstract(models.Model):
    """
        Abstract class for both test sets and test set runs. a test set is basically a list of (tests and test sets), while a test case run only contains test case runs.
    """
    name = models.CharField(max_length = 200)
    def __unicode__(self):
        return self.name
    class Meta:
        abstract = True


class TestSet(TestSetAbstract):
    """
        list of test sets and test cases
    """
    test_cases = models.ManyToManyField('TestCase', through = 'TestCasesTestSets')
    parent_test_set = models.ForeignKey('TestSet', default = None)
    def get_test_sets(self):
        """
            returns the test sets embedded in this one
        """
        return list(self.testset_set.all())
    def get_direct_test_cases(self):
        """
            returns the test cases immediately belonging to this test set
        """
        return list(self.test_cases.all())
    def get_test_cases(self):
        """
            returns all of the test cases belonging to this test set (also the ones of the children test sets)
        """
        res = list(self.test_cases.all())
        for ts in list(self.testset_set.all()):
            res.extend(ts.get_test_cases())
        return res
    def build(self):
        """
            returns {self, [child1.build(), child2.build(), ...]} used for the test sets tree in the manage menu "Test Sets"
        """
        children = []
        for t in self.get_test_sets():
            children.append(t.build())
        for t in self.get_direct_test_cases():
            children.append({'tsid': self.id, 'text': t.title, 'value': t.id, 'leaf': True})
        expanded = False
        if self.parent_test_set_id == 0:
            expanded = True
        return {'tsid': self.id, 'text': self.name, 'expanded': expanded, 'children': children}

class TestSetRun(TestSetAbstract):
    """
        test session. contains the schedule : who does which test case and at what time.
    """
    from_date = models.DateField('Starting Date')
    to_date = models.DateField('Ending Date')
    group = models.ForeignKey(Group)
    def add_set(self, ts):
        """
            create test case runs from the test cases of this test set
        """
        self.add_test_cases(ts.get_test_cases())
    def add_test_cases(self, otcl):
        """
            create test case runs from the test cases of this list
        """
        # check that there isn't more than 1 instance of each test in the list
        tcl = []
        for otc in list(otcl):
            good = True
            for tc in tcl:
                if otc.id == tc.id:
                    good = False
                else:
                    pass
            if good:
                tcl.append(otc)
        # duplicate
        for tc in list(tcl):
            tr = TestCaseRun()
            tr.test_case = tc
            tr.execution_date = self.from_date
            tr.tester_id = 0
            tr.title = tc.title
            tr.description = tc.description
            tr.creation_date = tc.creation_date
            tr.author = tc.author
            tr.environment = tc.environment
            tr.os = tc.os
            tr.browser = tc.browser
            tr.release = tc.release
            tr.version = tc.version
            tr.module = tc.module
            tr.sub_module = tc.sub_module
            tr.criticity = tc.criticity
            tr.precondition = tc.precondition
            tr.length = tc.length
            tr.test_set_run = self
            tr.done = False
            tr.save()
            self.testcaserun_set.add(tr)
        self.save()
    def get_test_cases(self):
        """
            returns all of the test case runs of this test set run
        """
        return list(self.testcaserun_set.all())
    def __init__(self, *args, **kwargs):
        super(TestSetRun, self).__init__(*args, **kwargs)
    def deal(self):
        """
            make the schedule, given the test case runs.
        """
        usrs = list(self.group.user_set.all())
        # check if the availability objects exist. if not, create them.
        for nd in range((self.to_date - self.from_date).days):
            d = self.from_date + datetime.timedelta(nd)
            for u in usrs:
                try:
                    a = Availability.objects.get(user = u, day = d)
                    if (self.from_date + datetime.timedelta(nd)).weekday() > 4:
                        a.delete()
                except Availability.DoesNotExist:
                    if (self.from_date + datetime.timedelta(nd)).weekday() < 5:
                        a = Availability(user = u, day = d, group = self.group)
                        a.save()
        # retrieve the availability objects during which the test cases runs can be executed
        avails = Availability.objects.filter(
            day__gte = self.from_date,
            day__lte = self.to_date,
            group = self.group,
        )
        # format the data
        av = []
        for a in avails:
            av.append(a.get_solvable_data())
        tc = []
        for t in self.get_test_cases():
            tc.append(t.get_solvable_data())
        # solve
        scont = SContext(av, tc)
        tr = scont.tr
        # apply
        for t in tr:
            tcr = TestCaseRun.objects.get(pk = t['id'])
            tcr.execution_date = t['x']
            tcr.tester = User.objects.get(pk = t['u'])
            tcr.save()
            tcr.make_step_runs()


class TestCasesTestSets(models.Model):
    """
        link between test cases and test sets
    """
    test_case = models.ForeignKey(TestCase)
    test_set = models.ForeignKey(TestSet)
    class Meta:
        db_table = 'test_manager_cases_sets'
        auto_created = TestCase


###################
# Test Case Steps #
###################
class TestCaseStepAbstract(models.Model):
    """
        Abstract class for both test case steps and test case step runs
    """
    num = models.IntegerField(default = 0)
    action = models.CharField(max_length = 2500)
    expected = models.CharField(max_length = 2500)
    def __unicode__(self):
        if len(self.action) > 20:
            return self.action[:15] + '...'
        else:
            return self.action


class TestCaseStep(TestCaseStepAbstract):
    """
        the action and expected result for a step of a test case
    """
    test_case = models.ForeignKey(TestCase)


class TestCaseStepRun(TestCaseStepAbstract):
    """
        the action and expected result, plus eventually jiras for a step of a test case run
    """
    test_case = models.ForeignKey(TestCaseRun)
    test_case_step = models.ForeignKey(TestCaseStep)
    def __init__(self, *args, **kwargs):
        super(TestCaseStepRun, self).__init__(*args, **kwargs)
    def get_jiras(self):
        """
            returns all of the jiras associated to this step
        """
        return list(self.jira_set.all())


#################
# Miscellaneous #
#################
class Jira(models.Model):
    """
        url and status of a jira associated to a test case step run
    """
    test_case_step = models.ForeignKey(TestCaseStepRun)
    url = models.CharField(max_length = 200)
    status = models.CharField(max_length = 200)
    def __unicode__(self):
        return self.test_case_step.__unicode__() + ' : ' + self.url[:20]


class Tag(models.Model):
    """
        tag associated to a test case, in order to find them easily
    """
    name = models.CharField(max_length = 200)
    test_case = models.ForeignKey(TestCase)
    def __unicode__(self):
        return self.name

class Availability(models.Model):
    """
        tells what % of the day someone is available to perform tests
    """
    day = models.DateField()
    user = models.ForeignKey(User)
    avail = models.IntegerField(default = config.default_availability)
    group = models.ForeignKey(Group)
    class Meta:
        verbose_name_plural = 'availabilities'
    def __unicode__(self):
        return "%s-%s" % (self.user, self.day.isoformat())
    def total_time(self):
        """
            returns the total time someone has to perform tests on this day
        """
        return 4.92 * self.avail
    def remaining_time(self):
        """
            returns how much time this person still has to do more tests today
        """
        ret = self.total_time()
        assigns = list(TestCaseRun.objects.filter(tester = self.user, execution_date = self.day))
        for a in assigns:
            ret -= a.length
        return ret
    def get_solvable_data(self):
        """
            returns the formatted data for the scheduling algorithm
        """
        return {'usr': self.user.id, 'd': self.day, 'pct': self.avail, 'rem': self.total_time()}

