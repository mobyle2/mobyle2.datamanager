# Data manager

Manage datasets

## Install

pip install -e git+https://github.com/mobyle2/mobyle2.datamanager.git#egg=mobyle2.datamanager

This is only a prototype. Many features/security etc.. are not implemented.

## Create fake user

python  src/mobyle2.datamanager/db/fakeuser.py --config src/mobyle2.datamanager/development.ini


## Access

Root url is http://localhost:6543/data-manager

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

# Plugins

Data manager supports plugins to upload or download files (delayed with Celery).
Plugins are delivered independently, and are based on Yapsy for plugin management.

A DropBox plugin is available at https://github.com/osallou/mobyle2.datamanager.dropbox
