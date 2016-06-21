from django.shortcuts import render
from .models import Problem, Customuser, Setting, AllowedMail
from django.contrib.auth.models import User, Group, Permission
from .forms import Loginform, Signupform, Editform, ChangePasswordForm, ForgotPasswordForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import datetime
import codelabs.config as config
import base64
from datetime import timedelta, datetime as dt
from django.utils import timezone
from .pydiscourse import sso as discourse_sso
import requests as rq

def forgot_password(request):
    if request.user.is_authenticated():
        return HttpResponseNotFound(render(request, 'general.html', config.DENIED))
    if request.method == 'GET':
        forgotpasswordform = ForgotPasswordForm()
        return render(request, 'forgotpassword.html', context = {'form':forgotpasswordform})
    forgotpasswordform = ForgotPasswordForm(request.POST)
    if not forgotpasswordform.is_valid():
        return render(request, 'forgotpassword.html', context = {'form':forgotpasswordform})
    mailid = forgotpasswordform.cleaned_data['email']
    if len(AllowedMail.objects.filter(mailid = mailid)) == 0:
        return render(request, 'forgotpassword.html', context = {'form':forgotpasswordform, 'not_in_database':True})
    userarr = User.objects.filter(email = mailid)
    if len(userarr) == 0:
        return render(request, 'forgotpassword.html', context = {'form':forgotpasswordform, 'donotexist':True})
    user = userarr[0]
    passwordkey = config.generate_key()
    config.send_change_password_mail(passwordkey, mailid, user.username)
    user.customuser.passwordkey = passwordkey
    user.customuser.passwordkey_exdate = timezone.now() + timedelta(minutes = 15)
    user.customuser.save()
    user.save()
    return render(request, 'general.html', context = config.forgotpass_info(mailid))    
    
def change_password(request):
    if request.user.is_authenticated():
        user = request.user
        passwordkey = 'NULL'
    elif 'passwordkey' in request.GET:
        passwordkey = request.GET['passwordkey']
        userarr = Customuser.objects.filter(passwordkey = passwordkey)
        if not userarr:
            print(1)
            return HttpResponseNotFound(render(request, 'general.html', config.NOTFOUND_ERROR))
        user = userarr[0].user
        if timezone.now() > user.customuser.passwordkey_exdate:
            print(2)
            return HttpResponseNotFound(render(request, 'general.html', config.NOTFOUND_ERROR))
    else:
        print(3)
        return HttpResponseNotFound(render(request, 'general.html', config.NOTFOUND_ERROR))
    if request.method == 'GET':
        changepasswordform = ChangePasswordForm()
        return render(request, 'changepassword.html', context = {'form':changepasswordform, 'passwordkey':passwordkey})
    changepasswordform = ChangePasswordForm(request.POST)
    if not changepasswordform.is_valid():
        return render(request, 'changepassword.html', context = {'form':changepasswordform, 'passwordkey':passwordkey})
    if not changepasswordform.cleaned_data['newpassword'] == changepasswordform.cleaned_data['confirmnewpassword']:
        changepasswordform = ChangePasswordForm()
        return render(request, 'changepassword.html', context = {'form':changepasswordform, 'donotmatch' : True, 'passwordkey':passwordkey})
    password = changepasswordform.cleaned_data['newpassword']
    user.customuser.password = password
    user.customuser.passwordkey_exdate = dt.now() - timedelta(minutes = 20)
    user.customuser.save()
    user.set_password(password)
    user.save()
    return render(request, 'general.html', config.PASSCHANGE_SUCCESS)
    

@login_required
def profile(request,handle):
    userarr = User.objects.filter(username=handle)
    if not userarr:
        return HttpResponseNotFound(render(request, 'general.html', config.NOTFOUND_ERROR))
    
    user = userarr[0]
    spojproblems = user.problem_set.filter(platform='spoj')
    hackerrankproblems = user.problem_set.filter(platform='hackerrank')
    codechefproblems = user.problem_set.filter(platform='codechef')
    geeksforgeeksproblems = user.problem_set.filter(platform='geeksforgeeks')
    context = {
                'user' : user,
                'spojproblems' : spojproblems, 
                'hackerrankproblems' : hackerrankproblems, 
                'codechefproblems' : codechefproblems, 
                'geeksforgeeksproblems' : geeksforgeeksproblems
            }
    return render(request, 'profile.html', context)
    
