# -*- coding: utf-8 -*-
from pyramid.view import view_config
#from pyramid.security import remember, authenticated_userid, forget

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.response import Response, FileResponse
from pyramid.settings import asbool

import json
import urllib
import re
import logging
import os
import pairtree
import tempfile
from copy import deepcopy

from bson import json_util

import mobyle.common
from mobyle.common.connection import connection
from mobyle.common.mobyleConfig import MobyleConfig
from mobyle.common.objectmanager import ObjectManager, AccessMode

from bson import ObjectId


from mobyle.data.manager.background import download, upload

from  mobyle.data.manager.pluginmanager import DataPluginManager

from mf.views import MF_EDIT, MF_READ

class Protocols:
    _BASE_PROTOCOLS = None

def get_protocols():
    """Return the list of allowed protocols"""
    if Protocols._BASE_PROTOCOLS is not None:
        return Protocols._BASE_PROTOCOLS
    Protocols._BASE_PROTOCOLS = []
    mob_config = MobyleConfig.get_current()
    allowed_protocols = mob_config['data']['remote']['allowed_protocols']
    if allowed_protocols:
        allowed_list = allowed_protocols.split(",")
        for protocol in allowed_list:
            Protocols._BASE_PROTOCOLS.append(protocol.strip()+"://")
    if mob_config['data']['local']['allowed_copy']:
        Protocols._BASE_PROTOCOLS.append('file://')
        Protocols._BASE_PROTOCOLS.append('symlink://')
    return Protocols._BASE_PROTOCOLS



@view_config(route_name='data_plugin_upload')
def data_plugin_upload(request):
    '''
    Manage the upload of a data using plugins
    '''
    httpsession = request.session
    #import mobyle.data.manager.plugins

    #TODO check I own the dataset

    options = {}
    try:
        uid = request.params.getone('id')
        options['protocol'] = request.params.getone('protocol')
        manager = ObjectManager()
        dataset = connection.ProjectData.find_one({"_id": ObjectId(uid)})
        options['id'] = uid
        #uid = dataset['uid']
        options['name'] = dataset['name']
        dfile = dataset.get_file_path()  + "/" + uid
        #dfile = manager.get_storage_path() + \
        #        '/' + pairtree.id2path(uid) + "/" + uid
    except Exception as e:
        logging.error("Wrong input paramerers: " + str(e))
        request.session.flash("Wrong input paramerers")
        values = my(request)
        return render_to_response('mobyle.data.webmanager:templates/my.mako',
                values, request=request)

    data_plugin_manager = DataPluginManager.get_manager()
    plugin = data_plugin_manager.getPluginByName(request.matchdict['plugin'])
    if plugin is None:
        return HTTPNotFound('No plugin ' + request.matchdict['plugin'])
    drop = plugin.plugin_object
    (authorized, msg) = drop.authorized(httpsession)
    if not authorized:
        request.session.flash(msg)
        values = my(request)
        return render_to_response('mobyle.data.webmanager:templates/my.mako',
                values, request=request)

    options = drop.set_options(request.session, options)
    use_delay = asbool(request.registry.settings['delay_background'])
    if use_delay:
        options['delay'] = True
        upload.delay(dfile, options)
    else:
        options['delay'] = False
        upload(dfile,options)
    request.session.flash('Upload to DropBox in progress')
    values = my(request)
    return render_to_response('mobyle.data.webmanager:templates/my.mako',
            values, request=request)


def get_auth_user(request):
    """
    Get user object from either session or apikey

    :param request: pyramid request object
    :type request: Request
    :return: a User object
    """
    user = None
    httpsession = request.session
    try:
        if "_id" in httpsession:
            user = connection.User.find_one({'_id': ObjectId(httpsession['_id'])})
        else:
            user = connection.User.find_one({'apikey': request.params.getone("apikey")})
    except Exception as e:
        logging.error("Could not match user:" + str(e))
    return user

