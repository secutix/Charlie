Charlie Test Manager
====================

A software testing manager written in python running on django.

Dependencies
------------

###In order to be able to install Charlie, you will need to install these first :
* python2
* python-pip
* Apache httpd
* memcached
* MySQL server
* python-mysqldb (aka mysql-python)
* Apache's WSGI module
* Django
* suds client
* python-memcached
* virtualenv
* simplejson

Download the source
-------------------

* [.tar.gz](https://github.com/nire/Charlie/tarball/master)
* [.zip](https://github.com/nire/Charlie/zipball/master)
* via git : git clone https://github.com/nire/Charlie

Installation
------------

### Charlie/charlie/tmg.wsgi
* edit app_home to the absolute path of the "Charlie" directory
* edit line 5 (sys.path.append...) to the absolute path of your django installation

### Charlie/apache_conf/charlie.conf
* replace APP_HOME on lines 6, 7, 8, 9, 15, 20, 27 with the absolute path of the Charlie directory

### Apache httpd main config file
* set DocumentRoot to [APP_HOME]/charlie
* enable module wsgi
* set User and Group to the user that owns the Charlie directory
* in the <Directory [...]> associated to DocumentRoot, check that the line is "Allow from all" and not "Deny from all"
* at the end of the file, add the line :
	Include "/path/to/Charlie/apache_conf/charlie.conf"

### Charlie/charlie/settings.py
* edit DATABASE
* edit APP_HOME to the absolute path of the Charlie/charlie directory
* if necessary, edit the first item of TEMPLATE_DIRS : change "/usr/lib/pyshared/python2.6/django" to the absolute path of your django installation

### Charlie/charlie/test_manager/config.py
#### In this file, you can adjust the settings of the application :
* URL to the Jira wsdl login
* Settings for the creation of test cases
* Default tester availability (in %)
* Choice of scheduling algorithm
* Management menu