@login_required
def allproblems(request):
    
    sort = request.GET.get('sort', 'solved')
    
    problems = Problem.objects.order_by('-' + sort)
    currentuser = request.user
    solvedproblems = currentuser.problem_set.all()
    context = {'problems' : problems, 'solvedproblems' : solvedproblems}
    return render(request, 'allproblems.html', context)
 
@login_required   
def problem(request,platform,code):
    problemarr = Problem.objects.filter(platform=platform,code=code)
    if not problemarr:
        return HttpResponseNotFound(render(request, 'general.html', config.NOTFOUND_ERROR))
    problem = problemarr[0]
    currentuser = request.user
    users = problem.users.all()
    issolved = currentuser in users
    context = {'problem':problem, 'users':users, 'currentuser':currentuser, 'developmentmode' : settings.DEBUG }
    return render(request, 'problem.html', context)
    
@login_required   
def profile_pic(request,handle):
    userarr = User.objects.filter(username=handle)
    if not userarr:
        return HttpResponse(config.CODEARENA_DOMAIN + '/static/img/usr-icon.png', content_type="image/png")
    user = userarr[0]
    return HttpResponse(user.customuser.pic, content_type="image/png")

@login_required
def edit(request):
    
    profileeditflag = Setting.objects.filter(parameter = 'profileeditflag')[0].value
    profileeditflag = profileeditflag == 1
    if not profileeditflag:
        return render(request, 'general.html', config.DENIED)
    user = request.user
    data = {
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'rollno' : user.customuser.rollno,
            'batch' : config.FIRST_PASS_OUT_BATCH if user.customuser.batch == 0 else user.customuser.batch,
            'branch' : user.customuser.branch,
            'spojhandle' : user.customuser.spojhandle,
            'hackerrankhandle' : user.customuser.hackerrankhandle,
            'codechefhandle' : user.customuser.codechefhandle,
            'geeksforgeekshandle' : user.customuser.geeksforgeekshandle,
            'topcoderhandle' : user.customuser.topcoderhandle,
            'codeforceshandle' : user.customuser.codeforceshandle,
            'interviewbithandle' : user.customuser.interviewbithandle,
            'picflag' : True if user.customuser.picflag == 1 else False
            }
    spojflag = user.customuser.spojflag
    hackerrankflag = user.customuser.hackerrankflag
    codechefflag = user.customuser.codechefflag
    geeksforgeeksflag = user.customuser.geeksforgeeksflag
    topcoderflag = user.customuser.topcoderflag
    codeforcesflag = user.customuser.codeforcesflag
    interviewbitflag = user.customuser.interviewbitflag
    
    if request.method == 'GET':
        editform = Editform(data)
        
        return render(request, 'edit.html', {'form': editform , 'interviewbitflag':interviewbitflag, 'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag, 'topcoderflag':topcoderflag, 'codeforcesflag':codeforcesflag, 'geeksforgeeksflag':geeksforgeeksflag })
    
    editform = Editform(request.POST, request.FILES, initial = data)
    
    if not editform.is_valid():
        return render(request, 'edit.html', {'form': editform , 'interviewbitflag':interviewbitflag,'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag, 'topcoderflag':topcoderflag, 'codeforcesflag':codeforcesflag,'geeksforgeeksflag':geeksforgeeksflag })
        
    if not editform.has_changed():
        return render(request, 'edit.html', {'form': editform , 'interviewbitflag':interviewbitflag,'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag, 'topcoderflag':topcoderflag, 'codeforcesflag':codeforcesflag,'geeksforgeeksflag':geeksforgeeksflag })
    
    if editform.cleaned_data['spojhandle'] != data['spojhandle']:
        spojflag = 2
        
    if editform.cleaned_data['hackerrankhandle'] != data['hackerrankhandle']:
        hackerrankflag = 2
        
    if editform.cleaned_data['codechefhandle'] != data['codechefhandle']:
        codechefflag = 2
    
    if editform.cleaned_data['geeksforgeekshandle'] != data['geeksforgeekshandle']:
        geeksforgeeksflag = 2
        
    if editform.cleaned_data['topcoderhandle'] != data['topcoderhandle']:
        topcoderflag = 2
        
    if editform.cleaned_data['codeforceshandle'] != data['codeforceshandle']:
        codeforcesflag = 2
    
    if editform.cleaned_data['interviewbithandle'] != data['interviewbithandle']:
        interviewbitflag = 2
        
    user.first_name  = editform.cleaned_data['first_name']
    user.last_name = editform.cleaned_data['last_name']
    user.customuser.rollno = editform.cleaned_data['rollno']
    user.customuser.batch = editform.cleaned_data['batch']
    user.customuser.branch = editform.cleaned_data['branch']
    
    if 'picflag' in editform.data:
        if editform.cleaned_data['pic']:
            print('hello')
            picdata = editform.cleaned_data['pic'].read()
            user.customuser.pic = picdata
            user.customuser.picflag = 1
    else:
        print('bye')
        user.customuser.picflag = 2
        user.customuser.pic = b'kj'
    
    user.customuser.spojhandle = editform.cleaned_data['spojhandle']
    user.customuser.spojflag = spojflag
    user.customuser.hackerrankhandle = editform.cleaned_data['hackerrankhandle']
    user.customuser.hackerrankflag = hackerrankflag
    user.customuser.codechefhandle = editform.cleaned_data['codechefhandle']
    user.customuser.codechefflag = codechefflag
    user.customuser.geeksforgeekshandle = editform.cleaned_data['geeksforgeekshandle']
    user.customuser.geeksforgeeksflag = geeksforgeeksflag
    user.customuser.topcoderhandle = editform.cleaned_data['topcoderhandle']
    user.customuser.topcoderflag = topcoderflag
    user.customuser.codeforceshandle = editform.cleaned_data['codeforceshandle']
    user.customuser.codeforcesflag = codeforcesflag
    user.customuser.interviewbithandle = editform.cleaned_data['interviewbithandle']
    user.customuser.interviewbitflag = interviewbitflag
    user.save()
    user.customuser.save()
    return render(request, 'edit.html', {'form': editform , 'interviewbitflag':interviewbitflag,'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag, 'topcoderflag':topcoderflag, 'codeforcesflag':codeforcesflag,'geeksforgeeksflag':geeksforgeeksflag })
    
def activate(request):
    activatekey = request.GET.get('activatekey')
    cuser = Customuser.objects.filter(activatekey = activatekey)
    if len(cuser) == 1:
        cuser = cuser[0]
        cuser.user.is_active = True
        cuser.user.save()
        cuser.save()
        return render(request, 'general.html', config.ACTIVATION_SUCCEEDED)
    return render(request, 'general.html', config.ACTIVATION_FAILED)
    
def signup(request):
    if request.user.is_authenticated():
        return render(request, 'general.html', config.DENIED)
        
    signupflag = Setting.objects.filter(parameter = 'signupflag')[0].value
    signupflag = signupflag == 1
    if not signupflag:
        return render(request, 'general.html', config.DENIED)
    
    if request.method == 'GET':
        signupform = Signupform()
        return render(request, 'signup.html', {'form': signupform})
        
    donotmatch = False
    alreadyexist = False
    donotexist = False
    signupform = Signupform(request.POST)
    if signupform.is_valid():
        if AllowedMail.objects.filter(mailid = signupform.cleaned_data['email']).exists():
            if signupform.cleaned_data['password'] == signupform.cleaned_data['confirmpassword']:
                if not User.objects.filter(username=signupform.cleaned_data['handle']).exists():
                    activatekey = config.generate_activation_key()
                    config.send_activation_mail(signupform.cleaned_data['handle'], signupform.cleaned_data['email'], activatekey)
                    user = User.objects.create(
                        first_name = signupform.cleaned_data['first_name'],
                        last_name = signupform.cleaned_data['last_name'],
                        username = signupform.cleaned_data['handle'],
                        email = signupform.cleaned_data['email'],
                        is_active = False
                    )
                    user.set_password(signupform.cleaned_data['password'])
                    user.groups = [Group.objects.get(name = 'student_group')]
                    user.save()
                    
                    customuser = Customuser.objects.create(
                        user = user,
                        rollno = signupform.cleaned_data['rollno'],
                        batch = signupform.cleaned_data['batch'],
                        branch = signupform.cleaned_data['branch']
                    )
                    customuser.save()
                    return render(request, 'general.html', config.activation_info(signupform.cleaned_data['email']))
                else:
                    alreadyexist = True
            else:
                donotmatch = True
        else:
            donotexist = True
    
    signupform = Signupform(request.POST)
    return render(request, 'signup.html', 
            {'form': signupform , 'donotmatch':donotmatch, 'alreadyexist':alreadyexist, 'donotexist':donotexist}
    )
    
@login_required
def discourse_login(request):
    if config.DISCOURSE_FLAG:
        email = request.user.email
        userid = request.user.id
        handle = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        avatar_url = config.CODEARENA_DOMAIN + '/profilepic/' + handle
        is_admin = 'true' if request.user.groups.all()[0].name == 'admin_group' else 'false'
        payload = request.GET['sso']
        sig = request.GET['sig']
        nonce = discourse_sso.sso_validate(payload, sig, config.DISCOURSE_SSO_SECRET)
        discourse_sso_login_url = config.DISCOURSE_URL + discourse_sso.sso_redirect_url(nonce,config.DISCOURSE_SSO_SECRET,email,userid,handle,name,avatar_url,is_admin)
        return HttpResponseRedirect(discourse_sso_login_url)
    return render(request, 'general.html', config.DENIED)
    
def log_in(request):
    invalid = False
    if request.user.is_authenticated():
        return render(request, 'general.html', config.DENIED)
        
    if request.method == 'GET':
        loginform = Loginform()
        if 'next' in request.GET:
                return render(request, 'login.html', {'form': loginform, 'next' : request.GET['next'] })
        return render(request, 'login.html', {'form': loginform})
        
    loginform = Loginform(request.POST)
    
    if loginform.is_valid():
        user = authenticate(username=loginform.cleaned_data['handle'], password=loginform.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                if 'next' in request.POST:
                    return HttpResponseRedirect(request.POST.get('next'))
                
                return HttpResponseRedirect('/allproblems')
            else:
                return render(request, 'login.html', {'form': loginform, 'inactive':True})
    
    return render(request, 'login.html', {'form': loginform, 'invalid':True})
   
@login_required 
def log_out(request):
    if config.DISCOURSE_FLAG:
        config.logout_discourse_user(request.user.username)
    logout(request)
    return HttpResponseRedirect('/')
        
@login_required
def search(request, q):
    handles = User.objects.values_list('username',flat=True).filter(username__contains=q)[:4]
    s = ''
    for handle in handles:
        s = s + '"' + handle + '",'
    if s == '':
        return HttpResponse('[]')
    s = '[' + s[:-1] + ']'
    return HttpResponse(s)

@login_required
def contests(request):
    return render(request, 'contests.html')
    
@login_required
def leaderboard(request):
    
    platform = request.GET.get('platform', 'codechef')
    cusers = Customuser.objects.all()
    if platform == 'spoj':
        cusers = cusers.filter(spojflag = 1).order_by('-spojrating')
        lusers = []
        if cusers:
            rank = 1
            lusers = [(1,cusers[0].user)]
        for i in range(1,len(cusers)):
            if cusers[i].spojrating != cusers[i-1].spojrating:
                rank += 1
            lusers.append((rank, cusers[i].user))
        return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })
    
    if platform == 'codechef':
        codechefchallenge = request.GET.get('codechefchallenge','long')
        
        if codechefchallenge == 'long':
            cusers = cusers.filter(codechefflag = 1, codecheflongrating__gt = 0).order_by('-codecheflongrating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].codecheflongrating != cusers[i-1].codecheflongrating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
            
        if codechefchallenge == 'short':
            cusers = cusers.filter(codechefflag = 1, codechefshortrating__gt = 0).order_by('-codechefshortrating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].codechefshortrating != cusers[i-1].codechefshortrating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
            
        if codechefchallenge == 'ltime':
            cusers = cusers.filter(codechefflag = 1, codechefltimerating__gt = 0).order_by('-codechefltimerating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].codechefltimerating != cusers[i-1].codechefltimerating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
        
        return HttpResponseNotFound(render(request, 'general.html', NOTFOUND_ERROR))
        
    if platform == 'codeforces':
        ratingtype = request.GET.get('ratingtype','current')
        
        if ratingtype == 'current':
            cusers = cusers.filter(codeforcesflag = 1, codeforcesrating__gt = 0).order_by('-codeforcesrating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].codeforcesrating != cusers[i-1].codeforcesrating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
            
        if ratingtype == 'max':
            cusers = cusers.filter(codeforcesflag = 1, codeforcesmaxrating__gt = 0).order_by('-codeforcesmaxrating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].codeforcesmaxrating != cusers[i-1].codeforcesmaxrating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
        
        return HttpResponseNotFound(render(request, 'general.html', NOTFOUND_ERROR))
        
    if platform == 'hackerrank':
        cusers = cusers.filter(hackerrankflag = 1).order_by('-hackerrankrating')
        lusers = []
        if cusers:
            rank = 1
            lusers = [(1,cusers[0].user)]
        for i in range(1,len(cusers)):
            if cusers[i].hackerrankrating != cusers[i-1].hackerrankrating:
                rank += 1
            lusers.append((rank, cusers[i].user))
        return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
    
    if platform == 'geeksforgeeks':
        cusers = cusers.filter(geeksforgeeksflag = 1).order_by('-geeksforgeeksrating')
        lusers = []
        if cusers:
            rank = 1
            lusers = [(1,cusers[0].user)]
        for i in range(1,len(cusers)):
            if cusers[i].geeksforgeeksrating != cusers[i-1].geeksforgeeksrating:
                rank += 1
            lusers.append((rank, cusers[i].user))
        return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
        
    if platform == 'codelabs':
        cusers = cusers.filter(points__gt = 0).order_by('-points')
        lusers = []
        if cusers:
            rank = 1
            lusers = [(1,cusers[0].user)]
        for i in range(1,len(cusers)):
            if cusers[i].hackerrankrating != cusers[i-1].hackerrankrating:
                rank += 1
            lusers.append((rank, cusers[i].user))
        return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
        
    if platform == 'interviewbit':
        cusers = cusers.filter(interviewbitrating__gt = 0).order_by('-interviewbitrating')
        lusers = []
        if cusers:
            rank = 1
            lusers = [(1,cusers[0].user)]
        for i in range(1,len(cusers)):
            if cusers[i].interviewbitrating != cusers[i-1].interviewbitrating:
                rank += 1
            lusers.append((rank, cusers[i].user))
        return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
        
    if platform == 'topcoder':
        ratingtype = request.GET.get('ratingtype','current')
        
        if ratingtype == 'current':
            cusers = cusers.filter(topcoderflag = 1, topcoderrating__gt = 0).order_by('-topcoderrating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].topcoderrating != cusers[i-1].topcoderrating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
            
        if ratingtype == 'max':
            cusers = cusers.filter(topcoderflag = 1, topcodermaxrating__gt = 0).order_by('-topcodermaxrating')
            lusers = []
            if cusers:
                rank = 1
                lusers = [(1,cusers[0].user)]
            for i in range(1,len(cusers)):
                if cusers[i].topcodermaxrating != cusers[i-1].topcodermaxrating:
                    rank += 1
                lusers.append((rank, cusers[i].user))
            return render(request, 'leaderboard.html', {'lusers': lusers, "platform": platform })#, 'fourthyear':fourthyear})
        
        return HttpResponseNotFound(render(request, 'general.html', NOTFOUND_ERROR))
    
    
    return HttpResponseNotFound(render(request, 'general.html', NOTFOUND_ERROR))
    
