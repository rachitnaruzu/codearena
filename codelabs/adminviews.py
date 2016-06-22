from django.shortcuts import render
from .models import Customuser, Setting, Problem, AllowedMail
from django.contrib.auth.models import User, Group, Permission
from .forms import SiteSettingsForm, AdminEditUserForm, Signupform, AddProblemForm, SendMailForm, EditProblemForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import datetime
import json
import codelabs.config as config
from codelabs.webscrape import validproblem
from codelabs.tasks import send_mail_to_many

@login_required
def allowedmails(request):
    if not request.user.has_perm('codelabs.view_allowed'):
        return render(request, 'general.html', config.DENIED)
        
    if request.method == 'GET':
        allowedmails = AllowedMail.objects.all()
        return render(request, 'admin/allowedmails.html', {'allowedmails':allowedmails})
    jsonmaillist = request.POST.get('maillist')
    if jsonmaillist == "" or jsonmaillist == '[]':
        allowedmails = AllowedMail.objects.all()
        return render(request, 'admin/allowedmails.html', {'allowedmails':allowedmails,'error':'empty list', 'jsonmaillist':jsonmaillist})
    if not config.valid_json_mail_list(jsonmaillist):
        allowedmails = AllowedMail.objects.all()
        return render(request, 'admin/allowedmails.html', {'allowedmails':allowedmails,'error':'incorrect format', 'jsonmaillist':jsonmaillist})
    maillist = json.loads(jsonmaillist)
    for mail in maillist:
        if len(AllowedMail.objects.filter(mailid = mail)) == 0:
            allowedmail = AllowedMail(mailid = mail)
            allowedmail.save()
    allowedmails = AllowedMail.objects.all()
    return render(request, 'admin/allowedmails.html',{'allowedmails':allowedmails,'success':True})
        

@login_required
def sendmail(request):
    if not request.user.has_perm('codelabs.send_mail'):
        return render(request, 'general.html', config.DENIED)
        
    if request.method == 'GET':
        sendmailform = SendMailForm()
        return render(request, 'admin/sendmail.html', {'form': sendmailform } )
    sendmailform = SendMailForm(request.POST)
    if not sendmailform.is_valid():
        return render(request, 'admin/sendmail.html', {'form': sendmailform } )
    to = sendmailform.cleaned_data['to']
    subject = sendmailform.cleaned_data['subject']
    content = sendmailform.cleaned_data['content']
    if content == "" or content == "[]":
        return render(request, 'admin/sendmail.html', {'form': sendmailform, 'error':'content is empty' } )
    recipient_list = []
    if to == 'active':
        users = User.objects.filter(is_active = True)
        recipient_list = [user.email for user in users]
    if to == 'custom':
        jsonmaillist = request.POST.get('recipients')
        if not config.valid_json_mail_list(jsonmaillist):
            return render(request, 'admin/sendmail.html', {'form': sendmailform, 'error':'invalid format' } )
        recipient_list = json.loads(jsonmaillist)
    send_mail_to_many.delay(subject, content, recipient_list)
    sendmailform = SendMailForm()
    return render(request, 'admin/sendmail.html', {'form': sendmailform, 'success':True } )
    
    
@login_required
def addproblem(request):
    if not request.user.has_perm('codelabs.add_problem'):
        return render(request, 'general.html', config.DENIED)
        
    if request.method == 'GET':
        addproblemform = AddProblemForm()
        return render(request, 'admin/addproblem.html', {'form': addproblemform } )
    addproblemform = AddProblemForm(request.POST)
    if not addproblemform.is_valid():
        return render(request, 'admin/addproblem.html', {'form': addproblemform } )
    problemcode = addproblemform.cleaned_data['problemcode']
    platform = addproblemform.cleaned_data['platform']
    url = addproblemform.cleaned_data['url']
    points = addproblemform.cleaned_data['points']
    if len(Problem.objects.filter(code = problemcode)) != 0:
        return render(request, 'admin/addproblem.html', {'form': addproblemform, 'present': True } )
    if not validproblem(problemcode, platform, url):
        return render(request, 'admin/addproblem.html', {'form': addproblemform, 'error': True } )
    problem = Problem(code = problemcode, platform = platform, solved = 0, url = url, points = points)
    problem.save()
    return render(request, 'admin/addproblem.html', {'form': addproblemform, 'success': True } )
    
