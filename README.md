# Data manager

Manage datasets

## Install

pip install -e git+https://github.com/mobyle2/mobyle2.datamanager.git#egg=mobyle2.datamanager

This is only a prototype. Many features/security etc.. are not implemented.

## Create fake user

python  src/mobyle2.datamanager/db/fakeuser.py --config src/mobyle2.datamanager/development.ini

## Configuration

delay_background = false

Set to true to use Celery to execute some time intensive tasks in background

dm_store = /tmp/data
Pairtree (dataset files) location

upload_dir = /tmp/ftp
Temporary location for file uploads

use_history = true
Manage history on datasets, needs git installed

drop_key =
drop_secret =
DropBox identifiers for plugin



## Access

pserve --reload --app-name=datamanager --server-name=datamanager
src/mobyle2.conf/mobyle.ini

Root url is http://localhost:6543/data-manager

## TODO

FTP:
  manage complex objects (ListData and StructData)

In case of remote_upload file://
 - check if allowed in configuration

Add revert possibility for files from a previous version of file
Add user id in history for file history management

Move following attributes to global config instead of ini file

    site_uri = http://localhost:6543

    # Manage history on datasets, needs git installed
    use_history = true

    drop_key =
    drop_secret =


Analyse possibility to use dulwich instead of gitpython+git

# Background tasks

Background tasks are manaed with celery.

To start celery:
    pceleryd src/mobyle2.datamanager/development.ini

Configuration (broker, workers etc...) should be set in ini file.

# Plugins

Data manager supports plugins to upload or download files (delayed with Celery).
Plugins are delivered independently, and are based on Yapsy for plugin management.

A DropBox plugin is available at https://github.com/mobyle2/mobyle2.datamanager.dropbox
