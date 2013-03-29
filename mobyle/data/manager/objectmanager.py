from pairtree import *

import uuid
import pairtree
import logging
import datetime

import mobyle.common
from mobyle.common.connection import connection
from mobyle.common.config import Config

from mongokit import Document
from bson.objectid import ObjectId

from git import *

from mobyle.data.tools.detector import BioFormat

@connection.register
class FakeData(Document):
    """
    Fake class to simulate datasets
    """

    __collection__ = 'fakedata'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'uid' : basestring, 'name' : basestring, 'path' : basestring, 'status' : int, 'size' : int, 'project' : basestring, 'format' : basestring }
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
    ERROR = 3

    def __init__(self):
        config = Config.config()
        logging.error("store = "+str(ObjectManager.storage)+", set to "+config.get("app:main","store"))

        if config.has_option("app:main","use_history"):
            ObjectManager.use_repo = config.getboolean("app:main","use_history")
        else:
            ObjectManager.use_repo = False

        if ObjectManager.storage is None:
            config = Config.config()
            f = PairtreeStorageFactory()
            ObjectManager.storage = f.get_store(store_dir=config.get("app:main","store"), uri_base="http://")
            logging.error("store = "+str(config.get("app:main","store")))
            if ObjectManager.use_repo:
                ObjectManager.repo = Repo.init(self.get_storage_path())


    def get_storage_path(self):
        '''Get path to the storage'''
        config = Config.config()
        return config.get("app:main","store")+"/pairtree_root/"

    def delete(self,uid,options={}):
        '''
        Delete a file from storage and database

        :param uid: Name of the file (uid)
        :type uid: str
        '''
        dataset = None
        try:
            dataset = connection.FakeData.find_one({ "uid" : uid})
            if dataset is not None:
                if dataset['path']:
                    obj = ObjectManager.storage.get_object(uid)
                    obj.del_file(uid)
                    if ObjectManager.use_repo:
                        index = ObjectManager.repo.index
                        index.remove([dataset['path']])
                        if 'msg' in options:
                            msg = options['msg']
                        else:
                            msg = "File removed"
                        index.commit(msg+" "+dataset['name'])
        except Exception as e:
            logging.error("Error while trying to delete")
        if dataset is not None:
            dataset.delete()

    def add(self,name,options={}):
        '''
        Adds a new dataset in status queued

        :param name: name fo the file
        :type name: str
        :param options: options related to file (project,...)
        :type options: dict
        :return: data database id
        '''
        config = Config.config()
        uid = uuid.uuid4().hex
        dataset = connection.FakeData()
        dataset['name'] = name
        dataset['uid'] = uid
        dataset['status'] = ObjectManager.QUEUED
        if 'project' in options:
            dataset['project'] = options['project']
        dataset.save()
        return str(dataset['_id'])

    def update(self,status,options):
        '''
        Update the status of the object

        :param id: Database id of the data
        :type id: str
        :param status: Status of the  upload/download (QUEUED,DOWNLOADING,DOWNLOADED,ERROR)
        :type status: int
        '''
        dataset = connection.FakeData.find_one({ "_id" : ObjectId(options['id'])})
        if status == ObjectManager.DOWNLOADED:
            config = Config.config()
            uid = dataset['uid']
            obj = ObjectManager.storage.get_object(uid)
            with open(options['file'],'rb') as stream:
                obj.add_bytestream(uid, stream)
            dataset['path'] = pairtree.id2path(uid)+"/"+uid
            dataset['size'] = os.path.getsize(self.get_storage_path()+dataset['path'])
            if 'project' in options:
                dataset['project'] = options['project']
            format = None
            mime = None

            if options['type'] == 0:
                # Try auto-detect
                detector = BioFormat()
                format = detector.detect_by_extension(dataset['name'])
                if format is None:
                    (format,mime) = detector.detect(self.get_storage_path()+dataset['path'])
            else:
                format = options['type']

            dataset['format'] = format

        dataset['status'] = status
        dataset.save()



    def store(self,name,file,options={}):
        '''
        Adds a new dataset and store input file

        :param name: name fo the file
        :type name: str
        :param file: Path to the input file
        :type file: str
        :param options: options related to file (project,...)
        :type options: dict
        :return: data database id
        '''
        config = Config.config()
        if 'id' in options and options['id']:
            dataset = connection.FakeData.find_one({ '_id' : ObjectId(options['id']) })
            uid = dataset['uid']
        else:
            dataset = connection.FakeData()
            uid = uuid.uuid4().hex

        obj = ObjectManager.storage.get_object(uid)
        with open(file,'rb') as stream:
            obj.add_bytestream(uid, stream)

        dataset['name'] = name
        dataset['uid'] = uid
        dataset['path'] = pairtree.id2path(uid)+"/"+uid
        dataset['status'] = ObjectManager.DOWNLOADED
        dataset['size'] = os.path.getsize(self.get_storage_path()+dataset['path'])
        if 'project' in options:
            dataset['project'] = options['project']

        if options['type'] == 0:
            # Try auto-detect
            detector = BioFormat()
            format = detector.detect_by_extension(dataset['name'])
            if format is None:
                (format,mime) = detector.detect(self.get_storage_path()+dataset['path'])
        else:
            format = options['type']

        dataset['format'] = format

        dataset.save()

        if ObjectManager.use_repo:
            index = ObjectManager.repo.index
            index.add([dataset['path']])
            if 'msg' in options:
                msg = options['msg']
            else:
                msg = "Update file content"
            index.commit(msg+" "+dataset['name'])

        return dataset['_id']


    def history(self,id):
        if not ObjectManager.use_repo:
            return []
        dataset = connection.FakeData.find_one({ '_id' : ObjectId(id) })
        uid = dataset['uid']
        path = pairtree.id2path(uid)+"/"+uid
        head = ObjectManager.repo.head
        #master = head.reference
        commits = []
        for commit in head.commit.iter_parents(paths='',skip=0):
            if commit.count(paths=path) >= 0:
                commits.append({ 'committed_date' : commit.committed_date, 'message' : commit.message })
        #return master.log()
        return commits
          



if __name__ == "__main__":
    config = Config.config()
    config.set("app:main","store","/tmp/data-test")
    import mobyle.common.connection

    mngr = ObjectManager()
    options = {}
    options['type'] = 0
    options['project'] = 'sample'
    id = mngr.store("sample.py",__file__,options)
    options['id'] = id
    options['msg'] = 'file replace'
    id = mngr.store("sample.py",__file__,options)
    logs = mngr.history(id)
    for log in logs:
        print "Log: "+str(datetime.datetime.fromtimestamp(log.committed_date).strftime('%Y-%m-%d %H:%M:%S'))+", "+log.message
