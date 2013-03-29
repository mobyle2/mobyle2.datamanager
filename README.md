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

Add revert possibility for files from a previous version of file
Add user id in history for file history management

Move following attributes to global config instead of ini file

    store = /tmp/data
    upload_dir = /tmp/ftp
    site_uri = http://localhost:6543
    
    # Manage history on datasets, needs git installed
    use_history = true
    
    drop_key =
    drop_secret =


Analyse possibility to use dulwich instead of gitpython+git
Analyse possibility to create a repo per file instead of global repo

# Background tasks

Background tasks are manaed with celery.

To start celery:
    pceleryd src/datamngr/development.ini

Configuration (broker, workers etc...) should be set in ini file.

# Plugins

Data manager supports plugins to upload or download files (delayed with Celery).
Plugins are delivered independently, and are based on Yapsy for plugin management.

A DropBox plugin is available at https://github.com/mobyle2/mobyle2.datamanager.dropbox
