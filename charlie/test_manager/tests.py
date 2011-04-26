from models import *

def test_get_testers():
    a = Tester(visa = 'a', privileged = True)
    b = Tester(visa = 'b', privileged = True)
    a.save()
    b.save()

    t = Team(name = "t")
    t.save()
    t.testers.add(a)
    t.testers.add(b)
    t.save()

    assert(list(t.get_testers())[0].visa == a.visa and list(t.get_testers())[0].privileged == a.privileged and list(t.get_testers())[1].visa == b.visa and list(t.get_testers())[1].privileged == b.privileged)

def test_get_tags():
    t = Team(name = "t")
    t.save()

    a = Tester(visa = 'a', privileged = True)
    a.team = t
    a.save()

    tc1 = TestCase(title="testcase1", precondition="precond", author=a, criticity=2)
    tc1.save()

    t1 = Tag(testcase=tc1, name="tag1")
    t2 = Tag(testcase=tc1, name="tag2")
    t1.save()
    t2.save()

    lr = list(tc1.get_tags())
    tt1 = lr[0]
    tt2 = lr[1]

    assert(tt1.name == t1.name and tt2.name == t2.name)

def test_get_steps():
    t = Team(name = "t")
    t.save()

    a = Tester(visa = 'a', privileged = True)
    a.team = t
    a.save()

    tc1 = TestCase(title="testcase1", precondition="precond1", author=a, criticity=3)
    tc2 = TestCase(title="testcase2", precondition="precond2", author=a, criticity=3)
    tc1.save()
    tc2.save()

    t1 = Tag(name="tag1", testcase=tc1)
    t2 = Tag(name="tag2", testcase=tc2)
    t1.save()
    t2.save()

    s1 = TestCaseStep(num=1, testcase=tc1, action="act1", expected="exp1")
    s2 = TestCaseStep(num=2, testcase=tc1, action="act2", expected="exp2")
    s3 = TestCaseStep(num=3, testcase=tc2, action="act3", expected="exp3")
    s4 = TestCaseStep(num=4, testcase=tc2, action="act4", expected="exp4")
    s1.save()
    s2.save()
    s3.save()
    s4.save()

    ts1 = list(tc2.get_steps())[0]
    ts2 = list(tc2.get_steps())[1]

    assert (ts1.num == s3.num and ts1.testcase.title == s3.testcase.title and ts1.action == s3.action and ts1.expected == s3.expected)

def test_get_testcases_and_reverse():
    t = Team(name = "t")
    t.save()

    a = Tester(visa = 'a', privileged = True)
    a.save()
    t.testers.add(a)
    t.save()

    tc1 = TestCase(title="testcase1", precondition="precond1", author=a, criticity=3)
    tc2 = TestCase(title="testcase2", precondition="precond2", author=a, criticity=3)
    tc1.save()
    tc2.save()

    t1 = Tag(name="tag1", testcase=tc1)
    t2 = Tag(name="tag2", testcase=tc2)
    t1.save()
    t2.save()

    s1 = TestCaseStep(num=1, testcase=tc1, action="act1", expected="exp1")
    s2 = TestCaseStep(num=2, testcase=tc1, action="act2", expected="exp2")
    s3 = TestCaseStep(num=3, testcase=tc2, action="act3", expected="exp3")
    s4 = TestCaseStep(num=4, testcase=tc2, action="act4", expected="exp4")
    s1.save()
    s2.save()
    s3.save()
    s4.save()

    tcs = TestCaseSet(title="tcs1")
    tcs.save()
    tcs.testcases.add(tc1)
    tcs.testcases.add(tc2)
    tcs.save()

    assert(list(tcs.get_testcases())[0].title == tc1.title and list(tcs.get_testcases())[0].precondition == tc1.precondition and list(tcs.get_testcases())[1].title == tc2.title and list(tcs.get_testcases())[1].precondition == tc2.precondition)
    assert(list(tc1.get_sets())[0].title == tcs.title and list(tc2.get_sets())[0].title == tcs.title)
