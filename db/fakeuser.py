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
from mobyle.common.users import User
from mobyle.common.project import Project

# Create root user
if connection.User.find({ 'first_name' : 'John' }).count() == 0:
    pwd = sha1("%s"%randint(1,1e99)).hexdigest()
    Config.logger().warn('User created with password: '+ pwd )
    user = connection.User()
    user['first_name'] = 'John'
    user['last_name'] = 'Wayne'
    user['email'] = 'fakeemail@do-not-reply.fr'
    user['hashed_password'] = pwd
    user['admin'] = False
    user['type'] = 'registered'
    hashed = bcrypt.hashpw(user['hashed_password'], bcrypt.gensalt())
    user['hashed_password'] = hashed
    user.save()

    project = connection.Project()
    project['name'] = 'sample'
    project['owner'] = user
    project['users'].append({ 'user' : user, 'role' : 'myrole'})
    project.save()

    print "Api Key "+user['apikey']