@login_required
def editproblem(request,platform,code):
    if not request.user.has_perm('codelabs.change_problem'):
        return render(request, 'general.html', config.DENIED)
    
    problem = Problem.objects.get(code = code, platform = platform)
    if request.method == 'GET':
        editproblemform = EditProblemForm({ 'points' : problem.points })
        return render(request, 'admin/editproblem.html', {'form': editproblemform, 'problem' : problem } )
    if 'delete' in request.POST:
        problem.delete()
        return HttpResponseRedirect('/allproblems')
    editproblemform = EditProblemForm(request.POST)
    if not editproblemform.is_valid():
        return render(request, 'admin/editproblem.html', {'form': editproblemform, 'problem' : problem } )
    problem.points = editproblemform.cleaned_data['points']
    problem.save()
    return render(request, 'admin/editproblem.html', {'form': editproblemform, 'success': True, 'problem' : problem } )

@login_required
def allusers(request):
    if not request.user.has_perm('codelabs.view_all'):
        return render(request, 'general.html', config.DENIED)
    groups = Group.objects.all()
    context = {'groups' : groups }
    return render(request, 'admin/allusers.html', context)
    
@login_required
def sitesettings(request):
    if not request.user.has_perm('codelabs.change_setting'):
        return render(request, 'general.html', config.DENIED)
    data = {}
    settings = Setting.objects.all()
    for setting in settings:
        data[setting.parameter] = True if setting.value == 1 else False
    if request.method == 'GET':
        sitesettingform = SiteSettingsForm(data)
        return render(request, 'admin/sitesettings.html', {'form': sitesettingform } )
    
    postdata = {}
    for key in data:    postdata[key] = True if key in request.POST else False
    sitesettingform = SiteSettingsForm(postdata,initial =  data)
    if not sitesettingform.has_changed():
        print('not changed')
        return render(request, 'admin/sitesettings.html', {'form': sitesettingform } )
    
    for setting in settings:
        setting.value = 1 if sitesettingform.data[setting.parameter] else 0
        setting.save();
    
    return render(request, 'admin/sitesettings.html', {'form': sitesettingform } )
    
