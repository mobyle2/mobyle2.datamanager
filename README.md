# Data manager

Manage datasets

This is only a prototype. Many features/security etc.. are not implemented.

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
