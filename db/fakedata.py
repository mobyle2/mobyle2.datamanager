'''
Initialise database content
'''


import argparse
import sys
from hashlib import sha1
from random import randint
import bcrypt

from mobyle.common.config import Config


parser = argparse.ArgumentParser(description='Initialize database content.')
parser.add_argument('--config')

args = parser.parse_args()

if not args.config:
  print "config argument is missing"
  sys.exit(2)

# Init config
config = Config(args.config).config()

# Init connection


import mobyle.common
from mobyle.common.connection import connection
from mobyle.data.manager.objectmanager import FakeData,FakeProject

# Create root user
if connection.FakeProject.find({ 'name' : 'sample' }).count() == 0:
    project = connection.FakeProject()
    project['name'] = 'sample'
    project.save()
    project = connection.FakeProject()
    project['name'] = 'sample2'
    project.save()


