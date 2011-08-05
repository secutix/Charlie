from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from test_manager.models import *
from django.core.context_processors import csrf
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import logout, login, authenticate
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from test_manager.config import *
import simplejson
import logging
import unicodedata

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
            try:
                request.session['auth'] = user.cust_auth
            except Exception:
                pass
            logging.info("User %s logged in" % user.username)
            login(request, user)
            if user.is_staff:
                json = {'success': True, 'next': '/manage/home/'}
            else:
                json = {'success': True, 'next': '/test_manager/planning/'}
        else:
            json = {'success': False, 'next': '/login/'};
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseRedirect(redirect)

def logout_view(request):
    """
        logout page
    """
    logging.info("User %s logged out" % User.objects.get(pk = request.session['uid']).username)
    logout(request)
    return HttpResponseRedirect("/login/")

def manage_planning(request):
    """
        Controller for the "Current sessions" view
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        json = []
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if request.method == 'GET':
            action = request.GET.get('action', '')
            if len(action) > 0:
                if action == 'allSessionsData':
                    try:
                        tsrid = int(request.GET.get('tsr_filter', ''))
                        t = TestSetRun.objects.get(pk = tsrid)
                        f_d = t.from_date
                        t_d = t.to_date
                        user_set = []
                        for u in set(Group.objects.get(pk = t.group_id).user_set.all().order_by('username')):
                            user_set.append(u)
                        user_set = list(set(user_set))
                        for u in list(user_set):
                            avails = Availability.objects.filter(day__gte = f_d, day__lte = t_d, user = u)
                            avs = []
                            for a in avails:
                                avs.append({
                                    'day': a.day,
                                    'time': a.remaining_time(),
                                })
                            tcr = []
                            for tr in list(TestCaseRun.objects.filter(tester = u, test_set_run = t).order_by('id')):
                                tcr.append({
                                    'title': tr.title,
                                    'execution_date': tr.execution_date,
                                    'length': tr.length,
                                    'qtip': str(tr.length) + ' min',
                                    'done': tr.done,
                                    'tcrid': tr.id,
                                })
                            json.append({'user': u.username.upper(), 'uid': u.id, 'tcr': tcr, 'avails': avs})
                    except ValueError:
                        user_set = []
                        f_d = datetime.date.today()
                        t_d = datetime.date.today()
                        for t in list(TestSetRun.objects.filter(displayed = True).order_by('name')):
                            if f_d > t.from_date:
                                f_d = t.from_date
                            else:
                                pass
                            if t_d < t.to_date:
                                t_d = t.to_date
                            else:
                                pass
                            for u in set(Group.objects.get(pk = t.group_id).user_set.all().order_by('username')):
                                user_set.append(u)
                        user_set = list(set(user_set))
                        for u in list(user_set):
                            avails = Availability.objects.filter(day__gte = f_d, day__lte = t_d, user = u)
                            avs = []
                            for a in avails:
                                avs.append({
                                    'day': a.day,
                                    'time': a.remaining_time(),
                                })
                            tcr = []
                            for tr in list(TestCaseRun.objects.filter(tester = u).order_by('title')):
                                if tr.test_set_run.displayed:
                                    tcr.append({
                                        'title': tr.title,
                                        'execution_date': tr.execution_date,
                                        'length': tr.length,
                                        'qtip': str(tr.length) + ' min',
                                        'done': tr.done,
                                        'tcrid': tr.id
                                    })
                            json.append({'user': u.username.upper(), 'uid': u.id, 'tcr': tcr, 'avails': avs})
                else:
                    pass
                return HttpResponse(simplejson.dumps(json, default = dthandler))
            else:
                try:
                    tsr = TestSetRun.objects.get(pk = int(request.GET.get('tsr', '')))
                    f_date = tsr.from_date
                    tsr_filter = request.GET.get('tsr', '')
                except Exception:
                    tsr_filter = 'all'
                    f_date = datetime.date.today()
                y = f_date.year
                m = f_date.month
                d = f_date.day
                c = {'d': d, 'm': m, 'y': y, 'tsr_filter': tsr_filter}
                c.update(csrf(request))
                return render_to_response('manage/planning.html', c)
        else:
            action = request.POST.get('action', '')
            if action == 'tcMove':
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
                    try:
                        av = Availability.objects.get(day = date, user = user)
                    except Availability.DoesNotExist:
                        Availability(
                            day = date,
                            user = user,
                            group = user.groups.all()[0],
                        ).save()
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
                    tr.module = tc.module
                    tr.sub_module = tc.sub_module
                    tr.criticity = tc.criticity
                    tr.precondition = tc.precondition
                    tr.length = tc.length
                    parentTs = 0
                    for t in TestSetRun.objects.filter(group = tester.groups.all()[0]):
                        if t.from_date < tr.execution_date:
                            parentTs = t
                            break
                    for t in TestSetRun.objects.filter(group = tester.groups.all()[0]):
                        if (t.from_date < tr.execution_date) and (parentTs.from_date < t.from_date):
                            parentTs = t
                    tr.test_set_run = parentTs
                    tr.done = False
                    tr.save()
                    tr.make_step_runs()
                    tr.save()
                    logging.info("Test Case Run %s created in Test Set Run %s" % (tr.title, tr.test_set_run.name))
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
                for tcr in list(TestCaseRun.objects.filter(tester = user).order_by('title')):
                    json.append({
                        'title': tcr.title,
                        'execution_date': tcr.execution_date,
                        'id': tcr.id,
                    })
            elif action == 'usersStore':
                for u in list(User.objects.all().order_by('username')):
                    json.append({
                        'id': u.id,
                        'username': u.username,
                    })
            else:
                pass
        return HttpResponse(simplejson.dumps(json, default = dthandler))
    else:
        return HttpResponse(simplejson.dumps(json))

def home(request):
    """
        test case set creation panel
    """
    json = []
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    if a_u.is_staff:
        if request.method == 'GET':
            try:
                action = request.GET.get('action', '')
            except Exception:
                pass
            if len(action) > 0:
                if action == 'testSets':
                    for tc in TestCase.objects.all().order_by('title'):
                        json.append({
                            'title': tc.title,
                            'id': tc.id,
                        })
                elif action == 'getTsTc':
                    try:
                        ts = TestSet.objects.get(pk = request.GET.get('tsid', ''))
                        for tc in ts.get_direct_test_cases():
                            json.append({
                                'title': tc.title,
                                'id': tc.id,
                            })
                    except Exception:
                        pass
                elif action == 'tcinfo':
                    try:
                        tc = TestCase.objects.get(pk = request.GET.get('tc', ''))
                        taglist = ''
                        for t in tc.get_tags():
                            taglist += t.name + ' '
                        json = {
                            'success': True,
                            'title': tc.title,
                            'description': tc.description,
                            'creation_date': tc.creation_date,
                            'author': tc.author.id,
                            'author_name': tc.author.username,
                            'module': tc.module,
                            'sub_module': tc.sub_module,
                            'criticity': tc.criticity,
                            'precondition': tc.precondition,
                            'length': tc.length,
                            'tags': taglist,
                        }
                        steps = []
                        for t in tc.get_steps():
                            if t.xp_image.name != '':
                                steps.append({
                                    'id': t.id,
                                    'num': t.num,
                                    'action': t.action,
                                    'expected': t.expected,
                                    'xp_image': t.xp_image._get_url(),
                                })
                            else:
                                steps.append({
                                    'id': t.id,
                                    'num': t.num,
                                    'action': t.action,
                                    'expected': t.expected,
                                    'xp_image': '',
                                })
                        json.update({'steps': steps})
                    except Exception as detail:
                        logging.error('failed to retrieve info : %s' % detail)
                        json = {'success': False}
                elif action == 'ispriv':
                    try:
                        u = User.objects.get(pk = request.GET.get('uid', ''))
                        json = {'success': True, 'priv': u.has_perm('test_manager.add_testcase')}
                    except Exception:
                        json = {'success': False}
                elif action == 'mainmenu':
                    json = config.main_menu
                elif action == 'teams':
                    for t in list(Group.objects.all().order_by('name')):
                        children = []
                        for u in list(t.user_set.all()):
                            children.append({'uid': u.id, 'text': u.username, 'leaf': True})
                        json.append({'leaf': False, 'gid': t.id, 'text': t.name, 'draggable': False, 'children': children, 'expanded': True, 'iconCls': 'folder'})
                    for u in list(User.objects.all().order_by('username')):
                        if len(list(u.groups.all())) == 0:
                            json.append({'uid': u.id, 'text': u.username, 'leaf': True})
                elif action == 'testsets':
                    rts = list(TestSet.objects.filter(parent_test_set__id = 0).order_by('name'))
                    for ts in rts:
                        json.append(ts.build())
                    ots = list(TestCase.objects.all().order_by('title'))
                    for t in ots:
                        if len(t.test_sets.all()) == 0:
                            tags = []
                            for tag in t.get_tags():
                                tags.append(tag.name)
                            json.append({'tsid': 0, 'text': t.title, 'value': t.id, 'leaf': True, 'tags': tags, 'qtip': str(t.length) + ' min'})
                elif action == 'history':
                    tsrlist_u = list(TestSetRun.objects.all())
                    tsrlist = sorted(tsrlist_u, key = lambda s: s.from_date)
                    for s in tsrlist:
                        json.append({
                            'name': s.name,
                            'tsid': s.id,
                            'from': s.from_date,
                            'to': s.to_date,
                            'team': s.group.id,
                            'teamname': s.group.name,
                            'disp': s.displayed,
                        })
                elif action == 'getgroups':
                    for g in list(Group.objects.all().order_by('name')):
                        json.append({
                            'gid': g.id,
                            'gname': g.name,
                        })
                elif action == 'combodata':
                    json = config.get_tc_data()
                else:
                    pass
            else:
                c = {}
                c.update(csrf(request))
                return render_to_response('manage/home.html', c)
        else:
            action = request.POST.get('action', '')
            if action == 'newtc':
                try:
                    tsid = request.POST.get('tsid', '')
                    title = request.POST.get('title', '')
                    description = request.POST.get('description', '')
                    precondition = request.POST.get('precondition', '')
                    module = request.POST.get('module', '')
                    modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                    smodule = request.POST.get('smodule', '')
                    criticity = int(request.POST.get('criticity', ''))
                    duration = int(request.POST.get('duration', ''))
                    try:
                        Config.objects.get(ctype = 'module', name = module)
                    except Config.DoesNotExist:
                        c = Config(ctype = 'module', name = module, value = modulev)
                        c.save()
                    try:
                        Config.objects.get(ctype = modulev, name = smodule)
                    except Config.DoesNotExist:
                        c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                        c.save()
                    if criticity > 5:
                        criticity = 5
                    else:
                        pass
                    if criticity < 1:
                        criticity = 1
                    else:
                        pass
                    tc = TestCase(
                        title = title,
                        description = description,
                        author = User.objects.get(pk = request.session['uid']),
                        module = Config.objects.get(ctype = 'module', name = module).value,
                        sub_module = Config.objects.get(ctype = modulev, name = smodule).value,
                        criticity = criticity,
                        precondition = precondition,
                        length = duration,
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
                            if l1 == 0:
                                steps_remaining = False
                            else:
                                n += 1
                        except (KeyError, TypeError):
                            steps_remaining = False
                    n -= 1
                    for i in range(n):
                        st = TestCaseStep(
                            num = i + 1,
                            action = request.POST.get('action' + str(i + 1), ''),
                            expected = request.POST.get('expected' + str(i + 1), ''),
                            test_case = tc,
                        )
                        if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                            st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                        else:
                            pass
                        st.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create test case'}
            elif action == 'dealagain':
                try:
                    tsr = TestSetRun.objects.get(pk = int(request.POST.get('tsid', '')))
                    tc_to_add = []
                    for t in tsr.get_test_cases():
                        tc_to_add.append(t.test_case)
                        t.delete()
                    tsr.add_test_cases(tc_to_add)
                    tsr.deal()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not deal again : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not deal again'}
            elif action == 'edittc':
                try:
                    tcid = int(request.POST.get('tcid', ''))
                    tsid = int(request.POST.get('tsid', ''))
                    tc = TestCase.objects.get(pk = tcid)
                    tc.title = request.POST.get('title', '')
                    tc.description = request.POST.get('description', '')
                    tc.precondition = request.POST.get('precondition', '')
                    module = request.POST.get('module', '')
                    modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                    smodule = request.POST.get('smodule', '')
                    try:
                        Config.objects.get(ctype = 'module', name = module)
                    except Config.DoesNotExist:
                        c = Config(ctype = 'module', name = module, value = modulev)
                        c.save()
                    try:
                        Config.objects.get(ctype = modulev, name = smodule)
                    except Config.DoesNotExist:
                        c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                        c.save()
                    tc.module = Config.objects.get(ctype = 'module', name = module).value
                    tc.sub_module = Config.objects.get(ctype = modulev, name = smodule).value
                    tc.criticity = int(request.POST.get('criticity', ''))
                    tc.length = int(request.POST.get('duration', ''))
                    tc.save()
                    logging.info("Test Case %s modified" % tc.title)
                    tags = request.POST.get('tags', '')
                    Tag(name = tc.title, test_case = tc).save()
                    for tag in tc.get_tags():
                        tag.delete()
                    for tag in list(tags.split()):
                        Tag(name = tag, test_case = tc).save()
                    if tsid != -1:
                        ts = TestSet.objects.get(pk = tsid)
                        ts.test_cases.add(tc)
                        ts.save()
                    else:
                        pass
                    steps_remaining = True
                    old_tc = []
                    for step in tc.get_steps():
                        old_tc.append(step.id)
                    n = 1
                    while steps_remaining:
                        try:
                            l1 = len(request.POST.get('action' + str(n), ''))
                            if l1 == 0:
                                steps_remaining = False
                            else:
                                n += 1
                        except (KeyError, TypeError):
                            logging.info("exit")
                            steps_remaining = False
                    n -= 1
                    for i in range(n):
                        try:
                            st = TestCaseStep.objects.get(pk = int(request.POST.get('sid' + str(i + 1), '')))
                            old_tc.remove(st.id)
                            st.num = i + 1
                            st.action = request.POST.get('action' + str(i + 1), '')
                            st.expected = request.POST.get('expected' + str(i + 1), '')
                        except (TestCaseStep.DoesNotExist, ValueError):
                            st = TestCaseStep(
                                num = i + 1,
                                action = request.POST.get('action' + str(i + 1), ''),
                                expected = request.POST.get('expected' + str(i + 1), ''),
                                test_case = tc
                            )
                        if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                            st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                        else:
                            pass
                        st.save()
                    for t in old_tc:
                        ts = TestCaseStep.objects.get(pk = t)
                        if len(ts.xp_image.name) != 0:
                            ts.xp_image.delete()
                        ts.delete()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Could not edit test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Could not edit test case'}
            elif action == 'editTs':
                try:
                    ts = TestSet.objects.get(pk = request.POST.get('tsid', ''))
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
                    ts.name = test_set_name
                    ts.parent_test_set_id = ptsi
                    ts.save()
                    logging.info("Test Set %s created" % ts.name)
                    for t in ts.get_direct_test_cases():
                        logging.info('removed %s from %s' % (t.title, ts.name))
                        ts.test_cases.remove(t)
                    for i in range(n):
                        logging.info('added %s to %s' % (TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))).title, ts.name))
                        ts.test_cases.add(TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))))
                    ts.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Could not edit Test Set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not edit test set'}
            elif action == 'delts':
                try:
                    ts = TestSet.objects.get(pk=request.POST.get('ts', ''))
                    logging.info("Test Set %s deleted" % ts.name)
                    ts.delete()
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'could not delete test set'}
                    logging.error('could not delete test set : %s' % detail)
            elif action == 'delteam':
                try:
                    g = Group.objects.get(pk = request.POST.get('t', ''))
                    logging.info("Group %s deleted" % g.name)
                    g.delete()
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'could not delete team'}
                    logging.error('could not delete team : %s' % detail)
            elif action == 'deltc':
                try:
                    tc = TestCase.objects.get(pk = request.POST.get('tc', ''))
                    tsid = int(request.POST.get('ts', ''))
                    if tsid != -1:
                        # remove this test case from this test set
                        ts = TestSet.objects.get(pk = tsid)
                        ts.test_cases.remove(tc)
                        logging.info("Test Case %s deleted from %s" % (tc.title, ts.name))
                    else:
                        # permanently delete this test case
                        tc.delete()
                        logging.info("Test Case %s deleted" % tc.title)
                    json = {'success': True}
                except Exception as detail:
                    logging.error("could not create test case %s" % detail)
                    json = {'success': False, 'errorMessage': 'could not delete test case'}
            elif action == 'deluser':
                try:
                    u = User.objects.get(pk = request.POST.get('u', ''))
                    if u.id != request.session['uid']:
                        logging.info("User %s deleted" % u.username)
                        u.delete()
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'User is authenticated'}
                except Exception as detail:
                    logging.error('could not delete user : %s' % detail)
                    json = {'success': False, 'errorMessage': 'An error occured'}
            elif action == 'mvts':
                try:
                    cts = TestSet.objects.get(pk = request.POST.get('cts', ''))
                    if request.POST.get('pts', '') == '-1':
                        cts.parent_test_set_id = 0
                        logging.info("Test Set %s moved to the root" % cts.name)
                    else:
                        cts.parent_test_set = TestSet.objects.get(pk = request.POST.get('pts', ''))
                        logging.info("Test Set %s moved inside of Test Set %s" % (cts.name, cts.parent_test_set.name))
                    cts.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move test set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move test set'}
            elif action == 'mvtc':
                try:
                    tc = TestCase.objects.get(pk = request.POST.get('tc', ''))
                    if request.POST.get('tts', '') != '-1':
                        tts = TestSet.objects.get(pk = request.POST.get('tts', ''))
                        tts.test_cases.add(tc)
                        logging.info("Test Case %s added to Test Set %s" % (tc.title, tts.name))
                        tts.save()
                    else:
                        pass
                    if request.POST.get('fts', '') != '-1':
                        fts = TestSet.objects.get(pk = request.POST.get('fts', ''))
                        fts.test_cases.remove(tc)
                        logging.info('Test Case %s removed from Test Set %s' % (tc.title, fts.name))
                        fts.save()
                    else:
                        pass
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move test case'}
            elif action == 'cptc':
                try:
                    tc = TestCase.objects.get(pk = request.POST.get('tc', ''))
                    if request.POST.get('ts', '') != '-1':
                        ts = TestSet.objects.get(pk = request.POST.get('ts', ''))
                        ts.test_cases.add(tc)
                        ts.save()
                        logging.info("Test Case %s copied to Test Set %s" % (tc.title, ts.name))
                    else:
                        logging.info("Test Case %s cannot be copied to root" % tc.title)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not copy test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not copy test case'}
            elif action == 'mvuser':
                try:
                    u = User.objects.get(pk = request.POST.get('user', ''))
                    for g in u.groups.all():
                        u.groups.remove(g)
                    u.save()
                    gid = int(request.POST.get('team', ''))
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
            elif action == 'chgdisp':
                try:
                    tsr = TestSetRun.objects.get(pk = int(request.POST.get('tsr', '')))
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
                            if l1 == 0:
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
            elif action == 'editUser':
                try:
                    u = User.objects.get(pk = request.POST.get('uid', ''))
                    u.username = request.POST.get('username', '')
                    u.save()
                    if u.is_staff:
                        pass
                    else:
                        is_priv = False
                        if request.POST.get('privileged', '') == 'on':
                            is_priv = True
                        special_permissions = [
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
                        ]
                        for p in special_permissions:
                            pm = Permission.objects.get(codename = p)
                            if is_priv:
                                u.user_permissions.add(pm)
                            else:
                                u.user_permissions.remove(pm)
                        u.save()
                    logging.info('User %s has been modified' % u.username)
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'Unable to modify this user'}
                    logging.error('Unable to edit user : %s' % detail)
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
        return HttpResponse(simplejson.dumps(json, default = dthandler))
    else:
        return HttpResponseRedirect('/')

def planning(request):
    """
        planning page (main page for testers)
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        try:
            action = request.GET.get('action', '')
            if action == 'events':
                tcr = TestCaseRun.objects.filter(tester = request.session['uid']).order_by('id')
                json = []
                dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
                for t in tcr:
                    json.append({
                        'title': t.title,
                        'execution_date': t.execution_date,
                        'tcrid': t.id,
                        'done': t.done,
                    })
                return HttpResponse(simplejson.dumps(json, default=dthandler))
            else:
                pass
        except Exception:
            pass
        c = Context({'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
        c.update(csrf(request))
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

def availabilities(request):
    """
        a page to save one's own availabilities
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    u = User.objects.get(pk = request.session['uid'])
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    if request.method == 'GET':
        action = request.GET.get('action', '')
        if len(action) > 0:
            json = []
            if action == 'avails':
                avs = Availability.objects.filter(user = u)
                for a in avs:
                    json.append({
                        'pct': a.avail,
                        'title': str(a.avail) + ' %',
                        'execution_date': a.day,
                        'tcrid': a.id,
                    })
            else:
                pass
            return HttpResponse(simplejson.dumps(json, default = dthandler))
        else:
            c = Context({'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
            c.update(csrf(request))
            return render_to_response('test_manager/availabilities.html', c)
    else:
        action = request.POST.get('action', '')
        json = []
        if action == 'chgavail':
            try:
                y = int(request.POST.get('y', ''))
                m = int(request.POST.get('m', ''))
                d = int(request.POST.get('d', ''))
                pct = int(request.POST.get('pct', ''))
                a_day = datetime.date(y, m, d)
                a = Availability.objects.get(user = u, day = a_day)
                logging.info('User %s changed availability for %r from %d to %d' % (u.username, a_day, a.avail, pct))
                a.avail = pct
                a.save()
                json = {'success': True}
            except Exception as detail:
                json = {'success': False, 'errorMessage': 'Could not change availability'}
                logging.error('User could not change availability : %s' % detail)
        else:
            pass
        return HttpResponse(simplejson.dumps(json))

def create_tc(request):
    """
        test case creation page
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if a_u.has_perm('test_manager.add_testcase'):
        if request.method == 'GET':
            try:
                action = request.GET.get('action', '')
                if action == 'comboData':
                    return HttpResponse(simplejson.dumps(config.get_tc_data()))
                else:
                    pass
            except Exception:
                pass
            c = {'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()}
            c.update(csrf(request))
            return render_to_response('test_manager/create_tc.html', c)
        else:
            try:
                title = request.POST.get('title', '')
                description = request.POST.get('description', '')
                precondition = request.POST.get('precondition', '')
                module = request.POST.get('module', '')
                modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                smodule = request.POST.get('smodule', '')
                criticity = int(request.POST.get('criticity', ''))
                duration = int(request.POST.get('duration', ''))
                if criticity > 5:
                    criticity = 5
                else:
                    pass
                if criticity < 1:
                    criticity = 1
                else:
                    pass
                try:
                    Config.objects.get(ctype = 'module', name = module)
                except Config.DoesNotExist:
                    c = Config(ctype = 'module', name = module, value = modulev)
                    c.save()
                try:
                    Config.objects.get(ctype = modulev, name = smodule)
                except Config.DoesNotExist:
                    c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                    c.save()
                tc = TestCase(title = title,
                    description = description,
                    author = User.objects.get(pk = request.session['uid']),
                    module = Config.objects.get(ctype = 'module', name = module).value,
                    sub_module = Config.objects.get(ctype = modulev, name = smodule).value,
                    criticity = criticity,
                    precondition = precondition,
                    length = duration,
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
                        if l1 == 0:
                            steps_remaining = False
                        else:
                            pass
                        n += 1
                    except (KeyError, TypeError):
                        steps_remaining = False
                n -= 2
                for i in range(n):
                    st = TestCaseStep(
                        num = i + 1,
                        action = request.POST.get('action' + str(i + 1), ''),
                        expected = request.POST.get('expected' + str(i + 1), ''),
                        test_case = tc,
                    )
                    if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                        st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                    else:
                        pass
                    st.save()
                return HttpResponse(simplejson.dumps({'success': True}))
            except Exception as detail:
                logging.error('could not create test case : %s' % detail)
                return HttpResponse(simplejson.dumps({'success': False, 'errorMessage': 'could not create test case'}))
    else:
        return HttpResponseRedirect('/test_manager/')

def do_test(request):
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        action = request.GET.get('action', '')
        if len(action) == 0:
            try:
                tc = TestCaseRun.objects.get(pk = int(request.GET.get('t', '')))
                request.session['ctcr'] = tc.id
                c = Context({'t': tc.id, 'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
                c.update(csrf(request))
                return render_to_response('test_manager/do_test.html', c)
            except Exception as detail:
                logging.error('could not find test set run : %s' % detail)
                return HttpResponse('erreur...')
        else:
            json = []
            dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
            try:
                tcr = TestCaseRun.objects.get(pk = request.session['ctcr'])
                if tcr.tester_id != request.session['uid']:
                    json = {'success': False, 'errorMessage': 'This test case run was given to another tester'}
                else:
                    if action == 'tcrinfo':
                        try:
                            module = Config.objects.get(ctype = 'module', value = tcr.module).name
                        except Config.DoesNotExist:
                            module = tcr.module
                        try:
                            sub_module = Config.objects.get(ctype = tcr.module, value = tcr.sub_module).name
                        except Config.DoesNotExist:
                            sub_module = tcr.sub_module
                        os = []
                        for o in list(Config.objects.filter(ctype = 'os')):
                            os.append({'name': o.name, 'value': o.value})
                        envir = []
                        for o in list(Config.objects.filter(ctype = 'envir')):
                            envir.append({'name': o.name, 'value': o.value})
                        browser = []
                        for o in list(Config.objects.filter(ctype = 'browser')):
                            browser.append({'name': o.name, 'value': o.value})
                        release = []
                        for o in list(Config.objects.filter(ctype = 'release')):
                            release.append({'name': o.name, 'value': o.value})
                        version = []
                        for o in list(Config.objects.filter(ctype = 'version')):
                            version.append({'name': o.name, 'value': o.value})
                        tags = []
                        for o in tcr.get_tags():
                            tags.append(o.name)
                        steps = []
                        for o in tcr.get_steps():
                            jiras = []
                            for j in o.get_jiras():
                                jiras.append({
                                    'name': j.name,
                                })
                            try:
                                xp_image_url = o.xp_image._get_url()
                            except Exception:
                                xp_image_url = ''
                            to_append = {
                                'id': o.id,
                                'num': o.num,
                                'action': o.action,
                                'expected': o.expected,
                                'xp_image': xp_image_url,
                                'comment': o.comment,
                                'jiras': jiras,
                            }
                            if o.done:
                                to_append.update({'status': o.status})
                            else:
                                to_append.update({'status': 'undefined'})
                            steps.append(to_append)
                        tc = {
                            'precondition': tcr.precondition,
                            'module': module,
                            'creation_date': tcr.creation_date,
                            'done': tcr.done,
                            'title': tcr.title,
                            'execution_date': tcr.execution_date,
                            'environment': tcr.environment,
                            'version': tcr.version,
                            'description': tcr.description,
                            'criticity': tcr.criticity,
                            'sub_module': sub_module,
                            'length': tcr.length,
                            'release': tcr.release,
                            'author': tcr.author_id,
                            'os': tcr.os,
                            'browser': tcr.browser,
                            'tags': tags,
                            'steps': steps,
                        }
                        json = {
                            'success': True,
                            'tc': tc,
                            'config': {
                                'os': os,
                                'envir': envir,
                                'browser': browser,
                                'release': release,
                                'version': version,
                            },
                        }
                    else:
                        json = {'success': False, 'errorMessage': 'wrong request'}
            except Exception as detail:
                logging.error('could not retrieve test case run info : %s' % detail)
                json = {'success': False, 'errorMessage': 'could not retrieve test case run info'}
            return HttpResponse(simplejson.dumps(json, default = dthandler))
    elif request.method == 'POST':
        json = []
        action = request.POST.get('action', '')
        if action == 'setstatus':
            try:
                sid = TestCaseStepRun.objects.get(pk = int(request.POST.get('sid', '')))
                is_ok = True
                log_msg = 'OK'
                if request.POST.get('is_ok', '') == 'false':
                    is_ok = False
                    log_msg = 'KO'
                sid.status = is_ok
                sid.done = True
                sid.save()
                logging.info('Step Run "%s" is %s' % (sid, log_msg))
                tcr = sid.test_case
                finished = False
                if len(tcr.os) * len(tcr.version) * len(tcr.environment) * len(tcr.release) * len(tcr.browser) > 0:
                    finished = True
                    for s in tcr.get_steps():
                        finished &= s.done
                    if(finished):
                        tcr.done = True
                        tcr.save()
                    else:
                        pass
                else:
                    pass
                json = {'success': True, 'over': finished}
            except Exception as detail:
                json = {'success': False, 'errorMessage': 'could not change test step status'}
                logging.error('Could not change test case step run status : %s' % detail)
        elif action == 'settcrparam':
            try:
                my_ctype = request.POST.get('param', '')
                my_value = request.POST.get('value', '')
                try:
                    param = Config.objects.get(ctype = my_ctype, value = my_value)
                except Config.DoesNotExist:
                    param = Config(
                        ctype = my_ctype,
                        value = my_value.lower().encode('ascii', 'ignore').replace(' ', '_'),
                        name = my_value,
                    )
                    param.save()
                tcr = TestCaseRun.objects.get(pk = int(request.session['ctcr']))
                if my_ctype == 'os':
                    tcr.os = param.value
                elif my_ctype == 'version':
                    tcr.version = param.value
                elif my_ctype == 'envir':
                    tcr.environment = param.value
                elif my_ctype == 'release':
                    tcr.release = param.value
                elif my_ctype == 'browser':
                    tcr.browser = param.value
                else:
                    pass
                tcr.save()
                finished = False
                if len(tcr.os) * len(tcr.version) * len(tcr.environment) * len(tcr.release) * len(tcr.browser) > 0:
                    finished = True
                    for s in tcr.get_steps():
                        finished &= s.done
                    if(finished):
                        tcr.done = True
                        tcr.save()
                    else:
                        pass
                else:
                    pass
                json = {'success': True, 'over': finished}
                logging.info('tcr %s : Set attribute %s to %s' % (tcr.__unicode__(), my_ctype, my_value))
            except Exception as detail:
                logging.error('Could not set this parameter : %s' % detail)
                json = {'error': True, 'errorMessage': 'Could not set this parameter'}
        elif action == 'addcomment':
            try:
                sid = TestCaseStepRun.objects.get(pk = int(request.POST.get('sid', '')))
                comment = request.POST.get('comment', '')
                sid.comment = comment
                sid.save()
                json = {'success': True}
            except Exception as detail:
                logging.error('Could not add comment : %s' % detail)
                json = {'success': False, 'errorMessage': 'Could not edit the comment for this step'}
        else:
            pass
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponse('erreur...')
