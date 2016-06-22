import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codearena.settings")
django.setup()

from codelabs.models import Setting, Customuser, Dummy, AllowedMail
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

# first user to register will be the admin
first_name = '<first_name>'
last_name = '<last_name>'
handle = '<handle>'
email = '<exampleid@email.com>'
rollno = '<rollno>'
password = '<password>'

student_group = Group.objects.filter(name = 'student_group')
if(len(student_group) != 0): student_group[0].delete()
problem_manager_group = Group.objects.filter(name = 'problem_manager_group')
if(len(problem_manager_group) != 0): problem_manager_group[0].delete()
admin_group = Group.objects.filter(name = 'admin_group')
if(len(admin_group) != 0): admin_group[0].delete()
viewer_group = Group.objects.filter(name = 'viewer_group')
if(len(viewer_group) != 0): viewer_group[0].delete()

view_all = Permission.objects.filter(codename = 'view_all')
if(len(view_all) != 0): view_all[0].delete()
powers = Permission.objects.filter(codename = 'powers')
if(len(powers) != 0): powers[0].delete()
send_mail = Permission.objects.filter(codename = 'send_mail')
if(len(send_mail) != 0): send_mail[0].delete()
view_allowed = Permission.objects.filter(codename = 'view_allowed')
if(len(view_allowed) != 0): view_allowed[0].delete()

signupflag = Setting.objects.filter(parameter = 'signupflag')
if(len(signupflag) != 0): signupflag[0].delete()
profileeditflag = Setting.objects.filter(parameter = 'profileeditflag')
if(len(profileeditflag) != 0): profileeditflag[0].delete()

user = User.objects.filter(username = handle)
if(len(user) != 0):
    user = user[0]
    user.customuser.delete()
    user.delete()
allowedmail = AllowedMail.objects.filter(mailid = email)
if(len(allowedmail) != 0): allowedmail[0].delete()

# creating permissions
add_user = Permission.objects.get(codename = 'add_user')
change_user = Permission.objects.get(codename = 'change_user')
delete_user = Permission.objects.get(codename = 'delete_user')
add_allowedmail = Permission.objects.get(codename = 'add_allowedmail')
change_allowedmail = Permission.objects.get(codename = 'change_allowedmail')
delete_allowedmail= Permission.objects.get(codename = 'delete_allowedmail')
add_problem = Permission.objects.get(codename = 'add_problem')
change_problem = Permission.objects.get(codename = 'change_problem')
delete_problem = Permission.objects.get(codename = 'delete_problem')
change_setting = Permission.objects.get(codename = 'change_setting')
view_all = Permission.objects.create(
    codename='view_all',
    name='can view all',
    content_type=ContentType.objects.get_for_model(Dummy)
)
powers = Permission.objects.create(
    codename='powers',
    name='have some admin powers',
    content_type=ContentType.objects.get_for_model(Dummy)
)
send_mail = Permission.objects.create(
    codename='send_mail',
    name='can send mail',
    content_type=ContentType.objects.get_for_model(Dummy)
)
view_allowed = Permission.objects.create(
    codename='view_allowed',
    name='view allowed mail ids',
    content_type=ContentType.objects.get_for_model(Dummy)
)

# creating groups
student_group = Group.objects.create(name =  'student_group')
problem_manager_group = Group.objects.create(name = 'problem_manager_group')
viewer_group = Group.objects.create(name = 'viewer_group')
admin_group =  Group.objects.create(name = 'admin_group')

admin_group.permissions.add(
    add_user,
    change_user,
    delete_user,
    add_allowedmail,
    change_allowedmail,
    delete_allowedmail,
    add_problem,
    change_problem,
    delete_problem,
    change_setting,
    view_all,
    powers,
    send_mail,
    view_allowed
)  

problem_manager_group.permissions.add(
    add_problem,
    change_problem,
    delete_problem,
    change_setting,
    powers
)

viewer_group.permissions.add(
    view_all,
    powers
)

admin_group.save()
viewer_group.save()
problem_manager_group.save()

Setting.objects.create(parameter = 'signupflag', value = 1)
Setting.objects.create(parameter = 'profileeditflag', value = 1)

user = User.objects.create(
    first_name = first_name,
    last_name = last_name,
    username = handle,
    email = email,
    is_active = True
)
user.set_password(password)
user.groups = [Group.objects.get(name = 'admin_group')]
user.save()
AllowedMail.objects.create(mailid = email)
customuser = Customuser.objects.create(
    user = user,
    rollno = rollno
)