def can_update_project(user, project):
    """
    Checks that user can add files to project

    :param user: Logged user
    :type user: User
    :param project: Project to update
    :type project: Project
    :return: bool
    """
    project_filter = project.my(MF_EDIT, None, user['email'])
    allowed = False
    mffilter = {}
    if project_filter is not None:
        mffilter['_id'] = project['_id']
        obj = connection.Project.find_one(mffilter)
        if obj is not None:
            allowed = True
    return allowed


def can_read_project(user, project):
    """
    Checks that user read elements of a project

    :param user: Logged user
    :type user: User
    :param project: Project to read
    :type project: Project
    :return: bool
    """
    project_filter = project.my(MF_READ, None, user['email'])
    allowed = False
    mffilter = {}
    if project_filter is not None:
        mffilter['_id'] = project['_id']
        obj = connection.Project.find_one(mffilter)
        if obj is not None:
            allowed = True
    return allowed

def can_read_dataset(user, data):
    """
    Checks that user can read a dataset in a project

    :param user: Logged user
    :type user: User
    :param data: ProjectData to read
    :type data: ProjectData
    :return: bool
    """
    if 'public' in data and data['public']:
        return True
    project = connection.Project.find_one({"_id": data['project']})
    if project is None:
        return False
    return can_read_project(user, project)

def can_update_dataset(user, data):
    """
    Checks that user can modify or delete a dataset in a project

    :param user: Logged user
    :type user: User
    :param data: ProjectData to update
    :type data: ProjectData
    :return: bool
    """
    project = connection.Project.find_one({"_id": data['project']})
    if project is None:
        return False
    return can_update_project(user, project)


@view_config(route_name='data_token', renderer='json')
def data_token(request):
    did = request.matchdict['uid']
    dataset = connection.ProjectData.find_one({"_id": ObjectId(did)})
    if dataset is None:
        return HTTPNotFound()

    user = get_auth_user(request)
    if not can_update_dataset(user, dataset):
        return HTTPForbidden()

    lifetime = 0
    try:
        lifetime = request.params.getone('lifetime')
    except Exception:
        lifetime = 3600 * 24
    file_path = []
    token = ObjectManager.get_token(did, file_path , AccessMode.READONLY,
                                    lifetime)
    return {'token': token}

@view_config(route_name='download')
def download(request):
    """
    Manage the download of a dataset for public datasets or user only datasets
    """
    data_uid = request.matchdict['uid']
    #file_path = ','.join(str(i) for i in request.matchdict['file'])
    dataset = connection.ProjectData.find_one({"_id": ObjectId(data_uid)})
    if dataset is None:
        raise HttpNotFound()
    if not dataset['public']:
        user = get_auth_user(request)
        if not user or not can_read_dataset(user,dataset):
            raise HTTPForbidden()
    file_path = os.path.join(dataset.get_file_path(),
                            dataset['data']['path'])
    if not os.path.exists(file_path):
        raise HTTPNotFound()
    logging.debug("request to download file "+file_path)
    mime_type = 'application/'+dataset['data']['format']
    response = FileResponse(file_path,
                                request=request,
                                content_type=str(mime_type))
    return response

@view_config(route_name='data_download', renderer='json')
def data_download(request):
    token = request.matchdict['token']
    file_path = ','.join(str(i) for i in request.matchdict['file'])
    #file_path = request.matchdict['file'].join('/')
    logging.debug("request to download path "+file_path+" for token " \
                  + token)
    data_token = connection.Token.find_one({"token": token})
    if data_token.check_validity(False):
        data_uid = data_token['data']['id']
        dataset = connection.ProjectData.find_one({"_id": ObjectId(data_uid)})
        # Get full path to the file
        file_path = os.path.join(dataset.get_file_path(), file_path)
        mime_type = 'application/'+dataset['data']['format']
        response = FileResponse(file_path,
                                request=request,
                                content_type=str(mime_type))
        return response

    else:
        raise HTTPForbidden()

