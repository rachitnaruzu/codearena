CodeArena
=========

CodeArena is an open source platform, which can be used by universities/colleges to assess programming skills of students. As of now its main functionality depends on the webscraping of data from various online coding platforms (codechef, hackerrank, topcoder, interviewbit, geeksforgeeks) and to provide following features:

- A single platform to display rankings of registered students based on their performance on online coding platforms.
- There is also a section of Problem Set where admin can add a problem from above mentioned platforms and codearena will display the list of registered students who have solved that particular problem on the platform from where the problem has been taken. Points can also be alloted to individual problems.
- Option to integrate with a Discourse Community using sso, which enables user to log in into the Discourse by just providing login credentials to codearena only.
- The trial version of this platform is available at [codearena.herokuapp.com](http://codearena.herokuapp.com).
use **guest** as username and **123456** as the password for log in.

Installation
----------------

**Note:** This installation procedure is meant for Ubuntu OS. Replace all the text inclosed with <> with actual values before executing the statements. Better execute the statements line by line rather than copy pasting the whole block. You might have to replace all 'localhost' text with '0.0.0.0' if you are deploying it on digitalocean or on some other online server. This installation assumes that you have alreasy installed python, pip and virtualenv \(sudo pip install virtualenv\).

#### Step 1 : [Installing PostgreSQL database]

We will use PostgreSQL database with codearena. The PostgreSQL installation procedure is taken from [this](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) link:

    sudo apt-get update
	sudo apt-get install postgresql postgresql-contrib
	# switch user to postgres
	sudo su - postgres
    psql
    # execute following sql commands in psql
      CREATE DATABASE codearena;
      CREATE USER codearenauser WITH PASSWORD '<CODEARENA_DATABASE_PASSWORD>';
      ALTER ROLE codearenauser SET client_encoding TO 'utf8';
      ALTER ROLE codearenauser SET default_transaction_isolation TO 'read committed';
      ALTER ROLE codearenauser SET timezone TO 'UTC';
      GRANT ALL PRIVILEGES ON DATABASE codearena TO codearenauser;
      \q
    exit
    
#### Step 2: [Installing broker for celery]
 
 	sudo apt-get install rabbitmq-server
    
#### Step 3: [Setting up codearena platform]

    cd /var
    sudo git clone https://github.com/rachitnaruzu/codearena.git
    
open /var/codearena/codelabs/config.py:
  
    sudo vim /var/codearena/codelabs/config.py
    
set the following variables:
 
    FIRST_PASS_OUT_BATCH = <FIRST_PASS_OUT_BATCH> # ex: 2005
    CODEARENA_MAIL_ID = "<CODEARENA_MAIL_ID>" # ex: 'noreply@codearena.example.com'
    CODEARENA_DOMAIN = "<CODEARENA_DOMAIN>" # ex: 'codearena.example.com'

open /var/codearena/codearena/settings.py:

	sudo vim /var/codearena/codearena/settings.py

set the following variables:
    
	SECRET_KEY = '<SECRET_KEY>' # used by django for security reasons
    
    # might have to replace local host with 127.0.0.1 or 0.0.0.0
    BROKER_URL = 'amqp://guest@localhost//' 
    
    # codearena requires email smtp server for verifying accounts.
    
    EMAIL_HOST = '<EMAIL_HOST>'
    EMAIL_PORT = <PORT_NUMBER>
    EMAIL_HOST_USER = '<EMAIL_HOST_USER>'
    EMAIL_HOST_PASSWORD = '<EMAIL_HOST_PASSWORD>'
    
    ALLOWED_HOSTS = ['<CODEARENA_DOMAIN>']
    
    # look for Databses variable below in the file
	DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'codearena',
            'USER': 'codearenauser',
            'PASSWORD': '<CODEARENA_DATABASE_PASSWORD>',
            'HOST': 'localhost', # or 127.0.0.1 or 0.0.0.0
            'PORT': '<POSTGRESQL_PORT>' # 5432 generally
        }
    }
    
open /var/codearena/seed.py:

	sudo vim /var/codearena/seed.py
    
set the following variables:

	# following user will be the admin
    first_name = '<first_name>'
    last_name = '<last_name>'
    handle = '<handle>'
    email = '<exampleid@email.com>'
    rollno = '<rollno>'
    password = '<password>'

In terminal:

    sudo apt-get install libpq-dev python-dev python3-dev libjpeg-dev libjpeg8-dev 
    sudo -i
    cd /var/codearena
    # create virtualenv with python3
    virtualenv venv -p python3
    # activate the virtualenv
    source venv/bin/activate
    pip install --upgrade pip 
    pip install -r requirements.txt
    python manage.py collectstatic --noinput
    python manage.py makemigrations
    python manage.py migrate
    python seed.py
    # deactivate virtualenv
    deactivate
    exit
    
open /var/codearena/codearena_nginx.conf:
    
    sudo vim /var/codearena/codearena_nginx.conf
    
set the following variables:

	server_name <CODEARENA_DOMAIN>; # without quotes
	
#### Step 4: [Setting up nginx]

    sudo apt-get install nginx
    
copy the files to specific locations:

    sudo cp /var/codearena/codearena_nginx.conf /etc/nginx/sites-enabled
    sudo cp /var/codearena/codearena_uwsgi.conf /etc/init

#### Step 5: [Initialize Servers]    

