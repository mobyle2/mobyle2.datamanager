# -*- coding: utf-8 -*-
import unittest

from pyramid import testing

import pymongo
import copy
import os

from bson.objectid import ObjectId

import mobyle.common
from mobyle.common.config import Config

Config("development.ini")

from mobyle.common import session

base_url = "http://localhost:6543"

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")
import mobyle.data.manager
import mobyle.data.manager.objectmanager
from mobyle.data.manager.objectmanager import ObjectManager,FakeData

class DataManagerTest(unittest.TestCase):

        datadir = None

        def setUp(self):
            from webtest import TestApp
            self.testapp = TestApp("config:development.ini", relative_to="./")
            config = Config().config()
            dirname, filename = os.path.split(os.path.abspath(__file__))
            DataManagerTest.datadir = dirname + "/data"
            config.set("app:main","store",DataManagerTest.datadir)
            from mobyle.data.manager.objectmanager import ObjectManager
            ObjectManager.storage = None
            self.manager = ObjectManager()
            mobyle.common.session.register([FakeData])
            datasets = mobyle.common.session.FakeData.find()
            for data in datasets:
                data.delete()


        def test_add(self):
            id = self.manager.add("sample.py",__file__)
            data = mobyle.common.session.FakeData.find_one({ '_id' : ObjectId(id) }) 
            self.assertTrue(data is not None)
            self.assertTrue(data['status']==ObjectManager.QUEUED)


	def test_store(self):
            options = { 'uncompress' : False , 'group' : False }
            id = self.manager.store('sample.py',__file__,options)
            data = mobyle.common.session.FakeData.find_one({ '_id' : ObjectId(id) })
            self.assertTrue(data is not None)
            self.assertTrue(data['status']==ObjectManager.DOWNLOADED)
            self.assertTrue(os.path.exists(DataManagerTest.datadir+"/pairtree_root/"+data['path']))

	def test_update(self):
            id = self.manager.add("sample.py",__file__)
            self.manager.update(ObjectManager.ERROR,{ "id" : id})
            data = mobyle.common.session.FakeData.find_one({ '_id' : ObjectId(id) })
            self.assertTrue(data is not None)
            self.assertTrue(data['status']==ObjectManager.ERROR)
            

