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
tc4 = TestCase(
    title = "tc4",
    description = "descr4",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env4",
    os = "os4",
    browser = "browser4",
    release = "rel4",
    version = "ver4",
    module = "mod4",
    sub_module = "smod4",
    criticity = 3,
    precondition = "precond4",
    length = 100,
)
tc4.save()
tc5 = TestCase(
    title = "tc5",
    description = "descr5",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env5",
    os = "os5",
    browser = "browser5",
    release = "rel5",
    version = "ver5",
    module = "mod5",
    sub_module = "smod5",
    criticity = 3,
    precondition = "precond5",
    length = 100,
)
tc5.save()
tc6 = TestCase(
    title = "tc6",
    description = "descr6",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env6",
    os = "os6",
    browser = "browser6",
    release = "rel6",
    version = "ver6",
    module = "mod6",
    sub_module = "smod6",
    criticity = 3,
    precondition = "precond6",
    length = 100,
)
tc6.save()
tc7 = TestCase(
    title = "tc7",
    description = "descr7",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env7",
    os = "os7",
    browser = "browser7",
    release = "rel7",
    version = "ver7",
    module = "mod7",
    sub_module = "smod7",
    criticity = 3,
    precondition = "precond7",
    length = 100,
)
tc7.save()
tc8 = TestCase(
    title = "tc8",
    description = "descr8",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env8",
    os = "os8",
    browser = "browser8",
    release = "rel8",
    version = "ver8",
    module = "mod8",
    sub_module = "smod8",
    criticity = 3,
    precondition = "precond8",
    length = 100,
)
tc8.save()
tc9 = TestCase(
    title = "tc9",
    description = "descr9",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env9",
    os = "os9",
    browser = "browser9",
    release = "rel9",
    version = "ver9",
    module = "mod9",
    sub_module = "smod9",
    criticity = 3,
    precondition = "precond9",
    length = 100,
)
tc9.save()
tc10 = TestCase(
    title = "tc10",
    description = "descr10",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env10",
    os = "os10",
    browser = "browser10",
    release = "rel10",
    version = "ver10",
    module = "mod10",
    sub_module = "smod10",
    criticity = 3,
    precondition = "precond10",
    length = 100,
)
tc10.save()
tc11 = TestCase(
    title = "tc11",
    description = "descr11",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env11",
    os = "os11",
    browser = "browser11",
    release = "rel11",
    version = "ver11",
    module = "mod11",
    sub_module = "smod11",
    criticity = 3,
    precondition = "precond11",
    length = 100,
)
tc11.save()
tc12 = TestCase(
    title = "tc12",
    description = "descr12",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env12",
    os = "os12",
    browser = "browser12",
    release = "rel12",
    version = "ver12",
    module = "mod12",
    sub_module = "smod12",
    criticity = 3,
    precondition = "precond12",
    length = 100,
)
tc12.save()
tc13 = TestCase(
    title = "tc13",
    description = "descr13",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env13",
    os = "os13",
    browser = "browser13",
    release = "rel13",
    version = "ver13",
    module = "mod13",
    sub_module = "smod13",
    criticity = 3,
    precondition = "precond13",
    length = 100,
)
tc13.save()
tc14 = TestCase(
    title = "tc14",
    description = "descr14",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env14",
    os = "os14",
    browser = "browser14",
    release = "rel14",
    version = "ver14",
    module = "mod14",
    sub_module = "smod14",
    criticity = 3,
    precondition = "precond14",
    length = 100,
)
tc14.save()
tc15 = TestCase(
    title = "tc15",
    description = "descr15",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env15",
    os = "os15",
    browser = "browser15",
    release = "rel15",
    version = "ver15",
    module = "mod15",
    sub_module = "smod15",
    criticity = 3,
    precondition = "precond15",
    length = 100,
)
tc15.save()
tc16 = TestCase(
    title = "tc16",
    description = "descr16",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env16",
    os = "os16",
    browser = "browser16",
    release = "rel16",
    version = "ver16",
    module = "mod16",
    sub_module = "smod16",
    criticity = 3,
    precondition = "precond16",
    length = 100,
)
tc16.save()
tc17 = TestCase(
    title = "tc17",
    description = "descr17",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env17",
    os = "os17",
    browser = "browser17",
    release = "rel17",
    version = "ver17",
    module = "mod17",
    sub_module = "smod17",
    criticity = 3,
    precondition = "precond17",
    length = 100,
)
tc17.save()
tc18 = TestCase(
    title = "tc18",
    description = "descr18",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env18",
    os = "os18",
    browser = "browser18",
    release = "rel18",
    version = "ver18",
    module = "mod18",
    sub_module = "smod18",
    criticity = 3,
    precondition = "precond18",
    length = 100,
)
tc18.save()
tc19 = TestCase(
    title = "tc19",
    description = "descr19",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env19",
    os = "os19",
    browser = "browser19",
    release = "rel19",
    version = "ver19",
    module = "mod19",
    sub_module = "smod19",
    criticity = 3,
    precondition = "precond19",
    length = 100,
)
tc19.save()
tc20 = TestCase(
    title = "tc20",
    description = "descr20",
    creation_date = date.today(),
    author = User.objects.get(username = "agr"),
    environment = "env20",
    os = "os20",
    browser = "browser20",
    release = "rel20",
    version = "ver20",
    module = "mod20",
    sub_module = "smod20",
    criticity = 3,
    precondition = "precond20",
    length = 100,
)
tc20.save()
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
ts1.test_cases.add(tc3)
ts1.test_cases.add(tc4)
ts1.test_cases.add(tc5)
ts1.test_cases.add(tc6)
ts1.test_cases.add(tc7)
ts1.test_cases.add(tc8)
ts1.test_cases.add(tc9)
ts1.test_cases.add(tc10)
ts1.test_cases.add(tc11)
ts1.test_cases.add(tc12)
ts1.test_cases.add(tc13)
ts1.test_cases.add(tc14)
ts1.test_cases.add(tc15)
ts1.test_cases.add(tc16)
ts1.test_cases.add(tc17)
ts1.test_cases.add(tc18)
ts1.test_cases.add(tc19)
ts1.test_cases.add(tc20)
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
    from_date = date.today(),
    to_date = date.today() + timedelta(7),
    group = Group.objects.get(name = 'team1'),
)
tsr2.save()
tsr2.add_test_cases([tc1, tc2])
tsr2.save()

tsr1.deal()

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

