from django import forms
from django.core.validators import RegexValidator
from datetime import date
from codelabs.config import FIRST_PASS_OUT_BATCH

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'email'}
                )
            )

class ChangePasswordForm(forms.Form):
    newpassword = forms.CharField(
                    widget=forms.PasswordInput(
                        attrs={'class':'form-control','placeholder':'password'}
                    ),
                    min_length=6,
                    max_length=30,
                    validators=[
                        RegexValidator(
                                regex='^[a-zA-Z_.0-9]+$',
                                message='password may contain letters or numbers' +
                                        'or _ or .',
                                code='invalid_password'
                            )
                    ]
                )
    confirmnewpassword = forms.CharField(
                    widget=forms.PasswordInput(
                        attrs={'class':'form-control','placeholder':'confirmpassword'}
                    ),
                    min_length=6,
                    max_length=30,
                    validators=[
                        RegexValidator(
                                regex='^[a-zA-Z_.0-9]+$',
                                message='password may contain letters or numbers' +
                                        'or _ or .',
                                code='invalid_confirmpassword'
                            )
                    ]
                )

class SendMailForm(forms.Form):
    to = forms.ChoiceField(
                required = True,
                choices = [('active', 'Active'), ('custom', 'Custom')],
                widget = forms.RadioSelect(
                        attrs = {'class':'radio-custom'}
                    )
            )
    recipients = forms.CharField(
                required = False,
                widget = forms.Textarea(
                    attrs={'class':'form-control','placeholder':'list of mail ids in form: [\'mail id\',....]','rows':'5'}
                )
            )
    subject = forms.CharField(
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'subject'}
                )
            )
    content = forms.CharField(
                widget = forms.Textarea(
                    attrs={'class':'form-control','placeholder':'content of mail','rows':'8'}
                )
            )

class EditProblemForm(forms.Form):
    points = forms.IntegerField(
                                min_value = 0, 
                                max_value = 100,
                                widget = forms.NumberInput(
                                attrs={'class':'form-control'}
                            )
                        )

class AddProblemForm(forms.Form):
    problemcode = forms.CharField(
                min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'problem code'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z][A-Za-z-_.0-9]*$',
                        message='problem code must start with a letter and ' + 
                                'may contain letters or _ or .',
                        code='invalid_problemcode'
                    )
                ]
            )
    url = forms.CharField(
                min_length=1,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'problem url'}
                ),
                validators=[
                    RegexValidator(
                        regex='http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                        message='problem code must be a valid url',
                        code='invalid_url'
                    )
                ]
            )
    platform = forms.ChoiceField(
                choices = [('codechef', 'codechef'), ('spoj', 'spoj'), ('hackerrank', 'hackerrank'), ('geeksforgeeks','geeksforgeeks')],
                widget = forms.Select(
                    attrs={'class':'form-control'}
                )
            )
    points = forms.IntegerField(
                                min_value = 0, 
                                max_value = 100,
                                widget = forms.NumberInput(
                                attrs={'class':'form-control'}
                            )
                        )

class Loginform(forms.Form):
    handle = forms.CharField(
                min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'handle'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-z][a-z_.0-9]*$',
                        message='handle must start with a letter and ' + 
                                'may contain letters or _ or .',
                        code='invalid_handle'
                    )
                ]
            )
    password = forms.CharField(
                    widget=forms.PasswordInput(
                        attrs={'class':'form-control','placeholder':'password'}
                    ),
                    min_length=6,
                    max_length=30,
                    validators=[
                        RegexValidator(
                                regex='^[a-zA-Z_.0-9]+$',
                                message='password may contain letters or numbers' +
                                        'or _ or .',
                                code='invalid_password'
                            )
                    ]
                )

class Editform(forms.Form):
    #global batch_choices
    
    first_name = forms.CharField(
                min_length=3,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'first_name'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z]+$',
                        message='first_name must be Alphabetic',
                        code='invalid_first_name'
                    )
                ]
            )
    last_name = forms.CharField(
                required=False,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'last_name'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z]+$',
                        message='last_name must be Alphabetic',
                        code='invalid_last_name'
                    )
                ]
            )
    rollno = forms.CharField(
                min_length=3,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'rollno'}
                )
            )
            
    batch = forms.ChoiceField(
                label = 'Batch(passing year)',
                choices = reversed([(y, y) for y in range(FIRST_PASS_OUT_BATCH, date.today().year + 5 )]),
                widget = forms.Select(
                        attrs = {'class':'form-control'}
                    )
                )
    
    branch = forms.ChoiceField(
                choices = [('CSE', 'CSE'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('MCA', 'MCA'), ('IMCA', 'IMCA')],
                widget = forms.Select(
                    attrs={'class':'form-control'}
                )
            )
    picflag = forms.BooleanField(
                label = 'pic',
                required = False,
                widget = forms.CheckboxInput (
                    attrs={'class':'cmn-toggle cmn-toggle-round'}
                ))
    pic = forms.ImageField(required = False)
    
    
    def clean_pic(self):
        pic = self.cleaned_data.get('pic',False)
        if pic:
            if pic._size > 400 * 1024:
                raise forms.ValidationError("Image file too large ( > 400KB )")
            return pic
        
    spojhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'spojhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='spojhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_spojhandle'
                            )
                    ]
            )
            
    hackerrankhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'hackerrankhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='hackerrankhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_hackerrankhandle'
                            )
                    ]
            )
    codechefhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'codechefhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='codechefhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_codechefhandle'
                            )
                    ]
            )
    geeksforgeekshandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'geeksforgeekshandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9%]*$',
                                message='geeksforgeekshandle must start with a letter and ' + 
                                        'may contain letters or _ or . or %',
                                code='invalid_geeksforgeekshandle'
                            )
                    ]
            )
    topcoderhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'topcoderhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='topcoderhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_topcoderhandle'
                            )
                    ]
            )
    codeforceshandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'codeforceshandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='codeforceshandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_codeforceshandle'
                            )
                    ]
            )
    interviewbithandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'interviewbithandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='interviewbithandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_interviewbithandle'
                            )
                    ]
            )

