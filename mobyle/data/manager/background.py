import logging
import tempfile
import urllib2
import os

from zipfile import ZipFile, is_zipfile

from celery import Celery
from celery.task import task
from mobyle.common.config import Config
from mobyle.common.objectmanager import ObjectManager
from mobyle.common.mobyleError import MobyleError

from  mobyle.data.manager.pluginmanager import DataPluginManager
from mobyle.common.connection import connection

from bson.objectid import ObjectId


# Initial setup
CONF = Config.config()
Celery('tasks', broker=CONF.get('app:main', 'db_uri') +
        CONF.get('app:main', 'db_name') )


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
    logging.info("Upload in background file " + options['name'] + ':' + furl)
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
    logging.info("Download in background file " +
                str(options['protocol']) + furl)
    mngr = ObjectManager()
    mngr.update(ObjectManager.DOWNLOADING, options)

    data_plugin_manager = DataPluginManager.get_manager()

    try:
        if options['protocol'] in ['http://', 'ftp://']:
            f = urllib2.urlopen(options['protocol'] + furl)
            (out, file_path) = tempfile.mkstemp()
            output_file = open(file_path, 'wb')
            output_file.write(f.read())
            options['files'] = [file_path]
            dataset = mngr.update(ObjectManager.DOWNLOADED, options)
            if len(dataset) > 1:
                raise MobyleError("download manage only one file")
            if dataset[0]['status'] == ObjectManager.UNCOMPRESS:
                # delay decompression
                options['delete'] = True
                if options['delay']:
                    uncompress.delay(file_path, options)
                else:
                    uncompress(file_path, options)
            else:
                os.remove(file_path)
        elif options['protocol'] in ['file://', 'symlink://']:
            if 'user_id' not in options:
                logging.error('no user id for file/symlink task')
                return
            user = connection.User.find_one({'_id':
                                            ObjectId(options['user_id'])})
            file_path = os.path.join(user['home_dir'], furl)
            # Only copy from user home directory
            if True or user['admin'] or (user['home_dir'] and \
            os.path.realpath(file_path).startswith(user['home_dir'])):
                # Do the copy or symlink
                if options['protocol'] == 'symlink://':
                    # symlink
                    options['files'] = [file_path]
                    mngr.update(ObjectManager.SYMLINK, options)
                else:
                    # copy
                    options['files'] = [file_path]
                    dataset = mngr.update(ObjectManager.DOWNLOADED, options)
                    # We manage here one file at a time, so only one dataset
                    if len(dataset) > 1:
                        raise MobyleError("download manage only one file") 
                    if dataset[0]['status'] == ObjectManager.UNCOMPRESS:
                        # delay decompression
                        if options['delay']:
                            uncompress.delay(file_path, options)
                        else:
                            uncompress(file_path, options)

        elif options['protocol'] in DataPluginManager.supported_protocols:
            # Use plugins
            plugin = data_plugin_manager.getPluginByName(options['protocol'])
            drop = plugin.plugin_object
            file_path = drop.download(furl, options)
            options['files'] = [file_path]
            dataset = mngr.update(ObjectManager.DOWNLOADED, options)
            if len(dataset) > 1:
                raise MobyleError("download manage only one file")
            if dataset[0]['status'] == ObjectManager.UNCOMPRESS:
                # delay decompression
                if options['delay']:
                    uncompress.delay(file_path, options)
                else:
                    uncompress(file_path, options)
            else:
                os.remove(file_path)
        else:
            logging.error("no matching protocol: " + str(options['protocol']))
            mngr.update(ObjectManager.ERROR, options)
    except Exception as e:
        logging.error("Download error: " + str(e)+" for "+furl)
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
        myzip = ZipFile(f, 'r')
        myzip.extractall(dir_path)
        myzip.close()
    else:
        mngr.update(ObjectManager.ERROR, options)
        return

    options['files'] = []
    for root, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            options['files'].append(os.path.join(dir_path, filename))
    try:
        mngr.update(ObjectManager.UNCOMPRESSED, options)
        if 'delete' in options and options['delete']:
                os.remove(f)
    except Exception:
        mngr.update(ObjectManager.ERROR, options)


@task
def compress(path, options=None):
    '''Compress a set of files for download

    :param path: Path to the files to be compressed
    :type path: string
    :param options: List of options, needs param "out" to specify zip out file
    :type options: dict
    '''
    with ZipFile(options['out'], 'w') as myzip:
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                myzip.write(os.path.join(path, filename))
