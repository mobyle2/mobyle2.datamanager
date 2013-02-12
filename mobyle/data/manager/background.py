import logging

from celery import Celery
from celery.task import task
from mobyle.common.config import Config

conf = Config.config()

celery = Celery('tasks', broker=conf.get('app:main','db_uri')+'/'+conf.get('app:main','db_name')+'/')

@task
def download(project=None,furl=None,uncompress=False,group=False):
    print "Download in background file "+furl