class Signupform(forms.Form):
    first_name = forms.CharField(
                min_length=3,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'first_name'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z]+$',
                        message='first_name must be Alphabetic',
                        code='invalid_first_name'
                    )
                ]
            )
    last_name = forms.CharField(
                required=False,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'last_name'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z]+$',
                        message='last_name must be Alphabetic',
                        code='invalid_last_name'
                    )
                ]
            )
    handle = forms.CharField(
                min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'handle'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-z][a-z_.0-9]*$',
                        message='handle must start with a letter and ' + 
                                'may contain letters or _ or .',
                        code='invalid_handle'
                    )
                ]
            )
    rollno = forms.CharField(
                min_length=3,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'rollno'}
                )
            )
            
    batch = forms.ChoiceField(
                label = 'Batch (passing year)',
                choices = reversed([(y, y) for y in range(FIRST_PASS_OUT_BATCH, date.today().year + 5 )]),
                widget = forms.Select(
                        attrs = {'class':'form-control'}
                    )
                )
    branch = forms.ChoiceField(
                choices = [('CSE', 'CSE'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('MCA', 'MCA'), ('IMCA', 'IMCA')],
                widget = forms.Select(
                    attrs={'class':'form-control'}
                )
            )
    email = forms.EmailField(
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'email'}
                )
            )
    password = forms.CharField(
                    widget=forms.PasswordInput(
                        attrs={'class':'form-control','placeholder':'password'}
                    ),
                    min_length=6,
                    max_length=30,
                    validators=[
                        RegexValidator(
                                regex='^[a-zA-Z_.0-9]+$',
                                message='password may contain letters or numbers' +
                                        'or _ or .',
                                code='invalid_password'
                            )
                    ]
                )
    confirmpassword = forms.CharField(
                    label = 'Confirm Password',
                    widget=forms.PasswordInput(
                        attrs={'class':'form-control','placeholder':'confirmpassword'}
                    ),
                    min_length=6,
                    max_length=30,
                    validators=[
                        RegexValidator(
                                regex='^[a-zA-Z_.0-9]+$',
                                message='password may contain letters or numbers' +
                                        'or _ or .',
                                code='invalid_confirmpassword'
                            )
                    ]
                )
                
class SiteSettingsForm(forms.Form):
    signupflag = forms.BooleanField(
                label = 'SignUp',
                required = False,
                widget = forms.CheckboxInput (
                    attrs={'class':'cmn-toggle cmn-toggle-round'}
                ))
    profileeditflag = forms.BooleanField(
                label = 'ProfileEdit',
                required = False,
                widget = forms.CheckboxInput (
                    attrs={'class':'cmn-toggle cmn-toggle-round'}
                ))
                
class AdminEditUserForm(forms.Form):
    first_name = forms.CharField(
                min_length=3,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'first_name'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z]+$',
                        message='first_name must be Alphabetic',
                        code='invalid_first_name'
                    )
                ]
            )
    last_name = forms.CharField(
                required=False,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'last_name'}
                ),
                validators=[
                    RegexValidator(
                        regex='^[a-zA-Z]+$',
                        message='last_name must be Alphabetic',
                        code='invalid_last_name'
                    )
                ]
            )
    rollno = forms.CharField(
                min_length=3,
                max_length=254,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'rollno'}
                )
            )
            
    batch = forms.ChoiceField(
                label = 'Batch(passing year)',
                choices = reversed([(y, y) for y in range(FIRST_PASS_OUT_BATCH, date.today().year + 5 )]),
                widget = forms.Select(
                        attrs = {'class':'form-control'}
                    )
                )
    
    branch = forms.ChoiceField(
                choices = [('CSE', 'CSE'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('MCA', 'MCA'), ('IMCA', 'IMCA')],
                widget = forms.Select(
                    attrs={'class':'form-control'}
                )
            )
            
    role = forms.ChoiceField(
                choices = [('student_group', 'Student'), ('admin_group', 'Admin'), ('problem_manager_group', 'Problem Manager'), ('viewer_group', 'Viewer')],
                widget = forms.Select(
                    attrs={'class':'form-control'}
                )
            )
    spojhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'spojhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='spojhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_spojhandle'
                            )
                    ]
            )
            
    hackerrankhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'hackerrankhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='hackerrankhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_hackerrankhandle'
                            )
                    ]
            )
    codechefhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'codechefhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='codechefhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_codechefhandle'
                            )
                    ]
            )
    geeksforgeekshandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'geeksforgeekshandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9%]*$',
                                message='geeksforgeekshandle must start with a letter and ' + 
                                        'may contain letters or _ or . or %',
                                code='invalid_geeksforgeekshandle'
                            )
                    ]
            )
    topcoderhandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'topcoderhandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='topcoderhandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_topcoderhandle'
                            )
                    ]
            )
    codeforceshandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'codeforceshandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='codeforceshandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_codeforceshandle'
                            )
                    ]
            )
    interviewbithandle = forms.CharField(
                required=False,
                #min_length=3,
                max_length=30,
                widget = forms.TextInput(
                    attrs={'class':'form-control','placeholder':'interviewbithandle'}
                ),
                validators=[
                        RegexValidator(
                                regex='^[A-Za-z][A-Za-z_.0-9]*$',
                                message='interviewbithandle must start with a letter and ' + 
                                        'may contain letters or _ or .',
                                code='invalid_interviewbithandle'
                            )
                    ]
            )