@view_config(route_name='public.json',renderer='json')
def public_json(request):
    '''
    Get public datasets in JSON format
    '''
    datasets = []
    
    datafilter = { 'public': True }
    datafilter = add_filter(datafilter, request)

    projectdata = connection.ProjectData.find(datafilter)

    for data in projectdata:
        if data['status'] == 2:
            datasets.append(data)
    return Response(json.dumps(datasets,
                    default=json_util.default),content_type="application/json")


@view_config(route_name='public', renderer='mobyle.data.webmanager:templates/public.mako')
def public(request):
    '''
    View listing of public datasets
    '''
    # Datasets will be loaded asynchronously to avoid page loading time
    projects = connection.Project.find({},{'name': 1})
    projectsname = {}
    for project in projects:
        projectsname[str(project['_id'])] = project['name']
    return {'projectsname': projectsname}


@view_config(route_name='my.json', renderer='json')
def my_json(request):
    '''
    Get user datasets in JSON format
    '''
    try:
        datasets = []
        user = get_auth_user(request)
        if user:
            try:
                user_projects = connection.Project.find({"users": {"$elemMatch": {'user': user['_id']}}})
                projects = []
                for project in user_projects:
                    projects.append(project['_id'])

                dfilter = {"project" : {"$in": projects}}
                dfilter = add_filter(dfilter, request)
                projectdata = connection.ProjectData.find(dfilter)
                # TODO get user owned datasets
                #projectdata = connection.ProjectData.find()
            except Exception as e:
                logging.error("ProjectData error: " + str(e))
                return []

            for data in projectdata:
                datasets.append(data)
    except Exception:
        datasets = []
    return Response(json.dumps(datasets,
                        default=json_util.default),
                        content_type="application/json")

def add_filter(dfilter, request):
    '''
    Check if request requires a specific filter on datasets

    :param dfilter: pre-existing filter
    :type dfilter: dict
    :param request: Http pyramid request
    :type request: Pyramid Request
    :return: dict of filter
    '''
    try:
        key = request.params.getone('filter')
        value = request.params.getone(key)
        if key == 'project':
            value = ObjectId(value)
        if key == 'type' or key == 'format':
            key = 'data.'+key
        dfilter[key] = value

    except Exception:
        logging.debug("no filter applied")
    return dfilter



@view_config(route_name='my', renderer='mobyle.data.webmanager:templates/my.mako')
def my(request):
    '''
    View listing datasets for the current user
    '''
    user = {}
    projectdata = {}
    httpsession = request.session
    projectsname = {}
    user = get_auth_user(request)
    #if "_id" in httpsession:
    if user is not None:
        #user = connection.User.find_one({'_id': ObjectId(httpsession['_id'])})
        try:
            # TODO get data owned by  user
            user_projects = connection.Project.find({"users": {"$elemMatch": {'user': user['_id']}}})
            projects = []
            for project in user_projects:
                projects.append(project['_id'])
                projectsname[str(project['_id'])] = project['name']
            projectdata = connection.ProjectData.find({"project": {"$in": projects}})
        except Exception as e:
            logging.error("ProjectData error: " + str(e))
            return {'user': user, 'data': []}
    return {'user': user, 'data': projectdata, 'projectsname' : projectsname }


@view_config(route_name='logout', renderer='mobyle.data.webmanager:templates/index.mako')
def logout(request):
    '''
    Logout view
    '''
    httpsession = request.session
    if "_id" in httpsession:
        del httpsession['_id']
    user = {'last_name': None, 'first_name': None, 'apikey': None, 'projects':
    []}
    return {'user': user}


@view_config(route_name='login', renderer='mobyle.data.webmanager:templates/index.mako')
def login(request):
    '''
    Login view
    '''
    user = {'last_name': None, 'first_name': None, 'apikey': None, 'projects': []}
    try:
        httpsession = request.session
        if "_id" in httpsession:
            user = connection.User.find_one({'_id': ObjectId(httpsession['_id'])})
        else:
            user = connection.User.find_one({'apikey': request.params.getone("apikey")})
        httpsession["_id"] = str(user["_id"])
    except Exception as e:
        logging.error("error with api key: " + str(e))
    try:
        projects = []
        if "_id" in httpsession:
            user_projects = connection.Project.find({"users": {"$elemMatch": {'user': user['_id']}}})
            for up in user_projects:
                projects.append({"name": up["name"],"id": up["_id"]})
            user['projects'] = projects
    except Exception as e:
        logging.error("error with projects: " + str(e))
        user['projects'] = projects
    return {'user': user, 'protocols': get_protocols()}


