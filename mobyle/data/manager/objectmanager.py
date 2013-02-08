from pairtree import *

from mobyle.common.config import Config

class ObjectManager:

    storage = None

    def __init__(self):
        if ObjectManager.storage is None:
            config = Config.config()
            f = PairtreeStorageFactory()
            ObjectManager.storage = f.get_store(store_dir=config.get("app:main","store"), uri_base="http://")


    def store(self,name,file):
        obj = ObjectManager.storage.create_object(name)
        with open(file,'rb') as stream:
            obj.add_bytestream(name, stream)

if __name__ == "__main__":
    config = Config.config()
    config.set("app:main","store","/tmp/data")
    mngr = ObjectManager()
    mngr.store("sample.py",__file__)
