# -*- coding: utf-8 -*-

from shutil import copyfile
import sys
import os.path
import argparse
from mobyle.common.config import Config


parser = argparse.ArgumentParser(description='Initialize database content.')
parser.add_argument('--config')

args = parser.parse_args()

if not args.config:
    print "config argument is missing"
    sys.exit(2)

# Init config
config = Config(args.config).config()

import mobyle.common
from mobyle.common.connection import connection
from mobyle.common.users import User
from mobyle.common.project import Project
from mobyle.common.objectmanager import ObjectManager
from mobyle.common.data import RefData
# init
ObjectManager()

user = connection.User.find_one({'first_name' : 'John'})
if user is None:
    print "Sample user not found"
    sys.exit(1)
project = connection.Project.find_one({'name' : 'sample'})
if project is None:
    print "Sample project not found"
    sys.exit(1)

options = {}
options['project'] = str(project['_id'])
options['uncompress'] = False
options['group'] = False
options['name'] = 'mydata1'
options['format'] = "EDAM:123"
options['type'] = "EDAM:456"

my_dataset = ObjectManager.add("sample1", options, False)
# Get path to the objects
my_path = my_dataset.get_file_path()
# Write a file to the dataset directory
sample_file = __file__
data_file = os.path.join(my_path, os.path.basename(sample_file))


my_dataset1 = ObjectManager.store('mydata1',sample_file, options)
my_dataset1['tags'] = [ 'tag1', 'tag2', 'tag3' ]
my_dataset1.save()

options['name'] = 'mydata2'
my_dataset2 = ObjectManager.store('mydata2',sample_file, options)
my_dataset2['tags'] = [ 'tag1', 'tag3' ]
my_dataset2.save()

options['name'] = 'mydata3'
my_dataset3 = ObjectManager.store('mydata3',sample_file, options)
my_dataset3['tags'] = [ 'tag3' ]
my_dataset3['public'] = True
my_dataset3.save()

options['name'] = 'mydata4'
my_dataset3 = ObjectManager.store('mydata4',sample_file, options)
my_dataset3['tags'] = [ 'tag4' ]
my_dataset3['public'] = True
my_dataset3.save()