def get_user(request):
    '''
    Return user information
    '''
    httpsession = request.session
    user = get_auth_user(request)
    if user is not None:
    #if "_id" in httpsession:
        #user = connection.User.find_one({'_id' : ObjectId(httpsession['_id'])  })
        projects = []
        try:
            user_projects = connection.Project.find({"users": {"$elemMatch": {'user': user['_id']}}})
            for up in user_projects:
                projects.append({"name": up["name"],"id": up["_id"]})
            user['projects'] = projects
        except Exception as e:
            logging.error("error with projects: " + str(e))
            user['projects'] = projects
        return user
    return {"first_name": "", "last_name": "", "projects": [], "apikey": ""}


@view_config(route_name='main', renderer='mobyle.data.webmanager:templates/index.mako')
def my_view(request):
    '''
    Base view, i.e. home
    '''
    uid = None
    try:
        uid = request.params.getone('id')
    except Exception:
        uid = None
    return {'user': get_user(request), 'uid': uid, 'protocols': get_protocols()}


@view_config(route_name='upload_remote_data', renderer='mobyle.data.webmanager:templates/index.mako')
def upload_remote_data(request):
    '''
    Manage the download of a remote data in the system
    '''
    manager = ObjectManager()
    data_plugin_manager = DataPluginManager.get_manager()

    options = {}
    try:
        options['rurl'] = request.params.getone('rurl')
    except Exception:
        options['rurl'] = None
    if options['rurl'] is None:
        #files = {}
        return {'user': get_user(request)}

    try:
        options['type'] = request.params.getone('type')
    except Exception:
        options['type'] = None

    try:
        options['format'] = request.params.getone('format')
    except Exception:
        options['format'] = 'auto'

    try:
        options['project'] = request.params.getone('project')
        user = get_auth_user(request)
        if user is None:
            raise HTTPForbidden()
        project = connection.Project.find_one({"_id": ObjectId(options['project'])})
        if project is None or not can_update_project(user, project):
            raise HttpForbidden()
    except Exception:
        options['project'] = None

    try:
        options['protocol'] = request.params.getone('protocol')
    except Exception:
        options['protocol'] = None

    # Try to protect against unexpected protocols
    if options['protocol'] not in DataPluginManager.supported_protocols and \
        options['protocol'] not in get_protocols():

        request.session.flash("Protocol not supported")
        return {'user': get_user(request)}

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


    #files = {}
    if options['id'] is None:
        new_dataset = manager.add(options['rurl'].replace('/','_'), options)
        if new_dataset is not None:
            options['id'] = str(new_dataset['_id'])

    # If http,ftp,scp i.e. base protocols, do not check plugins
    if options['protocol'] is not None and \
        options['protocol'] not in get_protocols():

        plugin = data_plugin_manager.getPluginByName(options['protocol'])
        if plugin is None:
            return HTTPNotFound('No plugin ' + request.matchdict['plugin'])
        drop = plugin.plugin_object
        (authorized, msg) = drop.authorized(request.session)
        if not authorized:
            request.session.flash(msg)
            values = my_view(request)
            return render_to_response('mobyle.data.webmanager:templates/index.mako', values, request=request)
         # Store session objects necessary for plugins
        options = drop.set_options(request.session, options)

    httpsession = request.session
    if "_id" in httpsession:
        options['user_id'] = httpsession['_id']
    use_delay = asbool(request.registry.settings['delay_background'])
    if use_delay:
        options['delay'] = True
        download.delay(options['rurl'], options)
    else:
        options['delay'] = False
        download(options['rurl'], options)
    request.session.flash('File download request in progress')
    return {'user': get_user(request), 'protocols': get_protocols()}


