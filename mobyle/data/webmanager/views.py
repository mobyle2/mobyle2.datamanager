# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.security import remember, authenticated_userid, forget

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import  render_view_to_response

import json
import urllib
import bcrypt
import re
import logging
import os
import pairtree
import tempfile

from bson import json_util

import mobyle.common
from mobyle.common.connection import connection
import mobyle.data.manager.objectmanager
from mobyle.data.manager.objectmanager import ObjectManager,FakeData

from bson import ObjectId


from mobyle.data.manager.background import download,upload

from  mobyle.data.manager.pluginmanager import DataPluginManager


base_protocols = ['http://','ftp://','scp://']

@view_config(route_name='data_plugin_upload')
def data_plugin_aupload(request):
    httpsession = request.session
    import mobyle.data.manager.plugins
    
    options = {}
    try:
      id = request.params.getone('id')
      options['protocol'] = request.params.getone('protocol')
      manager = ObjectManager()
      dataset = connection.FakeData.find_one({ "_id" : ObjectId(id)})
      options['id'] = id
      uid = dataset['uid']
      options['name'] = dataset['name']
      file = manager.get_storage_path()+'/'+pairtree.id2path(uid)+"/"+uid
    except Exception as e:
        logging.error("Wrong input paramerers: "+str(e))
        request.session.flash("Wrong input paramerers")
        values = my(request)
        return render_to_response('mobyle.data.webmanager:templates/my.mako',values,request=request)

    dataPluginManager = DataPluginManager.get_manager()
    plugin = dataPluginManager.getPluginByName(request.matchdict['plugin'])
    if plugin is None:
        return HTTPNotFound('No plugin '+request.matchdict['plugin']) 
    drop = plugin.plugin_object
    (authorized , msg) =  drop.authorized(httpsession)
    if not authorized:
        request.session.flash(msg)
        values = my(request)
        return render_to_response('mobyle.data.webmanager:templates/my.mako',values,request=request)

    options = drop.set_options(request.session, options)
    upload.delay(file,options)
    request.session.flash('Upload to DropBox in progress')
    values = my(request)
    return render_to_response('mobyle.data.webmanager:templates/my.mako',values,request=request)
    



@view_config(route_name='my.json', renderer='json')
def my_json(request):
    try:
        datasets = []
        user = connection.User.find_one({'apikey' : request.params.getone("apikey")  })
        if user:
            try:
                fakedata = connection.FakeData.find()
            except Exception as e:
                logging.error("Fakedata error: "+str(e))
                return []

            for data in fakedata:
                datasets.append(data)
    except Exception:
        datasets = []
    return json.dumps( datasets , default=json_util.default)



@view_config(route_name='my', renderer='mobyle.data.webmanager:templates/my.mako')
def my(request):
    user = {}
    fakedata = {}
    httpsession = request.session
    if "_id" in httpsession:
        user = connection.User.find_one({'_id' : ObjectId(httpsession['_id'])  })
        try:
            fakedata = connection.FakeData.find()
        except Exception as e:
            logging.error("Fakedata error: "+str(e))
            return { 'user' : user, 'data' : []}
    return { 'user' : user, 'data' : fakedata}

@view_config(route_name='logout', renderer='mobyle.data.webmanager:templates/index.mako')
def logout(request):
    httpsession = request.session
    if "_id" in httpsession:
        del httpsession['_id']
    user = { 'last_name' : None, 'first_name' : None, 'apikey' : None, 'projects' : [] }
    return { 'user' : user }

@view_config(route_name='login', renderer='mobyle.data.webmanager:templates/index.mako')
def login(request):
    user = { 'last_name' : None, 'first_name' : None, 'apikey' : None, 'projects' : [] }
    try:
        httpsession = request.session
        if "_id" in httpsession:
            user = connection.User.find_one({'_id' : ObjectId(httpsession['_id'])  })
        else:
            user = connection.User.find_one({'apikey' : request.params.getone("apikey")  })
        httpsession["_id"] = str(user["_id"])
    except Exception as e:
        logging.error("error with api key: "+str(e))
    try:
        projects = []
        if "_id" in httpsession:
            user_projects = connection.Project.find({ "users" : { "$elemMatch":{ 'user.$id' :  user['_id']}}})
            for up in user_projects:
                projects.append(up["name"])
            user['projects'] = projects
    except Exception as e:
        logging.error("error with projects: "+str(e))
        user['projects'] = projects
    return { 'user' : user }

