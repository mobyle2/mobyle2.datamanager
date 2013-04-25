import logging
import tempfile
import urllib2
import os

from zipfile import ZipFile, is_zipfile

from celery import Celery
from celery.task import task
from mobyle.common.config import Config
from mobyle.data.manager.objectmanager import ObjectManager

from  mobyle.data.manager.pluginmanager import DataPluginManager


# Initial setup
CONF = Config.config()
Celery('tasks', broker=CONF.get('app:main', 'db_uri')+ \
        '/'+CONF.get('app:main', 'db_name')+'/')



@task
def upload(furl, options=None):
    '''
    Upload a remote file (plugins)

    :param furl: path to the file
    :type furl: str
    :param options: name,id,.. of the file
    :type options: dict
    '''
    if options is None:
        options = {}
    logging.info("Upload in background file "+options['name']+':'+furl)
    # For init
    ObjectManager()
    data_plugin_manager = DataPluginManager.get_manager()
    if options['protocol'] in DataPluginManager.supported_protocols:
        plugin = data_plugin_manager.getPluginByName(options['protocol'])
        drop = plugin.plugin_object
        drop.upload(furl, options)


@task
def download(furl, options=None):
    '''
    Download a remote file (http,ftp,file)

    :param furl: URL to the file
    :type furl: str
    :param options: name,id,.. of the file
    :type options: dict
    '''
    if options is None:
        options = {}
    logging.error("Download in background file "+str(options['protocol'])+':'+furl)
    mngr = ObjectManager()
    mngr.update(ObjectManager.DOWNLOADING, options)

    data_plugin_manager = DataPluginManager.get_manager()
    
    try:
        if options['protocol'] in ['http://','ftp://']:
            f = urllib2.urlopen(options['protocol']+furl)
            (out, file_path) = tempfile.mkstemp()
            output_file = open(file_path, 'wb')
            output_file.write(f.read())
            options['file'] = file_path
            mngr.update(ObjectManager.DOWNLOADED, options)
            os.remove(file_path)
        elif options['protocol'] in DataPluginManager.supported_protocols:
            # Use plugins
            plugin = data_plugin_manager.getPluginByName(options['protocol'])
            drop = plugin.plugin_object
            file_path =  drop.download(furl, options)
            options['file'] = file_path
            mngr.update(ObjectManager.DOWNLOADED, options)
            os.remove(file_path)
        else:
            logging.error("no matching protocol: "+str(options['protocol']))
            mngr.update(ObjectManager.ERROR, options)           
    except Exception as e:
        logging.error("Download error: "+str(e))
        mngr.update(ObjectManager.ERROR, options)

@task
def uncompress(f, options=None):
    '''
    Uncompress a local file as a complex object
    or a set of objects

    :param furl: Path to the file
    :type furl: str
    :param options: group,.. of the file
    :type options: dict
    '''
    if options is None:
        options = {}
    mngr = ObjectManager()

    dir_path = tempfile.mkdtemp()

    if is_zipfile(f):
        myzip = ZipFile(f,'r')
        myzip.extractall(dir_path)
        myzip.close()
    else:
        mngr.update(ObjectManager.ERROR, options)
        return

    options['files'] = []
    for root, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            options['files'].append(os.path.join(dir_path, filename))
    mngr.update(ObjectManager.UNCOMPRESSED, options)
