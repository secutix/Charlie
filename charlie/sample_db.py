from test_manager.models import *
from test_manager.config import Config
from django.contrib.auth.models import User, Group
from datetime import date, timedelta

c = Config(ctype = 'os', name = 'Debian', value = 'debian')
c.save()
c = Config(ctype = 'os', name = 'ArchLinux', value = 'archlinux')
c.save()
c = Config(ctype = 'module', name = 'Module 1', value = 'mod1')
c.save()
c = Config(ctype = 'module', name = 'Module 2', value = 'mod2')
c.save()
c = Config(ctype = 'envir', name = 'Environment 1', value = 'env1')
c.save()
c = Config(ctype = 'envir', name = 'Environment 2', value = 'envi2')
c.save()
c = Config(ctype = 'browser', name = 'Firefox', value = 'firefox')
c.save()
c = Config(ctype = 'browser', name = 'Chromium', value = 'chromium')
c.save()
c = Config(ctype = 'release', name = 'Release 1', value = 'rel1')
c.save()
c = Config(ctype = 'release', name = 'Release 2', value = 'rel2')
c.save()
c = Config(ctype = 'version', name = 'Version 1', value = 'ver1')
c.save()
c = Config(ctype = 'version', name = 'Version 2', value = 'ver2')
c.save()
c = Config(ctype = 'mod1', name = 'Sub Module A', value = 'smoda')
c.save()
c = Config(ctype = 'mod1', name = 'Sub Module B', value = 'smodb')
c.save()
c = Config(ctype = 'mod2', name = 'Sub Module C', value = 'smodc')
c.save()
c = Config(ctype = 'mod2', name = 'Sub Module D', value = 'smodd')
c.save()

for i in range(20):
    tc = TestCase(
        title = "tc" + str(i),
        description = "descr",
        creation_date = date.today(),
        author = User.objects.get(pk = 1),
        environment = "env" + str(i),
        os = "os" + str(i),
        browser = "browser" + str(i),
        release = "rel" + str(i),
        version = "ver" + str(i),
        module = "mod" + str(i),
        sub_module = "smod" + str(i),
        criticity = 3,
        precondition = "precond" + str(i),
        length = 100,
    )
    tc.save()
    Tag(name = 'tag' + str(i), test_case = tc).save()
    Tag(name = 'tc' + str(i), test_case = tc).save()

for i in range(20):
    TestCaseStep(
        num = 1,
        action = 'action' + str(i),
        expected = 'expected' + str(i),
        test_case = TestCase.objects.get(title = "tc" + str(i)),
    ).save()
    TestCaseStep(
        num = 2,
        action = 'actionbis' + str(i),
        expected = 'expectedbis' + str(i),
        test_case = TestCase.objects.get(title = "tc" + str(i)),
    ).save()

ts1 = TestSet(
    name = 'ts1',
    parent_test_set_id = 0,
)
ts1.save()
for i in range(3, 12):
    ts1.test_cases.add(TestCase.objects.get(title = "tc" + str(i)))
ts1.save()

ts2 = TestSet(
    name = 'ts2',
    parent_test_set_id = 1,
)
ts2.save()
for i in range(6, 16):
    ts2.test_cases.add(TestCase.objects.get(title = "tc" + str(i)))
ts2.save()

tsr1 = TestSetRun(
    name = 'tsr1',
    from_date = date.today(),
    to_date = date.today() + timedelta(7),
    group = Group.objects.get(name = 'team1'),
)
tsr1.save()
tsr1.add_set(ts1)
tsr1.save()

tsr2 = TestSetRun(
    name = 'tsr2',
    from_date = date.today() - timedelta(6),
    to_date = date.today() - timedelta(2),
    group = Group.objects.get(name = 'team1'),
)
tsr2.save()
tsr2.add_set(ts2)
tsr2.save()

tsr1.deal()
tsr2.deal()

for t in tsr2.get_test_cases():
    t.done = True
    t.save()

j1 = Jira(
   test_case_step = TestCaseStepRun.objects.all()[0],
   url = 'http://jira1',
   status = 'unresolved',
)
j1.save()

j2 = Jira(
   test_case_step = TestCaseStepRun.objects.all()[1],
   url = 'http://jira2',
   status = 'being fixed',
)
j2.save()