def get_user(request):
    httpsession = request.session
    if "_id" in httpsession:
        user = connection.User.find_one({'_id' : ObjectId(httpsession['_id'])  })
        projects = []
        try:
            user_projects = connection.Project.find({ "users" : { "$elemMatch":{ 'user.$id' :  user['_id']}}})
            for up in user_projects:
                projects.append(up["name"])
            user['projects'] = projects
        except Exception as e:
            logging.error("error with projects: "+str(e))
            user['projects'] = projects
        return user
    return { "first_name" : "", "last_name" : "", "projects" : [], "apikey" : "" }

@view_config(route_name='main', renderer='mobyle.data.webmanager:templates/index.mako')
def my_view(request):
    uid = None
    try:
        uid = request.params.getone('id')
    except Exception:
        uid = None
    return { 'user' : get_user(request), 'uid' : uid }

@view_config(route_name='upload_remote_data', renderer='mobyle.data.webmanager:templates/index.mako')
def upload_remote_data(request):
    manager = ObjectManager()
    dataPluginManager = DataPluginManager.get_manager()

    options = {}
    try:
      options['rurl'] = request.params.getone('rurl')
    except Exception:
      options['rurl'] = None
    if options['rurl'] is None:
        files = {}
        return { 'user' : get_user(request) }

    try:
      options['type'] = int(request.params.getone('type'))
    except Exception:
      options['type'] = 0

    try:
      options['project'] = request.params.getone('project')
    except Exception:
      options['project'] = None

    try:
      options['protocol'] = request.params.getone('protocol')
    except Exception:
      options['protocol'] = None
      
    # Try to protect against unexpected protocols
    if options['protocol'] not in DataPluginManager.supported_protocols and options['protocol'] not in base_protocols:
        request.session.flash("Protocol not supported")
        return { 'user' : get_user(request) }

    try:
      options['id'] = request.params.getone('id')
    except Exception:
      options['id'] = None

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


    files = {}
    if options['id'] is None:
        options['id'] = manager.add(options['rurl'],options)
        
    # If http,ftp,scp i.e. base protocols, do not check plugins
    if options['protocol'] is not None and options['protocol'] not in base_protocols:    
        plugin = dataPluginManager.getPluginByName(options['protocol'])
        if plugin is None:
            return HTTPNotFound('No plugin '+request.matchdict['plugin']) 
        drop = plugin.plugin_object
        (authorized , msg) =  drop.authorized(request.session)
        if not authorized:
            request.session.flash(msg)
            values = my_view(request)
            return render_to_response('mobyle.data.webmanager:templates/index.mako',values,request=request)
         # Store session objects necessary for plugins
        options = drop.set_options(request.session, options)
        
    download.delay(options['rurl'],options)
    request.session.flash('File download request in progress')
    return { 'user' : get_user(request) }

@view_config(route_name='data', renderer='json')
def data(request):
    if request.method == 'DELETE':
        file = request.matchdict['uid']
        manager = ObjectManager()
        manager.delete(file)
        return {}
    if request.method == 'GET':
        id = request.matchdict['uid']
        dataset = connection.FakeData.find_one({ "_id" : ObjectId(id)})
        manager = ObjectManager()
        #return json.dumps( { 'dataset' : dataset, 'history' : manager.history(id) } , default=json_util.default) 
        return Response(json.dumps( { 'dataset' : dataset, 'history' : manager.history(id) } , default=json_util.default))
        


@view_config(route_name='upload_data', renderer='json')
def upload_data(request):
    options = {}
    try:
      options['project'] = request.params.getone('project')
    except Exception:
      options['project'] = None

    try:
      options['id'] = request.params.getone('id')
    except Exception:
      options['id'] = None
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

    try:
      options['type'] = int(request.params.getone('type'))
    except Exception:
      options['type'] = 0

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
    
     (out,file_path) = tempfile.mkstemp() 
     #upload_dir = os.path.join(Config.config().get('app:main','upload_dir')+'/',options['project'])
     #file_path = os.path.join(upload_dir, info['name'])
     output_file = open(file_path, 'wb')

     output_file.write(data)
     output_file.close()
     if options['uncompress']:
       logging.error('Should uncompress data')
     if options['group']:
       logging.error('Should group data')

     mngr = ObjectManager()
     mngr.store(info['name'],file_path,options)
     os.remove(file_path)
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

