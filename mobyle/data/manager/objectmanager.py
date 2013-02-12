from pairtree import *

import uuid
import pairtree
import mobyle.common
from mobyle.common.config import Config

from mongokit import Document

class FakeData(Document):
    """
    Fake class to simulate datasets
    """

    __collection__ = 'fakedata'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'uid' : basestring, 'name' : basestring, 'path' : basestring, 'status' : int, 'size' : int, 'project' : basestring }

if mobyle.common.session:
    mobyle.common.session.register([FakeData])

class ObjectManager:

    storage = None

    def __init__(self):
        if ObjectManager.storage is None:
            config = Config.config()
            f = PairtreeStorageFactory()
            ObjectManager.storage = f.get_store(store_dir=config.get("app:main","store"), uri_base="http://")


    def store(self,name,file,options={}):
        config = Config.config()
        uid = uuid.uuid4().hex
        obj = ObjectManager.storage.get_object(uid)
        with open(file,'rb') as stream:
            obj.add_bytestream(uid, stream)
        dataset = mobyle.common.session.FakeData()
        dataset['name'] = name
        dataset['uid'] = uid
        dataset['path'] = pairtree.id2path(uid)+"/"+uid
        dataset['status'] = 2
        dataset['size'] = os.path.getsize(config.get("app:main","store")+"/pairtree_root/"+dataset['path'])
        if 'project' in options:
            dataset['project'] = options['project']
        dataset.save()

if __name__ == "__main__":
    config = Config.config()
    config.set("app:main","store","/tmp/data")
    import mobyle.common.connection
    mobyle.common.connection.init_mongo('mongodb://localhost/')
    mobyle.common.session.register([FakeData])

    mngr = ObjectManager()
    mngr.store("sample.py",__file__)
