import logging
import tempfile
import urllib2
import os

from celery import Celery
from celery.task import task
from mobyle.common.config import Config
from mobyle.data.manager.objectmanager import ObjectManager


conf = Config.config()

import mobyle.common.connection
mobyle.common.connection.init_mongo(conf.get('app:main','db_uri'))


celery = Celery('tasks', broker=conf.get('app:main','db_uri')+'/'+conf.get('app:main','db_name')+'/')

@task
def download(furl,options={}):
    '''
    Download a remote file (http,ftp,file)

    :param furl: URL to the file
    :type furl: str
    :param options: name,id,.. of the file
    :type options: dict
    '''
    logging.info("Download in background file "+furl)
    mngr = ObjectManager()
    mngr.update(ObjectManager.DOWNLOADING,options)
    try:
        f = urllib2.urlopen(furl)
        (out,file_path) = tempfile.mkstemp()
        output_file = open(file_path, 'wb')
        output_file.write(f.read())
        options['file'] = file_path
        mngr.update(ObjectManager.DOWNLOADED,options)
        os.remove(file_path)
    except Exception as e:
        logging.error("Download error: "+str(e))
        mngr.update(ObjectManager.ERROR,options)

