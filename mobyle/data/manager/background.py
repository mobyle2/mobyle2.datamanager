import logging
import tempfile
import urllib2
import os

from celery import Celery
from celery.task import task
from mobyle.common.config import Config
from mobyle.data.manager.objectmanager import ObjectManager


conf = Config.config()

celery = Celery('tasks', broker=conf.get('app:main','db_uri')+'/'+conf.get('app:main','db_name')+'/')

@task
def download(furl,options={}):
    logging.error("Download in background file "+furl)
    f = urllib2.urlopen(furl)
    (out,file_path) = tempfile.mkstemp()
    output_file = open(file_path, 'wb')

    output_file.write(f.read())

    mngr = ObjectManager()
    mngr.store(furl,file_path,options)
    os.remove(file_path)

