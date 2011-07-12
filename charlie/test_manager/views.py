from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from test_manager.models import *
from test_manager.classes import Jiraconnection
from django.core.context_processors import csrf
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import logout, login, authenticate
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from test_manager.config import *
import simplejson
import logging

@csrf_exempt
def main_page(request):
    """
        handles requests to the root of the website
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        return HttpResponseRedirect('/manage/home/')
    else:
        return HttpResponseRedirect('/test_manager/planning/')

def login_view(request):
    """
        login page
    """
    redirect = '/login/'
    if request.method == "GET":
        try:
            logout(request)
        except Exception:
            pass
        c = {}
        c.update(csrf(request))
        return render_to_response('test_manager/login.html', c)
    elif request.method == "POST":
        user = authenticate(user_name=request.POST.get('login', ''), password=request.POST.get('password', ''))
        if user is not None:
            request.session['uid'] = user.id
            login(request, user)
            logging.info("User %s logged in" % user.username)
            if user.is_staff:
                redirect = '/manage/home/'
            else:
                redirect = '/test_manager/planning/'
        else:
            pass
    else:
        pass
    return HttpResponseRedirect(redirect)

def logout_view(request):
    """
        logout page
    """
    logging.info("User %s logged out" % User.objects.get(pk = request.session['uid']).username)
    logout(request)
    return HttpResponseRedirect("/login/")

@csrf_exempt
def home(request):
    """
        main administration custom page
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        return render_to_response('manage/home.html')
    else:
        return HttpResponseRedirect('/login/')