@view_config(route_name='data', renderer='json')
def data(request):
    '''
    Get or delete a dataset
    '''
    user = get_auth_user(request)
    did = request.matchdict['uid']
    dataset = connection.ProjectData.find_one({"_id": ObjectId(did)})
    if dataset is None:
        return HTTPNotFound()

    if request.method == 'DELETE':
        if not can_update_dataset(user, dataset):
            return HTTPForbidden()

        infile = request.matchdict['uid']
        ObjectManager.delete(infile)
        return {}
    if request.method == 'GET':
        if not can_read_dataset(user, dataset):
            return HTTPForbidden()
        projectname = connection.Project.find_one({"_id": dataset['project']})
        dataset['project'] = projectname['name']
        dataset['rootpath'] = ObjectManager.get_relative_file_path(dataset['_id'])
        return Response(json.dumps({'dataset': dataset, 'history':
            ObjectManager.history(did)}, default=json_util.default))


@view_config(route_name='upload_data', renderer='json')
def upload_data(request):
    '''
    Upload a file
    '''
    options = {}
    try:
        options['project'] = request.params.getone('project')
        user = get_auth_user(request)
        if user is None:
            raise HTTPForbidden()
        project = connection.Project.find_one({"_id": ObjectId(options['project'])})
        if project is None or not can_update_project(user, project):
            raise HttpForbidden()

    except Exception as e:
        logging.error(str(e))
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
        options['format'] = request.params.getone('format')
    except Exception:
        options['format'] = 'auto'

    try:
        options['type'] = request.params.getone('type')
    except Exception:
        options['type'] = None

    files = handle_file_upload(request, options)
    return {'files': files}

MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 5000000000  # bytes
REJECT_FILE_TYPES = re.compile('application/(fake|test)')
THUMBNAIL_MODIFICATOR = '=s80'  # max width / height
EXPIRATION_TIME = 300  # seconds


def validate(infile):
    '''
    Validate the input file
    '''
    if infile['size'] < MIN_FILE_SIZE:
        infile['error'] = 'File is too small'
    elif infile['size'] > MAX_FILE_SIZE:
        infile['error'] = 'File is too big'
    elif  REJECT_FILE_TYPES.match(infile['type']):
        infile['error'] = 'Filetype not allowed'
    else:
        return True
    return False


def get_file_size(infile):
    '''
    Get the size of the file
    '''
    infile.seek(0, 2)  # Seek to the end of the file
    size = infile.tell()  # Get the position of EOF
    infile.seek(0)  # Reset the file position to the beginning
    return size


def write_blob(data, info, options):
    '''
    Write file content and store it as a dataset
    '''
    if not options['project']:
        return None

    (out, file_path) = tempfile.mkstemp()
    output_file = open(file_path, 'wb')

    output_file.write(data)
    output_file.close()
    if options['uncompress']:
        logging.debug('Should uncompress data')
    if options['group']:
        logging.debug('Should group data')

    dataset = ObjectManager.store(info['name'], file_path, options)
    if dataset['status'] == ObjectManager.UNCOMPRESS:
        # delay decompression
        from mobyle.data.manager.background import uncompress
        newoptions = deepcopy(options)
        newoptions['id'] = str(dataset['_id'])
        newoptions['format'] = options['original_format']
        use_delay = options['delay']
        if use_delay:
            newoptions['delay'] = True
            uncompress.delay(dataset.get_file_path()+"/"+str(dataset['_id']), newoptions)
        else:
            newoptions['delay'] = False
            uncompress(dataset.get_file_path()+"/"+str(dataset['_id']), newoptions)

    os.remove(file_path)
    return file_path


def handle_file_upload(request, options):
    '''
    Handle the upload of a file from web interface
    '''
    results = []
    blob_keys = []
    options['delay'] = asbool(request.registry.settings['delay_background'])
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
                    '/' + options['project'] + '/' +\
                    urllib.quote(result['name'].encode('utf-8'), '')
        results.append(result)
    return results