@login_required
def createuser(request):
    if not request.user.has_perm('auth.add_user'):
        return render(request, 'general.html', config.DENIED)
        
    if request.method == 'GET':
        signupform = Signupform()
        return render(request, 'admin/createuser.html', {'form': signupform})
        
    donotmatch = False
    alreadyexist = False
    donotexist = False
    signupform = Signupform(request.POST)
    if signupform.is_valid():
        if AllowedMail.objects.filter(mailid = signupform.cleaned_data['email']).exists():
            if signupform.cleaned_data['password'] == signupform.cleaned_data['confirmpassword']:
                if not User.objects.filter(username=signupform.cleaned_data['handle']).exists():
                    if config.DISCOURSE_FLAG:
                        config.create_discourse_user(
                            name = signupform.cleaned_data['first_name'] + 
                            " " + signupform.cleaned_data['last_name'], 
                            handle = signupform.cleaned_data['handle'], 
                            email = signupform.cleaned_data['email'], 
                            password = signupform.cleaned_data['password']
                        )
                        config.activate_discourse_user(signupform.cleaned_data['handle'])
                    user = User.objects.create(
                        first_name = signupform.cleaned_data['first_name'],
                        last_name = signupform.cleaned_data['last_name'],
                        username = signupform.cleaned_data['handle'],
                        email = signupform.cleaned_data['email'],
                        is_active = True
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
                    signupform = Signupform()
                    return render(request, 'admin/createuser.html', {'form': signupform, 'success':True})
                else:
                    alreadyexist = True
            else:
                donotmatch = True
        else:
            donotexist = True
    
    signupform = Signupform(request.POST)
    return render(request, 'admin/createuser.html', 
            {'form': signupform , 'donotmatch':donotmatch, 'alreadyexist':alreadyexist, 'donotexist':donotexist}
    )
    
@login_required
def adminedituser(request, handle):
    if not request.user.has_perm('auth.change_user'):
        return render(request, 'general.html', config.DENIED)
    
    userarr = User.objects.filter(username=handle)
    if not userarr:
        return HttpResponseNotFound(render(request, 'general.html', config.NOTFOUND_ERROR))
    
    user = userarr[0]
    data = {
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'rollno' : user.customuser.rollno,
            'batch' : config.FIRST_PASS_OUT_BATCH if user.customuser.batch == 0 else user.customuser.batch,
            'branch' : user.customuser.branch,
            'role' : user.groups.all()[0].name,
            'spojhandle' : user.customuser.spojhandle,
            'hackerrankhandle' : user.customuser.hackerrankhandle,
            'codechefhandle' : user.customuser.codechefhandle,
            'geeksforgeekshandle' : user.customuser.geeksforgeekshandle,
            'topcoderhandle' : user.customuser.topcoderhandle,
            'codeforceshandle' : user.customuser.codeforceshandle,
            'interviewbithandle' : user.customuser.interviewbithandle
            }
    spojflag = user.customuser.spojflag
    hackerrankflag = user.customuser.hackerrankflag
    codechefflag = user.customuser.codechefflag
    geeksforgeeksflag = user.customuser.geeksforgeeksflag
    topcoderflag = user.customuser.topcoderflag
    codeforcesflag = user.customuser.codeforcesflag
    interviewbitflag = user.customuser.interviewbitflag
     
    if request.method == 'GET':
        adminedituserform = AdminEditUserForm(data)
        
        return render(request, 'admin/adminedituser.html', {'form': adminedituserform ,'interviewbitflag':interviewbitflag,'codeforcesflag':codeforcesflag, 'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag,'topcoderflag':topcoderflag, 'geeksforgeeksflag':geeksforgeeksflag, 'edituser':user })
    
    if 'delete' in request.POST:
        user.delete()
        if config.DISCOURSE_FLAG:
            delete_discourse_user(handle)
        return HttpResponseRedirect('/admin/allusers')
    
    adminedituserform = AdminEditUserForm(request.POST, initial = data)
    
    if not adminedituserform.is_valid():
        return render(request, 'admin/adminedituser.html', {'form': adminedituserform ,'interviewbitflag':interviewbitflag,'codeforcesflag':codeforcesflag, 'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag,'topcoderflag':topcoderflag, 'geeksforgeeksflag':geeksforgeeksflag, 'edituser':user })
        
    if not adminedituserform.has_changed():
        return render(request, 'admin/adminedituser.html', {'form': adminedituserform ,'interviewbitflag':interviewbitflag,'codeforcesflag':codeforcesflag, 'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag,'topcoderflag':topcoderflag, 'geeksforgeeksflag':geeksforgeeksflag, 'edituser':user })
    
    if adminedituserform.cleaned_data['spojhandle'] != data['spojhandle']:
        spojflag = 2
        
    if adminedituserform.cleaned_data['hackerrankhandle'] != data['hackerrankhandle']:
        hackerrankflag = 2
        
    if adminedituserform.cleaned_data['codechefhandle'] != data['codechefhandle']:
        codechefflag = 2
        
    if adminedituserform.cleaned_data['geeksforgeekshandle'] != data['geeksforgeekshandle']:
        geeksforgeeksflag = 2
        
    if adminedituserform.cleaned_data['topcoderhandle'] != data['topcoderhandle']:
        topcoderflag = 2
        
    if adminedituserform.cleaned_data['codeforceshandle'] != data['codeforceshandle']:
        codeforcesflag = 2
        
    if adminedituserform.cleaned_data['interviewbithandle'] != data['interviewbithandle']:
        interviewbitflag = 2
    
    user.first_name  = adminedituserform.cleaned_data['first_name']
    user.last_name = adminedituserform.cleaned_data['last_name']
    user.customuser.rollno = adminedituserform.cleaned_data['rollno']
    user.customuser.batch = adminedituserform.cleaned_data['batch']
    user.customuser.branch = adminedituserform.cleaned_data['branch']
    
    role = adminedituserform.cleaned_data['role']
    user.groups = [Group.objects.get(name = role)]
    
    user.customuser.spojhandle = adminedituserform.cleaned_data['spojhandle']
    user.customuser.spojflag = spojflag
    user.customuser.hackerrankhandle = adminedituserform.cleaned_data['hackerrankhandle']
    user.customuser.hackerrankflag = hackerrankflag
    user.customuser.codechefhandle = adminedituserform.cleaned_data['codechefhandle']
    user.customuser.codechefflag = codechefflag
    user.customuser.geeksforgeekshandle = adminedituserform.cleaned_data['geeksforgeekshandle']
    user.customuser.geeksforgeeksflag = geeksforgeeksflag
    user.customuser.topcoderhandle = adminedituserform.cleaned_data['topcoderhandle']
    user.customuser.topcoderflag = topcoderflag
    user.customuser.codeforceshandle = adminedituserform.cleaned_data['codeforceshandle']
    user.customuser.codeforcesflag = codeforcesflag
    user.customuser.interviewbithandle = adminedituserform.cleaned_data['interviewbithandle']
    user.customuser.interviewbitflag = interviewbitflag
    user.save()
    user.customuser.save()
    return render(request, 'admin/adminedituser.html', {'form': adminedituserform ,'interviewbitflag':interviewbitflag, 'codeforcesflag':codeforcesflag, 'spojflag':spojflag, 'hackerrankflag':hackerrankflag, 'codechefflag':codechefflag,'topcoderflag':topcoderflag, 'geeksforgeeksflag':geeksforgeeksflag, 'edituser':user })
    
    
