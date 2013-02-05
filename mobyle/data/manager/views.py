# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.security import remember, authenticated_userid, forget

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.response import Response

import json
import urllib
import bcrypt
import re
import logging
import os

from pyramid.httpexceptions import HTTPFound

@view_config(route_name='my', renderer='mobyle.data.manager:templates/my.mako')
def my(request):
    return {}

@view_config(route_name='login', renderer='mobyle.data.manager:templates/index.mako')
def login(request):
    user = { "name" : "osallou" , "projects" : [ 'project1', 'project2' ], "apikey" : "1234" }
    return { 'user' : user }


@view_config(route_name='main', renderer='mobyle.data.manager:templates/index.mako')
def my_view(request):
    #user = { "name" : "osallou" , "projects" : [ 'project1', 'project2' ] }
    #return { 'user' : user }
    return { 'user' : { "name" : "", "projects" : [], "apikey" : "" } }


@view_config(route_name='upload_data', renderer='json')
def upload_data(request):
    logging.error('I should be connected and I should check that I own the project')
    if request.method == 'DELETE':
        file = request.params.getone('key')
        os.remove(file)
        return {}

    options = {}
    try:
      options['project'] = request.params.getone('project')
    except Exception:
      options['project'] = None
    try:
      if request.params.getone('uncompress'):
        options['uncompress'] = True
    except Exception:
      options['uncompress'] = False

    try:
      if request.params.getone('group'):
        options['group'] = True
    except Exception:
      options['group'] = False


    files = handle_file_upload(request,options)
    return { 'files' : files }

MIN_FILE_SIZE = 1 # bytes
MAX_FILE_SIZE = 5000000000 # bytes
REJECT_FILE_TYPES = re.compile('application/(fake|test)')
THUMBNAIL_MODIFICATOR = '=s80' # max width / height
EXPIRATION_TIME = 300 # seconds

def validate(file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        elif  REJECT_FILE_TYPES.match(file['type']):
            file['error'] = 'Filetype not allowed'
        else:
            return True
        return False
    
def get_file_size(file):
        file.seek(0, 2) # Seek to the end of the file
        size = file.tell() # Get the position of EOF
        file.seek(0) # Reset the file position to the beginning
        return size

def write_blob(data, info, options):
     if not options['project']:
       return None
     upload_dir = os.path.join('/tmp/ftp/',options['project'])
     file_path = os.path.join(upload_dir, info['name'])
     output_file = open(file_path, 'wb')

     # Finally write the data to the output file
     #input_file = info['file']
     #input_file.seek(0)
     #while 1:
     #    data = input_file.read(2<<16)
     #    if not data:
     #        break
     #    output_file.write(data)
     output_file.write(data)
     output_file.close()
     if options['uncompress']:
       logging.error('Should uncompress data')
     if options['group']:
       logging.error('Should group data')

     return file_path

def handle_file_upload(request,options):

        results = []
        blob_keys = []
        for name, fieldStorage in request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = re.sub(r'^.*\\', '',
                fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = get_file_size(fieldStorage.file)
            if validate(result):
                blob_key = str(
                    write_blob(fieldStorage.value, result, options)
                )
                blob_keys.append(blob_key)
                result['delete_type'] = 'DELETE'
                result['delete_url'] = request.host_url +\
                    '/data?key=' + urllib.quote(blob_key, '')
                if not 'url' in result:
                    result['url'] = request.host_url +\
                        '/' + options['project'] + '/' + urllib.quote(
                            result['name'].encode('utf-8'), '')
            results.append(result)
        return results

