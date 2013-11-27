# -*- coding: utf-8 -*-
import unittest

from pyramid import testing

import os
import tempfile

from bson.objectid import ObjectId

import mobyle.common
from mobyle.common.config import Config
from mobyle.common.mobyleConfig import MobyleConfig

Config("development.ini")

from mobyle.common.connection import connection

base_url = "http://localhost:6543"

import mobyle.data.manager
import mobyle.common.objectmanager
from mobyle.common.objectmanager import ObjectManager
from mobyle.common.project import ProjectData
from mobyle.data.manager.background import download


class DataManagerTest(unittest.TestCase):

        datadir = None

        def setUp(self):
            from webtest import TestApp
            self.testapp = TestApp("config:development.ini", relative_to="./")
            if MobyleConfig.get_current() is None:
                mob_config = connection.MobyleConfig()
                mob_config['active'] = True
                mob_config['data']['remote']['allowed_protocols'] = 'http,ftp'
                mob_config['data']['local']['allowed_copy'] = True
                mob_config.save()
            config = Config().config()
            dirname, filename = os.path.split(os.path.abspath(__file__))
            DataManagerTest.datadir = dirname + "/data"
            config.set("app:main", "store", DataManagerTest.datadir)
            ObjectManager.storage = None
            self.manager = ObjectManager()
            datasets = connection.ProjectData.find()
            for data in datasets:
                data.delete()
            users = connection.User.find()
            for user in users:
                user.delete()
            projects = connection.Project.find()
            for project in projects:
                project.delete()

        def test_add(self):
            fid = self.manager.add("sample.py")
            data = connection.ProjectData.find_one({'_id': ObjectId(fid)})
            self.assertTrue(data is not None)
            self.assertTrue(data['status'] == ObjectManager.QUEUED)

        def test_store(self):
            options = {'uncompress': False, 'group': False, 'type':
            'text/plain', 'format': 'python'}
            newdata = self.manager.store('sample.py', __file__, options)
            fid = newdata['_id']
            data = connection.ProjectData.find_one({'_id': ObjectId(fid)})
            self.assertTrue(data is not None)
            self.assertTrue(data['status'] == ObjectManager.DOWNLOADED)
            self.assertTrue(os.path.exists(DataManagerTest.datadir +
                            "/pairtree_root/" + data['data']['path']))

        def test_update(self):
            options = {'uncompress': False, 'group': False, 'type':
            'text/plain', 'format': 'python'}
            newdata = self.manager.add(__file__, options)
            options['id'] = newdata['_id']
            self.manager.update(ObjectManager.ERROR, options)
            data = connection.ProjectData.find_one({'_id': ObjectId(options['id'])})
            self.assertTrue(data is not None)
            self.assertTrue(data['status'] == ObjectManager.ERROR)

        def test_delete(self):
            options = {'uncompress': False, 'group': False, 'type':
            'text/plain', 'format': 'python'}
            newdata = self.manager.store('sample.py', __file__, options)
            fid = newdata['_id']
            data = connection.ProjectData.find_one({'_id': ObjectId(fid)})
            self.assertTrue(data['status'] == ObjectManager.DOWNLOADED)
            self.assertTrue(os.path.exists(DataManagerTest.datadir +
                            "/pairtree_root/" + data['data']['path']))
            self.manager.delete(fid, options)
            self.assertFalse(os.path.exists(DataManagerTest.datadir +
                            "/pairtree_root/" + data['data']['path']))
            try:
                data = connection.ProjectData.find_one({'_id': ObjectId(fid)})
                self.fail("Data should have been deleted")
            except Exception:
                # Nothing found, this is fine
                pass

        def test_isarchive(self):
            self.assertTrue(self.manager.isarchive('test.zip') is not None)
            self.assertTrue(self.manager.isarchive('test.tar.gz') is not None)
            self.assertTrue(self.manager.isarchive('test.bz2') is not None)
            self.assertTrue(self.manager.isarchive('test.txt') is None)


        def test_copy_local(self):
            my_user = connection.User()
            my_user['home_dir'] = tempfile.mkdtemp()
            my_user['email'] = 'fake@user4test'
            my_user.save()
            my_project = connection.Project()
            my_project['name'] = 'sample'
            my_project['owner'] = my_user['_id']
            my_project.save()
            my_tmp_file = open( os.path.join(my_user['home_dir'],'sample.txt'),'w')
            my_tmp_file.write("some data")
            my_tmp_file.close()
	    options = {}
            options['user_id'] = str(my_user['_id'])
            options['protocol'] = 'file://'
            options['group'] = False
            options['uncompress'] = False
            options['project'] = str(my_project['_id'])
            options['type'] = 'text/plain'
            options['format'] = 'text'
            options['rurl'] = os.path.join(my_user['home_dir'],'sample.txt')
            manager = ObjectManager()
            newdata  =manager.add(options['rurl'], options)
            options['id'] = newdata['_id']
            download(options['rurl'], options)
            data = connection.ProjectData.find_one({'_id': ObjectId(options['id'])})
            self.assertTrue(os.path.exists(DataManagerTest.datadir +
                            "/pairtree_root/" + data['data']['path']))


        def test_symlink_local(self):
            my_user = connection.User()
            my_user['home_dir'] = tempfile.mkdtemp()
            my_user['email'] = 'fake@user4test'
            my_user.save()
            my_project = connection.Project()
            my_project['name'] = 'sample'
            my_project['owner'] = my_user['_id']
            my_project.save()
            my_tmp_file = open( os.path.join(my_user['home_dir'],'sample.txt'),'w')
            my_tmp_file.write("some data")
            my_tmp_file.close()
	    options = {}
            options['user_id'] = str(my_user['_id'])
            options['protocol'] = 'symlink://'
            options['group'] = False
            options['uncompress'] = False
            options['project'] = str(my_project['_id'])
            options['type'] = 'text/plain'
            options['format'] = 'text'
            options['rurl'] = os.path.join(my_user['home_dir'],'sample.txt')
            manager = ObjectManager()
            newdata = manager.add(options['rurl'], options)
            options['id'] = newdata['_id']
            download(options['rurl'], options)
            data = connection.ProjectData.find_one({'_id': ObjectId(options['id'])})
            self.assertTrue(os.path.exists(DataManagerTest.datadir +
                            "/pairtree_root/" + data['data']['path']))

