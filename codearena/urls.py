from django.conf.urls import url, include
from django.contrib import admin
from . import views
from codelabs import views as codelabsviews, adminviews
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^denied/$', views.denied, name='denied'),
    url(r'^search/(?P<q>[a-z0-9_]+)', codelabsviews.search),
    url(r'^users/(?P<handle>[a-z0-9_]+)/$', codelabsviews.profile, name='users'),
    url(r'^edit/$', codelabsviews.edit, name='edit'),
    url(r'^login/$', codelabsviews.log_in, name='login'),
    url(r'^logout/$', codelabsviews.log_out, name='logout'),
    url(r'^signup/$', codelabsviews.signup, name='signup'),
    url(r'^allproblems/', codelabsviews.allproblems , name='allproblems'),
    url(r'^leaderboard/', codelabsviews.leaderboard , name='leaderboard'),
    url(r'^problems/(?P<platform>[a-zA-Z0-9-]+)/(?P<code>[a-zA-Z0-9-]+)/', codelabsviews.problem, name='problems'),
    url(r'^activate/', codelabsviews.activate, name='activate'),
    url(r'^profilepic/(?P<handle>[a-z0-9_]+)$', codelabsviews.profile_pic, name='profilepic'),
    url(r'^changepassword/$', codelabsviews.change_password, name='changepassword'),
    url(r'^forgot/$', codelabsviews.forgot_password, name='forgot'),
    url(r'^discourse/login$', codelabsviews.discourse_login, name='discourselogin'),
    
    url(r'^admin/allowedmails/', adminviews.allowedmails, name='allowedmails'),
    url(r'^admin/sendmail/', adminviews.sendmail, name='sendmail'),
    url(r'^admin/addproblem/', adminviews.addproblem, name='addproblem'),
    url(r'^admin/editproblem/(?P<platform>[a-zA-Z0-9-]+)/(?P<code>[a-zA-Z0-9-]+)/', adminviews.editproblem, name='editproblem'),
    url(r'^admin/allusers/', adminviews.allusers, name='allusers'),
    url(r'^admin/createuser/', adminviews.createuser, name='createuser'),
    url(r'^admin/sitesettings/', adminviews.sitesettings, name='sitesettings'),
    url(r'^admin/adminedituser/(?P<handle>[a-z0-9_]+)/$', adminviews.adminedituser, name='adminedituser')
]