initialize directories:

    sudo mkdir /var/codearena/venv/var
    sudo mkdir /var/codearena/venv/var/run
    sudo mkdir /var/codearena/venv/var/log
    sudo mkdir /var/codearena/venv/var/run/celery
    sudo mkdir /var/codearena/venv/var/log/celery
    sudo mkdir /var/codearena/venv/var/log/uwsgi

initialize nginx:
    
    # you may have to stop apache2 if it is installed and running
    sudo service apache2 stop # (optional)
    sudo service nginx restart
    
initialize uwsgi:
    
    sudo /var/codearena/venv/bin/uwsgi --ini /var/codearena/codearena_uwsgi.ini
    
initialize celery:

    sudo /var/codearena/venv/bin/celery multi start worker1 --workdir=/var/codearena --pidfile=/var/codearena/venv/var/run/celery/%N.log --logfile=/var/codearena/venv/var/log/celery/%N.log --loglevel=INFO --app=codearena --time-limit=300 --concurrency=8
    
initialize webscraping job:

    sudo cp /var/codearena/codearena_webscrape /etc/cron.daily
    sudo chmod +x /etc/cron.daily/codearena_webscrape
    sudo /etc/cron.daily/codearena_webscrape
    
Phew !! All done, now go to \<CODEARENA_DOMAIN\> and login using admin credentials.

#### Step 6

Go to Admin -> Allowed Mail and add all the mailid that should be allowed to register using signup. add mailids in json format => ["user1@examplemail.com", "use2@examplemail.com", .....]

#### Step 7: [Restart Server]

if you restart your os, you may have to rerun the servers:
    
    sudo service apache2 stop # (optional)
    sudo service nginx restart
    sudo /var/codearena/venv/bin/uwsgi --ini /var/codearena/codearena_uwsgi.ini
    sudo /var/codearena/venv/bin/celery multi start worker1 --workdir=/var/codearena --pidfile=/var/codearena/venv/var/run/celery/%N.log --logfile=/var/codearena/venv/var/log/celery/%N.log --loglevel=INFO --app=codearena --time-limit=300 --concurrency=8

### Setting Up Discourse (Optional)

#### Step 1: [Install Discourse on same server as of CodeArena]
\# skip this step if you have already installed Discourse on another server. 

Install discourse from [this](https://github.com/discourse/discourse/blob/master/docs/INSTALL-cloud.md) link. Use same EMAIL_SMTP_HOST values as that of codearena, when asked during the installation.

open /var/codearena/discourse_app.yml:

    sudo vim /var/codearena/discourse_app.yml

set the following variables (copy them from /var/discourse/app.yml):

    DISCOURSE_DEVELOPER_EMAILS: '<ADMIN_MAIL_ID>'
    DISCOURSE_SMTP_ADDRESS: <EMAIL_HOST> # you may set it same as that in /var/codearena/codearena/settings.py
    DISCOURSE_SMTP_USER_NAME: '<EMAIL_HOST_USER>'
    DISCOURSE_SMTP_PASSWORD: '<EMAIL_HOST_PASSWORD>'
    LETSENCRYPT_ACCOUNT_EMAIL: '<ADMIN_MAIL_ID>'

In terminal:

    sudo /var/discourse/launcher stop app || true
    sudo rm /var/discourse/app.yml
    sudo cp /var/codearena/discourse_app.yml /var/discourse/app.yml
    sudo service nginx reload
    sudo /var/discourse/launcher rebuild app
    
Above procedure is taken from [this](https://meta.discourse.org/t/running-other-websites-on-the-same-machine-as-discourse/17247) link.

#### Step 2: [Setting up Discourse SSO]

Assuming that Discourse has been setup correctly, create admin user in discourse with same 
handle as that of codearena admin, then log in to discourse.Go to USERS -> click on the admin user -> click 'Generate' button. This will generate \<DISCOURSE_API_KEY\>.Go to settings and set the followin variables 
(you can search for them in the discourse search bar):
    
    notification_email : <CODEARENA_MAIL_ID>
    check invite only
    check login required
    uncheck enable local logins
    uncheck allow new registrations
    uncheck enable signup cta
    check enable sso
    enable verbose sso login
    sso url : <CODEARENA_DOMAiN>/discourse/login # add http or https as per your domain
    sso secret : <DISCOURSE_SSO_SECRET> # can be kept same as <SECRET_KEY>
    check sso overrides email
    check sso overrides username
    check sso overrides name
    check sso overrides avatar
    logout redirect : <CODEARENA_DOMAiN>/logout # add http or https as per your domain
    uncheck automatically download gravatars
    uncheck allow uploaded avatars
    uncheck external system avatars enabled
    
open /var/codearena/codelabs/config.py:

    sudo vim /var/codearena/codelabs/config.py
    
set the following variables:
    
    # Discourse Settings
    DISCOURSE_FLAG = True # set it to True to enable discourse linking through sso

    # No need to set below discourse variables if DISCOURSE_FLAG is set to False
    DISCOURSE_API_KEY = '<DISCOURSE_API_KEY>'
    DISCOURSE_ADMIN = '<DISCOURSE_ADMIN>' # handle of the admin user
    DISCOURSE_URL = '<DISCOURSE_URL>' # forums.example.com
    DISCOURSE_SSO_SECRET = '<DISCOURSE_SSO_SECRET>'
    
stop the running uwsgi process:

    sudo ps ax | grep uwsgi 
    # kill all the processes with PIDs given by above statement.
    sudo kill -9 <PID>
    sudo /var/codearena/venv/bin/uwsgi --ini /var/codearena/codearena_uwsgi.ini
    

License
-------

Released under the [MIT License](http://opensource.org/licenses/MIT).

