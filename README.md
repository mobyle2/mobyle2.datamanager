# Data manager

Manage datasets

## Install

pip install -e git+https://github.com/mobyle2/mobyle2.datamanager.git#egg=mobyle2.datamanager

This is only a prototype. Many features/security etc.. are not implemented.

## Create fake user

python  src/mobyle2.datamanager/db/fakeuser.py --config src/mobyle2.datamanager/development.ini

## TODO

In case of remote_date file://
 - check if allowed in configuration
 - only only local registered users (ldap)
 - limit access to a list of root directories

# Background tasks

Background tasks are manaed with celery.

To start celery:
    pceleryd src/datamngr/development.ini

Configuration (broker, workers etc...) should be set in ini file.


# FTP test server

Run: python mobftp.py
Prototype hard codes the reading of development.ini for setup.
It runs a FTP server on port 2121, and you can log in with a user email and apikey as password.

PUT and DELETE are not yet coded.
You cannot change directory, you can only get a file with its ID (not the displayed name)

Example:
<pre>
Name (localhost:osallou): fakeemail@do-not-reply.fr
331 Username ok, send password.
Password: 
230 Welcome
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering extended passive mode (|||57370|).
125 Data connection already open. Transfer starting.
 DSC_0151.JPG                      88336 2013 02 20 15:18 b44ff600af6f4d8f8b2f31bbf476e864
226 Transfer complete.
ftp> get b44ff600af6f4d8f8b2f31bbf476e864
local: b44ff600af6f4d8f8b2f31bbf476e864 remote: b44ff600af6f4d8f8b2f31bbf476e864
</pre>

