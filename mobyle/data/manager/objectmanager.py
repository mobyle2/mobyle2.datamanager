from pairtree import *

import uuid
import pairtree
import logging

import mobyle.common
from mobyle.common import session
from mobyle.common.config import Config

from mongokit import Document
from bson.objectid import ObjectId

from mobyle.data.tools.detector import BioFormat

class FakeData(Document):
    """
    Fake class to simulate datasets
    """

    __collection__ = 'fakedata'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'uid' : basestring, 'name' : basestring, 'path' : basestring, 'status' : int, 'size' : int, 'project' : basestring, 'format' : basestring }
    default_values = {'format': 'txt'}

if mobyle.common.session:
    mobyle.common.session.register([FakeData])


class ObjectManager:
    """
    Manager for datasets.

    This class store files in a pairtree filesystem and update status of objects in database.
    """

    storage = None

    QUEUED = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    ERROR = 3

    def __init__(self):
        if ObjectManager.storage is None:
            config = Config.config()
            f = PairtreeStorageFactory()
            ObjectManager.storage = f.get_store(store_dir=config.get("app:main","store"), uri_base="http://")

    def get_storage_path(self):
        '''Get path to the storage'''
        config = Config.config()
        return config.get("app:main","store")+"/pairtree_root/"

    def delete(self,uid):
        '''
        Delete a file from storage and database

        :param uid: Name of the file (uid)
        :type uid: str
        '''
        dataset = None
        try:
            dataset = mobyle.common.session.FakeData.find_one({ "uid" : uid})
            if dataset is not None:
                if dataset['path']:
                    obj = ObjectManager.storage.get_object(uid)
                    obj.del_file(uid)
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
        dataset = mobyle.common.session.FakeData()
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
        mobyle.common.session.register([FakeData])
        dataset = mobyle.common.session.FakeData.find_one({ "_id" : ObjectId(options['id'])})
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

            if not type in options:
                options['type'] = 0

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
            dataset = mobyle.common.session.FakeData.find_one({ '_id' : ObjectId(options['id']) })
            uid = dataset['uid']
        else:
            dataset = mobyle.common.session.FakeData()
            uid = uuid.uuid4().hex

        obj = ObjectManager.storage.get_object(uid)
        with open(file,'rb') as stream:
            obj.add_bytestream(uid, stream)
        mobyle.common.session.register([FakeData])

        dataset['name'] = name
        dataset['uid'] = uid
        dataset['path'] = pairtree.id2path(uid)+"/"+uid
        dataset['status'] = ObjectManager.DOWNLOADED
        dataset['size'] = os.path.getsize(self.get_storage_path()+dataset['path'])
        if 'project' in options:
            dataset['project'] = options['project']

        if not type in options:
            options['type'] = 

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
        return dataset['_id']

if __name__ == "__main__":
    config = Config.config()
    config.set("app:main","store","/tmp/data")
    import mobyle.common.connection
    mobyle.common.connection.init_mongo('mongodb://localhost/')
    mobyle.common.session.register([FakeData])

    mngr = ObjectManager()
    mngr.store("sample.py",__file__)
