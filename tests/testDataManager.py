# -*- coding: utf-8 -*-
import unittest

from pyramid import testing

import os


from bson.objectid import ObjectId

import mobyle.common
from mobyle.common.config import Config

Config("development.ini")

from mobyle.common.connection import connection

base_url = "http://localhost:6543"

import mobyle.data.manager
import mobyle.data.manager.objectmanager
from mobyle.data.manager.objectmanager import ObjectManager
from mobyle.common.project import ProjectData


class DataManagerTest(unittest.TestCase):

        datadir = None

        def setUp(self):
            from webtest import TestApp
            self.testapp = TestApp("config:development.ini", relative_to="./")
            config = Config().config()
            dirname, filename = os.path.split(os.path.abspath(__file__))
            DataManagerTest.datadir = dirname + "/data"
            config.set("app:main", "store", DataManagerTest.datadir)
            ObjectManager.storage = None
            self.manager = ObjectManager()
            datasets = connection.ProjectData.find()
            for data in datasets:
                data.delete()

        def test_add(self):
            fid = self.manager.add("sample.py", _file__)
            data = connection.ProjectData.find_one({'_id': ObjectId(fid)})
            self.assertTrue(data is not None)
            self.assertTrue(data['status'] == ObjectManager.QUEUED)

        def test_store(self):
            options = {'uncompress': False, 'group': False, 'type':
            'text/plain', 'format': 'python'}
            fid = self.manager.store('sample.py', __file__, options)
            data = connection.ProjectData.find_one({'_id': ObjectId(fid)})
            self.assertTrue(data is not None)
            self.assertTrue(data['status'] == ObjectManager.DOWNLOADED)
            self.assertTrue(os.path.exists(DataManagerTest.datadir + "/pairtree_root/" + data['path']))

        def test_update(self):
            options = {'uncompress': False, 'group': False, 'type':
            'text/plain', 'format': 'python'}
            options['id'] = self.manager.add(__file__, options)
            self.manager.update(ObjectManager.ERROR, options)
            data = connection.ProjectData.find_one({'_id': ObjectId(options['id'])})
            self.assertTrue(data is not None)
            self.assertTrue(data['status'] == ObjectManager.ERROR)


