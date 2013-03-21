import logging
import tempfile
import urllib2
import os

from celery import Celery
from celery.task import task
from mobyle.common.config import Config
from mobyle.data.manager.objectmanager import ObjectManager

from  mobyle.data.manager.pluginmanager import DataPluginManager

conf = Config.config()



celery = Celery('tasks', broker=conf.get('app:main','db_uri')+'/'+conf.get('app:main','db_name')+'/')



@task
def upload(furl,options={}):
    '''
    Upload a remote file (plugins)

    :param furl: path to the file
    :type furl: str
    :param options: name,id,.. of the file
    :type options: dict
    '''
    logging.info("Upload in background file "+options['name']+':'+furl)
    mngr = ObjectManager()
    dataPluginManager = DataPluginManager.get_manager()
    if options['protocol'] in DataPluginManager.supported_protocols:
        plugin = dataPluginManager.getPluginByName(options['protocol'])
        drop = plugin.plugin_object
        drop.upload(furl,options)

@task
def download(furl,options={}):
    '''
    Download a remote file (http,ftp,file)

    :param furl: URL to the file
    :type furl: str
    :param options: name,id,.. of the file
    :type options: dict
    '''
    logging.info("Download in background file "+str(options['protocol'])+':'+furl)
    mngr = ObjectManager()
    mngr.update(ObjectManager.DOWNLOADING,options)

    dataPluginManager = DataPluginManager.get_manager()
    
    try:
        if options['protocol'] in ['http://','ftp://']:
            f = urllib2.urlopen(options['protocol']+furl)
            (out,file_path) = tempfile.mkstemp()
            output_file = open(file_path, 'wb')
            output_file.write(f.read())
            options['file'] = file_path
            mngr.update(ObjectManager.DOWNLOADED,options)
            os.remove(file_path)
        elif options['protocol'] in DataPluginManager.supported_protocols:
            # Use plugins
            plugin = dataPluginManager.getPluginByName(options['protocol'])
            drop = plugin.plugin_object
            file_path =  drop.download(furl,options)
            options['file'] = file_path
            mngr.update(ObjectManager.DOWNLOADED,options)
            os.remove(file_path)
        else:
            logging.error("no matching protocol: "+str(options['protocol']))
            mngr.update(ObjectManager.ERROR,options)           
    except Exception as e:
        logging.error("Download error: "+str(e))
        mngr.update(ObjectManager.ERROR,options)

