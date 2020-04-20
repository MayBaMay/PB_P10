# PUR BEURRE - OPENCLASSROOMS PYTHON - PROJECT #10
This open source project was created for the OpenClassRooms' Python developer course (Project 10/13)).
Its purpose is to deploy an application on a distant server, in this case Digital Ocean, using a Nginx web server, gunicorn and supervisor.

We used the Purbeurre application deployed on Heroku for the [projet #8](https://github.com/MayBaMay/PB_P8) of this course. It is a DJANGO application integrating a back-end part based on Python 3.7 and a front-end part developed with HTML5, CSS3 and JavaScript using Bootsrap.

Ask the application a product name, select one of the products to confirm your choice and it will give you a list of similar products with a better nutriscore.
When registered, the user can save those favorite subsitutes.

Fork the project on you github account.

## Deployment

### IaaS Digital Ocean
Configuration :<br/>
  -	Image : Ubuntu 18.04.3(LTS)
  -	Plan : Standard - $5/mois
  -	Datacenter region : le plus proche de vous
  -	SSH Keys :
  ```
  $ cd /Users/username/.ssh/
  $ cat id_rsa.pub
  ```
  -	How many droplets : 1
  -	Choose Hostname : bonapp
Fire-Wall :<br/>
Name : OCP-Firewall<br/>
Configuration Inbound Rules :
-	SSH TCP 22
-	http TCP 80
Droplets : bonapp<br/>

### SSH connexion
Get the app's IP adress from Digital Ocean
```
$ ssh root@<your ip adress>
Are you sure you want to continue connecting (yes/no)? yes
Création d’un nouvel utilisateur :
root@bonapp:~# adduser <username>
Enter new UNIX password: <your password>
Retype new UNIX password: <your password>
passwd: password updated successfully
Changing the user information for <username>
Enter the new value, or press ENTER for the default
```

Add user to the super-user group (sudo)
```
root@bonapp:~# gpasswd -a  <username> sudo
root@bonapp:~# su - <username>
```
You are now connected as the new user<br/>

Create a .ssh directory and change permissions
```
<username>@bonapp:~$ mkdir .ssh  
<username>@bonapp:~$ chmod 700 .ssh
```
Create a new file for your public key, change autorisations and disconnect your user
```
<username>@bonapp:~$ vi .ssh/authorized_keys
```
Paste all your ssh key in it
```
<username>@bonapp:~$ chmod 600 .ssh/authorized_keys
<username>@bonapp:~$ exit
```
Delete all connexion autorisation from root
```
root@bonapp~$ vi /etc/ssh/sshd_config
```
Change `PermitRootLogin` to `no`
Then recharge program:
```
root@bonapp~$ service ssh reload
```
Test your ssh connexion in a new terminal window
```
$ ssh <username>@<your ip adress>
```

### Load application on server
Install librairies
```
<username>@bonapp:~$ sudo apt-get update
[sudo] password for pb: <your password>
<username>@bonapp:~$ sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib
```
Clone the application from git
```
<username>@bonapp:~$ git clone https://github.com/MayBaMay/PB_P10.git
```
Create a virtual environnment and load dependencies
```
<username>@bonapp:~$ sudo apt install virtualenv
<username>@bonapp:~$ virtualenv env -p python3
<username>@bonapp:~$ source env/bin/activate
(env) <username>@bonapp:~$ pip install -r PB_P10/requirements.txt
```

### Add production variables
```
env) <username>@bonapp:~$ touch PB_P10/pur_beurre_project/settings/.env
(env) <username>@bonapp:~$ vi PB_P10/pur_beurre_project/settings/.env

SECRET_KEY = <your secret_key>
DB_NAME = 'purbeurre'
DB_USER = '<username>'
DB_HOST = ''
DB_PORT = '5432'
DB_PASSWORD = '<your password>'
IP = '<your ip adress>'
```
### Création de la base et migration des données
```
(env) <username>@bonapp:~$ sudo -u postgres psql
psql (12.2 (Ubuntu 10.12-0ubuntu0.18.04.1))
Type "help" for help.

postgres=# CREATE DATABASE purbeurre;
postgres=#  CREATE USER <username> WITH PASSWORD '<your password>';
postgres=#  ALTER ROLE <username> SET client_encoding TO 'utf8';
postgres=# ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';
postgres=#  ALTER ROLE <username> SET timezone TO 'Europe/Paris';
postgres=#  GRANT ALL PRIVILEGES ON DATABASE purbeurre TO <username>;
postgres=#  \q
```
Generate static files
```
(env) <username>@bonapp:~$ export ENV=PRODUCTION
(env) <username>@bonapp:~$ ./PB_P10/manage.py collectstatic
```
Launch maigrations
```
(env) <username>@bonapp:~$ ./PB_P10/manage.py migrate
```
Create a super user
```
(env) <username>@bonapp:~$ ./PB_P10/manage.py createsuperuser
```

Load json dumps
```
(env) <username>@bonapp:~$ python PB_P10/manage.py loaddata foodSearch/dumps/foodSearch.json
```

### Création du serveur Nginx

```
(env) <username>@bonapp:~$ sudo apt-get install nginx
(env) <username>@bonapp:~$ sudo touch /etc/nginx/sites-available/purbeurre
(env) <username>@bonapp:~$ sudo ln -s /etc/nginx/sites-available/purbeurre /etc/nginx/sites-enabled
(env) <username>@bonapp:~$ sudo vi /etc/nginx/sites-available/purbeurre

server {

    listen 80; server_name <your ip adress>;
    root /home/<username>/PB_P10/;

    location /static {
        alias /home/<username>/PB_P10/pur_beurre_project/staticfiles/;
    }

     location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
        if (!-f $request_filename) {
            proxy_pass http://127.0.0.1:8000;
            break;
        }
    }
}
```
Reload Nginx configuration
```
(env) <username>@bonapp:~$ sudo service nginx reload
```

### Gunicorn and Supervisor installation and configuration

```
(env) <username>@bonapp:~$ sudo apt-get install supervisor
(env) <username>@bonapp:~$ cd PB_P10
(env) <username>@bonapp:~/PB_P10$ gunicorn pur_beurre_project.wsgi:application
(env) <username>@bonapp:~/PB_P10$ sudo vi /etc/supervisor/conf.d/purbeurre-gunicorn.conf

[program:purbeurre-gunicorn]
command = /home/<username>/env/bin/gunicorn pur_beurre_project.wsgi:application
user = <username>
directory = /home/<username>/PB_P10
autostart = true
autorestart = true
environment = DJANGO_SETTINGS_MODULE='pur_beurre_project.settings.production'
(env) <username>@bonapp:~$  sudo supervisorctl reread
purbeurre -gunicorn: available
(env) <username>@bonapp:~$  sudo supervisorctl update
purbeurre -gunicorn: added process group
(env) <username>@bonapp:~$  sudo supervisorctl status
```

## Updates

### Database
In case of models modifications :
```
(env) <username>@bonapp:~$ python PB_P10/manage.py makemigrations
(env) <username>@bonapp:~$ python PB_P10/manage.py migrate
```

Automatic Cron task for updating database can be added :
```
(env) <username>@bonapp:~$ crontab -e

# m h  dom mon dow   command
00 00    * * 0    /home/<username>/update_db.sh

(env) <username>@bonapp:~$ vi update_db.sh
#!/bin/bash
echo --- crontab-began $(date) --- >> /tmp/update_db.log
source env/bin/activate
python ~/PB_P10/manage.py fill_db -f >> /tmp/update_db.log
deactivate
echo crontab-ends $(date) >> /tmp/update_db.log
exit

(env) <username>@bonapp:~$ chmod +x update_db.sh
```

### Nginx
In case of Nginx configurations modifications :
```
(env) <username>@bonapp:/etc/nginx$ sudo service nginx reload
```

### supervisor
In case of Supervisor configurations modifications :
```
(env) <username>@bonapp:~$  sudo supervisorctl restart purbeurre-gunicorn
(env) <username>@bonapp:~$  sudo supervisorctl reread
purbeurre -gunicorn: available
(env) <username>@bonapp:~$  sudo supervisorctl update
purbeurre -gunicorn: added process group
Puis vérifiez que le processus a bien été ajouté en tapant la commande status :
(env) <username>@bonapp:~$  sudo supervisorctl status
```

## Monitoring

### Errors monitoring with Sentry
Be alerted for each errors occured on your application with Sentry<br/>
Create an account https://sentry.io/signup/ and a new Django project <br/>
Then install th sentry-sdk librairy :
```
(env) <username>@bonapp:~$  pip install --upgrade 'sentry-sdk==0.14.3'
```
Modify in your dev environnment the dsn address in the production.py module
```
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="<your dsn address>",
    integrations=[DjangoIntegration()],
)
```
Commit the changes, push on Github and come back to your server
```
(env) <username>@bonapp:~$  cd  PB_P10
(env) <username>@bonapp:~/PB_P10$  git pull origin master
```
Your app will now be on the surveillance of Sentry

### System monitoring on Newrelic
Create an account Newrelic and create a new host in NewRelic Infrastructure<br/>
Choose platform Linux and installer apt and follow the given instructions for Ubuntu 18
You can now check how your app how's doing your application

### Activate alerts on Digital Ocean
You can create an alert policy to watn you if your app activity is highly increasing.