@csrf_exempt
def home_teams(request):
    """
        returns the tree with users and teams
    """
    json = []
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        for t in list(Group.objects.all()):
            children = []
            for u in list(t.user_set.all()):
                children.append({'uid': u.id, 'text': u.username, 'leaf': True})
            json.append({'gid': t.id, 'text': t.name, 'draggable': False, 'children': children, 'expanded': True, 'iconCls': 'folder'})
        for u in list(User.objects.all()):
            if len(list(u.groups.all())) == 0:
                json.append({'uid': u.id, 'text': u.username, 'leaf': True})
    else:
        pass
    return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def home_ts(request):
    """
        returns the tree of test sets
    """
    json = []
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        rts = list(TestSet.objects.filter(parent_test_set__id = 0))
        for ts in rts:
            json.append(ts.build())
        ots = list(TestCase.objects.all())
        for t in ots:
            if len(t.test_sets.all()) == 0:
                tags = []
                for tag in t.get_tags():
                    tags.append(tag.name)
                json.append({'tsid': 0, 'text': t.title, 'value': t.id, 'leaf': True, 'tags': tags})
    else:
        pass
    return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def manage_planning(request):
    """
        Controller for the "Current sessions" view
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        if request.method == 'GET':
            try:
                tsr = TestSetRun.objects.get(pk = int(request.GET.get('s', '')))
                tsr.displayed = True
                logging.info("Test Session %s made visible" % tsr.name)
                tsr.save()
                f_date = tsr.from_date
            except Exception:
                f_date = datetime.date.today()
            y = f_date.year
            m = f_date.month
            d = f_date.day
            return render_to_response('manage/planning.html', {'d': d, 'm': m, 'y': y})
        else:
            action = request.POST.get('action', '')
            json = []
            dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
            if action == 'allSessionsData':
                user_set = []
                for t in list(TestSetRun.objects.filter(displayed = True)):
                    for u in set(Group.objects.get(pk = t.group_id).user_set.all()):
                        user_set.append(u)
                user_set = list(set(user_set))
                for u in list(user_set):
                    tcr = []
                    for tr in (TestCaseRun.objects.filter(tester = u)):
                        if tr.test_set_run.displayed:
                            tcr.append({
                                'title': tr.title,
                                'execution_date': tr.execution_date,
                                'done': tr.done,
                                'id': tr.id
                            })
                    json.append({'user': u.username.upper(), 'uid': u.id, 'tcr': tcr})
            elif action == 'tcMove':
                try:
                    try:
                        user = User.objects.get(username = request.POST.get('user', ''))
                    except User.DoesNotExist:
                        user = User.objects.get(pk = int(request.POST.get('user', '')))
                    tcr = TestCaseRun.objects.get(pk = int(request.POST.get('tcr', '')))
                    y = int(request.POST.get('year', ''))
                    m = int(request.POST.get('month', ''))
                    d = int(request.POST.get('day', ''))
                    date = datetime.date(y, m, d)
                    tcr.tester = user
                    tcr.execution_date = date
                    tcr.save()
                    logging.info("Test Case Run %s moved to %s on %s's calendar" % (tcr.title, date.isoformat(), user.username))
                    json.append({'success': True})
                except Exception as detail:
                    logging.error("unable to move test case. %s" % detail)
                    json.append({'success': False, 'errorMessage': 'unable to move TC'})
            elif action == 'newTcr':
                try:
                    tc = TestCase.objects.get(pk = int(request.POST.get('tc')))
                    tester = User.objects.get(pk = int(request.POST.get('user')))
                    tr = TestCaseRun()
                    tr.test_case = tc
                    y = int(request.POST.get('year', ''))
                    m = int(request.POST.get('month', ''))
                    d = int(request.POST.get('day', ''))
                    tr.execution_date = datetime.date(y, m, d)
                    tr.tester = tester
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
                    tr.test_set_run = TestSetRun.objects.latest('id')
                    tr.done = False
                    tr.save()
                    tr.make_step_runs()
                    tr.save()
                    logging.info("Test Case Run %s created" % tr.title)
                    json.append({'success': True})
                except Exception as detail:
                    logging.error("Unable to create test case run : %s" % detail)
                    json.append({'success': False, 'errorMessage': 'could not create test case run'})
            elif action == 'delTcr':
                try:
                    tcr = TestCaseRun.objects.get(pk = int(request.POST.get('tcr', '')))
                    logging.info("Test Case Run %s deleted" % tcr.title)
                    tcr.delete()
                    json.append({'success': True})
                except Exception:
                    json.append({'success': False, 'errorMessage': 'could not delete test case run'})
            elif action == 'gettcr':
                user = User.objects.get(username = request.POST.get('user', ''))
                for tcr in list(TestCaseRun.objects.filter(tester = user)):
                    json.append({
                        'title': tcr.title,
                        'execution_date': tcr.execution_date,
                        'id': tcr.id,
                    })
            elif action == 'usersStore':
                for u in list(User.objects.all()):
                    json.append({
                        'id': u.id,
                        'username': u.username,
                    })
            else:
                pass
        return HttpResponse(simplejson.dumps(json, default = dthandler))
    else:
        return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def home_data(request):
    """
        test case set creation panel
    """
    json = []
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if request.method == 'GET':
            action = request.GET.get('action', '')
            if action == 'testSets':
                for tc in TestCase.objects.all():
                    json.append({
                        'title': tc.title,
                        'id': tc.id,
                    })
            elif action == 'history':
                tsrlist_u = list(TestSetRun.objects.all())
                tsrlist = sorted(tsrlist_u, key = lambda s: s.from_date)
                for s in tsrlist:
                    json.append({
                        'name': s.name,
                        'id': s.id,
                        'from': s.from_date,
                        'to': s.to_date,
                        'team': s.group.id,
                        'teamname': s.group.name,
                        'disp': s.displayed,
                    })
            elif action == 'deltc':
                try:
                    tc = TestCase.objects.get(pk = request.GET.get('tc', ''))
                    logging.info("Test Case %s deleted" % tc.title)
                    tc.delete()
                    json = {'success': True}
                except Exception as detail:
                    logging.error("could not create test case %s" % detail)
                    json = {'success': False, 'errorMessage': 'could not delete test case'}
            elif action == 'deluser':
                u = User.objects.get(pk = request.GET.get('u', ''))
                if u.id != request.session['uid']:
                    logging.info("User %s deleted" % u.username)
                    u.delete()
                    json = {'success': True}
                else:
                    json = {'success': False, 'errorMessage': 'User is authenticated'}
            elif action == 'delteam':
                try:
                    g = Group.objects.get(pk = request.GET.get('t', ''))
                    logging.info("Group %s deleted" % g.name)
                    g.delete()
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'could not delete team'}
                    logging.error('could not delete team : %s' % detail)
            elif action == 'delts':
                try:
                    ts = TestSet.objects.get(pk=request.GET.get('ts', ''))
                    logging.info("Test Set %s deleted" % ts.name)
                    ts.delete()
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'could not delete test set'}
                    logging.error('could not delete test set : %s' % detail)
            elif action == 'mvuser':
                try:
                    u = User.objects.get(pk = request.GET.get('user', ''))
                    for g in u.groups.all():
                        u.groups.remove(g)
                    u.save()
                    gid = int(request.GET.get('team', ''))
                    if gid != -1:
                        g = Group.objects.get(pk = gid)
                        u.groups.add(g)
                        logging.info("User %s moved to %s" % (u.username, g.name))
                        u.save()
                    else:
                        logging.info("User %s moved out of groups" % u.username)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move user : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move user'}
            elif action == 'getgroups':
                for g in list(Group.objects.all()):
                    json.append({
                        'gid': g.id,
                        'gname': g.name,
                    })
            elif action == 'cptc':
                try:
                    tc = TestCase.objects.get(pk = request.GET.get('tc', ''))
                    if request.GET.get('ts', '') != '-1':
                        ts = TestSet.objects.get(pk = request.GET.get('ts', ''))
                        ts.test_cases.add(tc)
                        ts.save()
                        logging.info("Test Case %s copied to Test Set %s" % (tc.title, ts.name))
                    else:
                        logging.info("Test Case %s cannot be copied to root" % tc.title)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not copy test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not copy test case'}
            elif action == 'mvtc':
                try:
                    tc = TestCase.objects.get(pk = request.GET.get('tc', ''))
                    for cts in tc.get_sets():
                        cts.test_cases.remove(tc)
                    if request.GET.get('ts', '') != '-1':
                        ts = TestSet.objects.get(pk = request.GET.get('ts', ''))
                        ts.test_cases.add(tc)
                        ts.save()
                        logging.info("Test Case %s moved to Test Set %s" % (tc.title, ts.name))
                    else:
                        logging.info("Test Case %s moved to root" % tc.title)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move test case'}
            elif action == 'mvts':
                try:
                    cts = TestSet.objects.get(pk = request.GET.get('cts', ''))
                    if request.GET.get('pts', '') == '-1':
                        cts.parent_test_set_id = 0
                        logging.info("Test Set %s moved to the root" % cts.name)
                    else:
                        cts.parent_test_set = TestSet.objects.get(pk = request.GET.get('pts', ''))
                        logging.info("Test Set %s moved inside of Test Set %s" % (cts.name, cts.parent_test_set.name))
                    cts.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move test set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move test set'}
            elif action == 'combodata':
                json = config.tc_data
            else:
                pass
        else:
            action = request.POST.get('action', '')
            if action == 'newtc':
                try:
                    tsid = request.POST.get('tsid', '')
                    title = request.POST.get('title', '')
                    description = request.POST.get('description', '')
                    precondition = request.POST.get('precondition', '')
                    envir = request.POST.get('envir', '')
                    os = request.POST.get('os', '')
                    browser = request.POST.get('browser', '')
                    release = request.POST.get('release', '')
                    version = request.POST.get('version', '')
                    module = request.POST.get('module', '')
                    smodule = request.POST.get('smodule', '')
                    criticity = request.POST.get('criticity', '')
                    tc = TestCase(
                        title = title,
                        description = description,
                        author = User.objects.get(pk = request.session['uid']),
                        environment = envir,
                        os = os,
                        browser = browser,
                        release = release,
                        version = version,
                        module = module,
                        sub_module = smodule,
                        criticity = int(criticity),
                        precondition = precondition
                    )
                    tc.save()
                    logging.info("Test Case %s created" % tc.title)
                    tags = request.POST.get('tags', '')
                    Tag(name = title, test_case = tc).save()
                    for tag in list(tags.split()):
                        Tag(name = tag, test_case = tc).save()
                    if tsid != '-1':
                        ts = TestSet.objects.get(pk = tsid)
                        ts.test_cases.add(tc)
                        ts.save()
                    else:
                        pass
                    steps_remaining = True
                    n = 1
                    while steps_remaining:
                        try:
                            l1 = len(request.POST.get('action' + str(n), ''))
                            l2 = len(request.POST.get('expected' + str(n), ''))
                            if l1 == 0 or l2 == 0:
                                steps_remaining = False
                            else:
                                pass
                            n += 1
                        except (KeyError, TypeError):
                            steps_remaining = False
                    for i in range(n - 1):
                        st = TestCaseStep(
                            num = i + 1,
                            action = request.POST.get('action' + str(i + 1), ''),
                            expected = request.POST.get('expected' + str(i + 1), ''),
                            test_case = tc
                        )
                        st.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create test case'}
            elif action == 'newtestsetrun':
                try:
                    f_y = int(request.POST.get('from_y', ''))
                    f_m = int(request.POST.get('from_m', ''))
                    f_d = int(request.POST.get('from_d', ''))
                    t_y = int(request.POST.get('to_y', ''))
                    t_m = int(request.POST.get('to_m', ''))
                    t_d = int(request.POST.get('to_d', ''))
                    tsr = TestSetRun()
                    tsr.name = request.POST.get('name', '')
                    tsr.from_date = datetime.date(f_y, f_m, f_d)
                    tsr.to_date = datetime.date(t_y, t_m, t_d)
                    tsr.displayed = True
                    tsr.group = Group.objects.get(pk = int(request.POST.get('group', '')))
                    tsr.save()
                    logging.info("Test Set Run %s created" % tsr.name)
                    steps_remaining = True
                    n = 0
                    while steps_remaining:
                        try:
                            l1 = len(request.POST.get('tcid' + str(n), ''))
                            l2 = len(request.POST.get('tcname' + str(n), ''))
                            if l1 == 0 or l2 == 0:
                                steps_remaining = False
                            else:
                                pass
                            n += 1
                        except (KeyError, TypeError):
                            steps_remaining = False
                    test_cases = []
                    for i in range(n - 1):
                        test_cases.append(TestCase.objects.get(pk = int(request.POST.get('tcid' + str(i), ''))))
                    tsr.add_test_cases(test_cases)
                    tsr.deal()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create test set run : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create test set run'}
            elif action == 'chgdisp':
                try:
                    tsr = TestSetRun.objects.get(pk = request.POST.get('tsr', ''))
                    dispd = request.POST.get('disp', '')
                    if dispd == 'false':
                        tsr.displayed = False
                        logging.info("Test Set Run %s is now hidden" % tsr.name)
                    else:
                        tsr.displayed = True
                        logging.info("Test Set Run %s is now displayed" % tsr.name)
                    tsr.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not change test session status : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not change test session status'}
            elif action == 'newUser':
                try:
                    User(username = request.POST.get('username', '')).save()
                    u = User.objects.get(username = request.POST.get('username', ''))
                    logging.info("User %s created" % request.POST.get('username', ''))
                    if request.POST.get('team', '') != '-1':
                        g = Group.objects.get(pk = request.POST.get('team', ''))
                        u.groups.add(g)
                        privileged = request.POST.get('privileged', '')
                        permissions = [
                            'change_availability',
                            'add_jira',
                            'change_jira',
                            'change_testcaserun',
                            'change_testcasesteprun',
                        ]
                        if privileged == 'on':
                            permissions.extend([
                                'add_tag',
                                'change_tag',
                                'delete_tag',
                                'add_testcase',
                                'change_testcase',
                                'add_testcasestep',
                                'change_testcasestep',
                                'delete_testcasestep',
                                'add_testcaserun',
                                'add_testcasesteprun',
                                'delete_testcasesteprun',
                            ])
                        else:
                            pass
                        for p in permissions:
                            pm = Permission.objects.get(codename = p)
                            u.user_permissions.add(pm)
                        u.save()
                    else:
                        pass
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create user : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create user'}
            elif action == 'newTeam':
                try:
                    g = Group(name = request.POST.get('name', ''))
                    g.save()
                    logging.info("Group %s created" % g.name)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create team : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create team'}
            elif action == 'testSets':
                try:
                    test_set_name = request.POST.get('testSetName', '')
                    ptsi = int(request.POST.get('parentTestSetId', ''))
                    n = 0
                    while True:
                        try:
                            current_tc = request.POST.get('tc' + str(n), '')
                            l = len(current_tc)
                            if l == 0:
                                break
                            else:
                                pass
                            n += 1
                        except (TypeError, KeyError):
                            break
                    ts = TestSet(
                        name = test_set_name,
                        parent_test_set_id = ptsi,
                    )
                    ts.save()
                    logging.info("Test Set %s created" % ts.name)
                    for i in range(n):
                        ts.test_cases.add(TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))))
                    ts.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create test set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'The test set couldn\'t be created'}
            else:
                pass
    else:
        pass
    return HttpResponse(simplejson.dumps(json, default = dthandler))

@csrf_exempt
def home_menu(request):
    """
        returns the list of admin pages
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        return HttpResponse(simplejson.dumps(config.main_menu))
    else:
        return HttpResponse(simplejson.dumps({}))

