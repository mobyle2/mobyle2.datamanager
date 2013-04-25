'''
This module manages object storage
'''
from pairtree import PairtreeStorageFactory

import re
import uuid
import pairtree
import logging
import os
import sys,traceback

import mobyle.common
from mobyle.common.connection import connection
from mobyle.common.config import Config

from mongokit import Document
from bson.objectid import ObjectId

from git import Repo

from copy import deepcopy

from mobyle.data.tools.detector import BioFormat


@connection.register
class FakeData(Document):
    """
    Fake class to simulate datasets
    """

    __collection__ = 'fakedata'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'uid' : basestring, 'name' : basestring, 'path' : basestring,
    'status' : int, 'size' : int, 'project' : basestring, 'format' : basestring,
    'type' : basestring }
    default_values = {'format': 'txt'}


@connection.register
class FakeProject(Document):
    """
    Fake class to simulate datasets
    """

    __collection__ = 'fakeproject'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring }


class ObjectManager:
    """
    Manager for datasets.

    This class store files in a pairtree filesystem and update status of objects in database.
    """

    storage = None
    # Git repo
    repo = None
    use_repo = False

    QUEUED = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    UNCOMPRESS = 3
    FORMATCHECKING = 4
    ERROR = 5
    UNCOMPRESSED = 6

    FILEROOT = 'data'

    def __init__(self):
        config = Config.config()
        logging.debug("store = "+str(ObjectManager.storage)+ \
            ", set to "+config.get("app:main", "store"))

        if config.has_option("app:main","use_history"):
            ObjectManager.use_repo = config.getboolean("app:main","use_history")
        else:
            ObjectManager.use_repo = False

        if ObjectManager.storage is None:
            config = Config.config()
            fstore = PairtreeStorageFactory()
            ObjectManager.storage = fstore.get_store( \
                store_dir=config.get("app:main","store"), uri_base="http://")
            logging.debug("store = "+str(config.get("app:main", "store")))
            #if ObjectManager.use_repo:
            #    ObjectManager.repo = Repo.init(self.get_storage_path())

    @classmethod
    def _get_file_root(cls, uid):
        '''Get the file root to append to the pairtree path
        '''
        return ObjectManager.FILEROOT+'.'+uid

    def get_repository(self, uid):
        '''Get repository for the file. If it does not exists,
        create it. There is one repo per file path.

        :param uid: uid of the dataset
        :type uid: str
        :return: Repo for this dataset
        '''
        repo = self.get_storage_path() + \
            pairtree.id2path(uid)+ '/'+ self._get_file_root(uid)
        if not os.path.exists(repo+"/.git"):
            repository = Repo.init(repo)
        else:
            repository = Repo(repo)
        return repository

    def get_repository_index(self, uid):
        ''' Get repository index'''
        return self.get_repository(uid).index

    @classmethod
    def get_storage_path(cls):
        '''Get path to the storage'''
        config = Config.config()
        return config.get("app:main", "store")+"/pairtree_root/"

    def get_file_path(self, uid):
        '''Get full path for a file uid'''
        return self.get_storage_path()+pairtree.id2path(uid)+ \
            "/"+self._get_file_root(uid)+"/"+uid

    def delete(self, uid, options=None):
        '''
        Delete a file from storage and database

        :param uid: Name of the file (uid)
        :type uid: str
        '''
        if options is None:
            options = {}
        dataset = None
        try:
            dataset = connection.FakeData.find_one({ "uid" : uid})
            if dataset is not None:
                if dataset['path']:
                    obj = ObjectManager.storage.get_object(uid)
                    # If origin is a archive, it has not been added
                    # to the repository
                    if ObjectManager.use_repo and not options['uncompress']:
                        index = self.get_repository_index(uid)
                        index.remove([uid])
                        if 'msg' in options:
                            msg = options['msg']
                        else:
                            msg = "File removed"
                        index.commit(msg+" "+dataset['name'])
                    else:
                        path = self._get_file_root(uid)
                        obj.del_file(uid,path)
        except Exception as e:
            logging.error("Error while trying to delete ")
            #traceback.print_exc(file=sys.stdout)
        if dataset is not None:
            dataset.delete()

    @classmethod
    def add(cls, name, options=None):
        '''
        Adds a new dataset in status queued

        :param name: name fo the file
        :type name: str
        :param options: options related to file (project,...)
        :type options: dict
        :return: data database id
        '''
        if options is None:
            options = {}
        Config.config()
        uid = uuid.uuid4().hex
        dataset = connection.FakeData()
        dataset['name'] = name
        dataset['uid'] = uid
        dataset['status'] = ObjectManager.QUEUED
        if 'project' in options:
            dataset['project'] = options['project']
        dataset.save()
        return str(dataset['_id'])

    @classmethod
    def isarchive(cls, filepath):
        ''' Check if file is a supported archive format

        :param filepath: path of the file
        :type filepath: str
        :return: True if match a known/supported archive type
        '''
        filetypes = re.compile( '\.(tar\.gz|bz2|zip)')
        return filetypes.search(filepath)

    def update(self, status, options):
        '''
        Update the status of the object

        :param id: Database id of the data
        :type id: str
        :param status: Status of the  upload/download (QUEUED,DOWNLOADING,DOWNLOADED,ERROR)
        :type status: int
        '''
        dataset = connection.FakeData.find_one({ "_id" : ObjectId(options['id'])})

        if status == ObjectManager.DOWNLOADED and options['uncompress'] and\
        self.isarchive(options['name']):
            status = ObjectManager.UNCOMPRESS

        if status == ObjectManager.DOWNLOADED or \
             status == ObjectManager.UNCOMPRESSED:
            # Data is downloaded and eventually uncompressed
            Config.config()
            uid = dataset['uid']
            path = self._get_file_root(uid)
            obj = ObjectManager.storage.get_object(uid)
            if options['uncompress']:
                if options['group']:
                    dataset['path'] = pairtree.id2path(uid)+path
                for filepath in options['files']:
                    if options['group']:
                        # Copy files
                        with open(filepath,'rb') as stream:
                            obj.add_bytestream(os.path.basename(filepath), stream, path)
                        # TODO Add file info for all files 
                        # TODO manage Data object complexity, subdir etc...
                        # Update current object
                    else:
                        # Create a new data for this file
                        newoptions = deepcopy(options)
                        newoptions['uncompress'] = False
                        newoptions['group'] = False
                        newoptions['id'] = None
                        dataid = self.store(os.path.basename(filepath), \
                            filepath, newoptions) 
                if not options['group']:
                    # remove current obj, each sub file is a new independant
                    # object
                    self.delete(uid, options)
                    # We have managed child object
                    # now we can leave
                    return
            else:
                dataset['path'] = \
                pairtree.id2path(uid)+"/"+self._get_file_root(uid)+"/"+uid
                with open(options['file'],'rb') as stream:
                    obj.add_bytestream(uid, stream, path)
                dataset['size'] = os.path.getsize(self.get_storage_path()+dataset['path'])

            if 'project' in options:
                dataset['project'] = options['project']
            fformat = None
            mime = None

            if options['format'] == 'auto':
                # Try auto-detect
                detector = BioFormat()
                fformat = detector.detect_by_extension(dataset['name'])
                if fformat is None:
                    (fformat, mime) = detector.detect(self.get_storage_path()+dataset['path'])
            else:
                fformat = options['format']

            dataset['format'] = fformat

        dataset['type'] = options['type']

        dataset['status'] = status
        dataset.save()
        if status == ObjectManager.UNCOMPRESS:
            # delay decompression
            from mobyle.data.manager.background import uncompress
            uncompress.delay(options['file'], options)




    def store(self, name, infile, options=None):
        '''
        Adds a new dataset and store input file

        :param name: name fo the file
        :type name: str
        :param infile: Path to the input file
        :type infile: str
        :param options: options related to file (project,...)
        :type options: dict
        :return: data database id
        '''
        if options is None:
            options = {}
        Config.config()
        if 'id' in options and options['id']:
            dataset = connection.FakeData.find_one({ '_id' : ObjectId(options['id']) })
            uid = dataset['uid']
        else:
            dataset = connection.FakeData()
            uid = uuid.uuid4().hex

        obj = ObjectManager.storage.get_object(uid)
        with open(infile,'rb') as stream:
            obj.add_bytestream(uid, stream, self._get_file_root(uid))

        dataset['name'] = name
        dataset['uid'] = uid
        dataset['path'] = pairtree.id2path(uid)+"/"+self._get_file_root(uid)+"/"+uid
        dataset['status'] = ObjectManager.DOWNLOADED
        if options['uncompress'] and self.isarchive(name) is not None:
            dataset['status'] = ObjectManager.UNCOMPRESS
            options['original_format']  = options['format']
            options['format'] = 'archive'

        dataset['size'] = os.path.getsize(self.get_storage_path()+dataset['path'])
        if 'project' in options:
            dataset['project'] = options['project']

        if options['format'] == 'auto':
            # Try auto-detect
            detector = BioFormat()
            fformat = detector.detect_by_extension(dataset['name'])
            if fformat is None:
                (fformat, mime) = detector.detect(self.get_storage_path()+dataset['path'])
        else:
            fformat = options['format']

        dataset['format'] = fformat
        dataset['type'] = options['type']

        dataset.save()

        if dataset['status'] == ObjectManager.UNCOMPRESS:
            # delay decompression
            from mobyle.data.manager.background import uncompress
            newoptions = deepcopy(options)
            newoptions['id'] = dataset['_id']
            newoptions['format']  = options['original_format']
            uncompress.delay(self.get_file_path(dataset['uid']), newoptions)


        if ObjectManager.use_repo and not options['uncompress']:
            index = self.get_repository_index(uid)
            index.add([uid])
            if 'msg' in options:
                msg = options['msg']
            else:
                msg = "Update file content"
            index.commit(msg+" "+dataset['name'])

        return dataset['_id']


    def history(self, fid):
        '''
        Get historical data from repository commits

        :param fid: Id of the dataset needing historical operations
        :type fid: str
        :return: array of commit date and message dict
        '''

        if not ObjectManager.use_repo:
            return []
        dataset = connection.FakeData.find_one({ '_id' : ObjectId(fid) })
        uid = dataset['uid']
        #path = pairtree.id2path(uid) + "/"+ self._get_file_root(uid) + '/'+ uid
        repo = self.get_repository(uid)
        head = repo.head
        commits = []
        for commit in head.commit.iter_parents(paths='', skip=0):
            #if commit.count(paths=path) >= 0:
            commits.append({ 'committed_date' : commit.committed_date, \
                            'message' : commit.message })
        return commits
          

