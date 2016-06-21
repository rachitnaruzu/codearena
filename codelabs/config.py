from .pydiscourse.client import DiscourseClient
from django.core.mail import send_mail
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from random import randint
import requests as rq

# Discourse Settings
DISCOURSE_FLAG = False # set it to True to enable discourse linking through sso

# No need to set below discourse variables if DISCOURSE_FLAG is set to False
DISCOURSE_API_KEY = '<DISCOURSE_API_KEY>'
DISCOURSE_ADMIN = '<DISCOURSE_ADMIN>'
DISCOURSE_URL = '<DISCOURSE_URL>'
DISCOURSE_SSO_SECRET = '<DISCOURSE_SSO_SECRET>'

FIRST_PASS_OUT_BATCH = <FIRST_PASS_OUT_BATCH>
CODEARENA_MAIL_ID = "<CODEARENA_MAIL_ID>"
CODEARENA_DOMAIN = "<CODEARENA_DOMAIN>"

NOTFOUND_ERROR = {'title':'404 Error', 'content':'Page not Found'}
DENIED = {'title':'Denied', 'content':'You do not have permission to access this page.'}
ACTIVATION_SUCCEEDED = {'title':'Activation', 'content':'Activation Succeded. You may log in now.'}
ACTIVATION_FAILED = {'title':'Activation', 'content':'Activation Failed. Contact Admin.'}
PASSCHANGE_SUCCESS = {'title':'Change Password', 'content':'Password has been changed successfully.'}

def validateEmail(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True

def valid_json_mail_list(jsonmaillist):
    try:
        json_object = json.loads(jsonmaillist)
        if isinstance(json_object, list):
            for mail in json_object:
                if not validateEmail(mail):
                    return False
        else:
            return False
    except ValueError:
        return False
    return True

def forgotpass_info(mailid):
    content = "A change password mail has been send to you at " + mailid  +  ". Please click the link in the mail to change you password."
    return {'title':'Forgot Password', 'content':content}
    
def activation_info(mailid):
    content = "An activation mail has been send to you at " + mailid  +  ". Please click the link in the mail to activate your account."
    return {'title':'Activation', 'content':content}
    
def create_discourse_user(name,handle,email,password):
    dclient = DiscourseClient(DISCOURSE_URL, api_username=DISCOURSE_ADMIN, api_key=DISCOURSE_API_KEY)
    dclient.create_user(name,handle,email,password)
    
def activate_discourse_user(handle):
    dclient = DiscourseClient(DISCOURSE_URL, api_username=DISCOURSE_ADMIN, api_key=DISCOURSE_API_KEY)
    duser = dclient.getUserByUsername(handle)
    did = duser['user']['id']
    dclient.activateUserById(did)
    
def logout_discourse_user(handle):
    dclient = DiscourseClient(DISCOURSE_URL, api_username=DISCOURSE_ADMIN, api_key=DISCOURSE_API_KEY)
    duser = dclient.getUserByUsername(handle)
    did = duser['user']['id']
    dclient.logout(did)
    
def delete_discourse_user(handle):
    dclient = DiscourseClient(DISCOURSE_URL, api_username=DISCOURSE_ADMIN, api_key=DISCOURSE_API_KEY)
    dclient.delete_user(userid = handle)
    
def generate_key():
    l = 12
    key = ""
    for i in range(0, l):
        choice = randint(0, 2)
        if choice == 0: key +=  chr(randint(ord('0'), ord('9')))
        if choice == 1: key +=  chr(randint(ord('a'), ord('z')))
        if choice == 2: key +=  chr(randint(ord('A'), ord('Z')))
    return key
    
def generate_activation_key():
    return generate_key()

def send_change_password_mail(passwordkey, toid, handle):
    subject = "Change Password"
    link = CODEARENA_DOMAIN + "/changepassword/?passwordkey=" + passwordkey
    content = (
            "Hello " + handle + ",<br>" 
            " Click on <a href=\"" + link + "\" target=\"_blank\">this link</a> to change your password. <br>"
            "<br>"
            "<br>"
            "<br>"
            " Regards " + CODEARENA_DOMAIN
        )
    send_mail(subject, content, CODEARENA_MAIL_ID, [toid])
    
def send_activation_mail(handle, toid, activatekey):
    subject = "Activation Mail"
    link = CODEARENA_DOMAIN + "/activate/?activatekey=" + activatekey
    content = ( 
                "Hello " + handle + ",<br>" 
                " Click on <a href=\"" + link + "\" target=\"_blank\">this link</a> link to activate your account. <br>"
                "<br>"
                "<br>"
                "<br>"
                " Regards " + CODEARENA_DOMAIN
            )
    send_mail(subject, content, CODEARENA_MAIL_ID, [toid])