@csrf_exempt
def planning_data(request):
    """
        returns the list of test case runs the logged in user has to perform
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    tcr = TestCaseRun.objects.filter(tester = request.session['uid'])
    json = []
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    for t in tcr:
        json.append({
            'title': t.title,
            'execution_date': t.execution_date,
            'id': t.id,
            'done': t.done,
        })
    return HttpResponse(simplejson.dumps(json, default=dthandler))

@csrf_exempt
def planning(request):
    """
        planning page (main page for testers)
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        c = Context({'tester_visa': u.username.upper(), 'tester_id': u.id})
        return render_to_response('test_manager/planning.html', c)
    else:
        if u.has_perm('test_manager.add_testcaserun'):
            try:
                tcr = TestCaseRun.objects.get(pk = request.POST.get('tcr', ''))
                tcr.execution_date = datetime.date(int(request.POST.get('year', '')), int(request.POST.get('month', '')), int(request.POST.get('day', '')))
                tcr.save()
                logging.info("Test Case Run %s moved to %s" % (tcr.title, tcr.execution_date.isoformat()))
                json = {'success': True}
            except Exception as detail:
                logging.error('could not move test case run : %s' % detail)
                json = {'success': False, 'errorMessage': 'could not move test case run'}
        else:
            logging.error('user %s attempted to move test case run' % u.username)
            json = {'success': False, 'errorMessage': 'You are not allowed to do this'}
        return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def availabilities(request):
    """
        a page to save one's own availabilities
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    return HttpResponse('Availabilities')

@csrf_exempt
def create_tc(request):
    """
        test case creation page
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.has_perm('test_manager.add_testcase'):
        c = Context({'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()})
        return render_to_response('test_manager/create_tc.html', c)
    else:
        return HttpResponseRedirect('/test_manager/')

@csrf_exempt
def create_tc_data(request):
    """
        returns the content of the dropdown fields of the form
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    return HttpResponse(simplejson.dumps(config.tc_data))

@csrf_exempt
def create_tc_updt(request):
    """
        save the new test case and redirect to the planning
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.has_perm('test_manager.add_testcase'):
        try:
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            precondition = request.POST.get('precondition', '')
            envir = request.POST.get('envir', '')
            os = request.POST.get('os', '')
            browser = request.POST.get('browser', '')
            release = request.POST.get('release', '')
            version = request.POST.get('version', '')
            module = request.POST.get('module', '')
            smodule = request.POST.get('smodule', '')
            criticity = request.POST.get('criticity', '')
            tc = TestCase(title = title,
                description = description,
                author = User.objects.get(pk = request.session['uid']),
                environment = envir,
                os = os,
                browser = browser,
                release = release,
                version = version,
                module = module,
                sub_module = smodule,
                criticity = int(criticity),
                precondition = precondition,
            )
            tc.save()
            logging.info("Test Case %s created" % tc.title)
            Tag(name = title, test_case = tc).save()
            tags = request.POST.get('tags', '')
            for tag in list(tags.split()):
                Tag(name = tag, test_case = tc).save()
            steps_remaining = True
            n = 1
            while steps_remaining:
                try:
                    l1 = len(request.POST.get('action' + str(n), ''))
                    l2 = len(request.POST.get('expected' + str(n), ''))
                    if l1 == 0 or l2 == 0:
                        steps_remaining = False
                    else:
                        pass
                    n += 1
                except (KeyError, TypeError):
                    steps_remaining = False
            for i in range(n - 1):
                st = TestCaseStep(
                    num = i + 1,
                    action = request.POST.get('action' + str(i + 1), ''),
                    expected = request.POST.get('expected' + str(i + 1), ''),
                    test_case = tc
                )
                st.save()
            return HttpResponse(simplejson.dumps({'success': True}))
        except Exception as detail:
            logging.error('could not create test case : %s' % detail)
            return HttpResponse(simplejson.dumps({'success': False, 'errorMessage': 'could not create test case'}))
    else:
        return HttpResponse(simplejson.dumps({}))
