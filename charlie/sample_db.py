from test_manager.models import *
from django.contrib.auth.models import User, Group
from datetime import date, timedelta

tc1 = TestCase(
    title = 'tc1',
    description = 'descr1',
    creation_date = date.today(),
    author = User.objects.get(username = 'agr'),
    environment = 'env1',
    os = 'os1',
    browser = 'browser1',
    release = 'rel1',
    version = 'ver1',
    module = 'mod1',
    sub_module = 'smod1',
    criticity = 3,
    precondition = 'precond1',
    length = 100,
)
tc1.save()
tag1 = Tag(
    name = 'tag1',
    test_case = tc1,
)
tag1.save()

tc2 = TestCase(
    title = 'tc2',
    description = 'descr2',
    creation_date = date.today(),
    author = User.objects.get(username = 'agr'),
    environment = 'env2',
    os = 'os2',
    browser = 'browser2',
    release = 'rel2',
    version = 'ver2',
    module = 'mod2',
    sub_module = 'smod2',
    criticity = 3,
    precondition = 'precond2',
    length = 25,
)
tc2.save()
tag2 = Tag(
    name = 'tag2',
    test_case = tc2,
)
tag2.save()

tc3 = TestCase(
    title = 'tc3',
    description = 'descr3',
    creation_date = date.today(),
    author = User.objects.get(username = 'agr'),
    environment = 'env3',
    os = 'os3',
    browser = 'browser3',
    release = 'rel3',
    version = 'ver3',
    module = 'mod3',
    sub_module = 'smod3',
    criticity = 3,
    precondition = 'precond3',
    length = 35,
)
tc3.save()
tag3 = Tag(
    name = 'tag3',
    test_case = tc3,
)
tag3.save()

for i in range(4, 20):
    tc = TestCase(
        title = "tc" + str(i),
        description = "descr",
        creation_date = date.today(),
        author = User.objects.get(username = "agr"),
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

s1a = TestCaseStep(
    num = 1,
    action = 'act1a',
    expected = 'exp1a',
    test_case = tc1,
)
s1a.save()

s1b = TestCaseStep(
    num = 2,
    action = 'act1b',
    expected = 'exp1b',
    test_case = tc1,
)
s1b.save()

s2a = TestCaseStep(
    num = 1,
    action = 'act2a',
    expected = 'exp2a',
    test_case = tc2,
)
s2a.save()

s2b = TestCaseStep(
    num = 2,
    action = 'act2b',
    expected = 'exp2b',
    test_case = tc2,
)
s2b.save()

s3a = TestCaseStep(
    num = 1,
    action = 'act3a',
    expected = 'exp3a',
    test_case = tc3,
)
s3a.save()

s3b = TestCaseStep(
    num = 2,
    action = 'act3b',
    expected = 'exp3b',
    test_case = tc3,
)
s3b.save()

a1 = Availability(
    day = date.today(),
    user = User.objects.get(username = 'agr'),
    group = Group.objects.all()[0],
    avail = 45,
)
a1.save()

a2 = Availability(
    day = date.today(),
    user = User.objects.get(username = 'nre'),
    group = Group.objects.all()[0],
    avail = 85,
)
a2.save()

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
ts2.test_cases.add(tc1)
ts2.test_cases.add(tc2)
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
    from_date = date.today() - timedelta(3),
    to_date = date.today() - timedelta(1),
    group = Group.objects.get(name = 'team1'),
)
tsr2.save()
tsr2.add_test_cases([tc1, tc2])
tsr2.save()

tsr1.deal()
tsr2.deal()

#j1 = Jira(
#    test_case_step = TestCaseStepRun.objects.all()[0],
#    url = 'http://jira1',
#    status = 'unresolved',
#)
#j1.save()
#
#j2 = Jira(
#    test_case_step = TestCaseStepRun.objects.all()[1],
#    url = 'http://jira2',
#    status = 'being fixed',
#)
#j2.save()

