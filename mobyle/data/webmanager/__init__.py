# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.request import Response
import pyramid_beaker


def data_include(config):
    config.add_route('main', '/')

    config.add_route('upload_data', '/data')
    config.add_route('upload_remote_data', '/remotedata')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('my', '/my')
    config.add_route('my.json', '/my.json')
    config.add_route('public', '/public')
    config.add_route('public.json', '/public.json')
    config.add_route('projects', '/projects')
    config.add_route('oauth_auth', '/oauth/v2/authorize')
    config.add_route('oauth_access', '/oauth/v2/token')
    config.add_route('data', '/data/{uid}')
    config.add_route('data_edit', '/data/{uid}/edit')
    config.add_route('data_token', '/data/{uid}/token')
    config.add_route('data_upload', '/data/{uid}/upload')
    config.add_route('data_download', '/data-download/{token}/*file')

    config.add_static_view('static',
                            'mobyle.data.webmanager:static',
                            cache_max_age=3600)

    config.add_route('data_plugin', '/plugin')
    config.add_route('data_plugin_upload', '/plugin/{plugin}/upload')
    config.add_route('data_plugin_download', '/plugin/{plugin}/download')

    from mobyle.common import connection
    from mf.dashboard import Dashboard
    Dashboard.set_connection(connection.connection)
    from mobyle.common.service_terms import ServiceTypeTerm
    from mobyle.common.service import Service
    from mobyle.common.mobyleConfig import MobyleConfig
    Dashboard.add_dashboard([ServiceTypeTerm, Service], config)

    from bson import json_util
    from bson.objectid import ObjectId
    import datetime
    from pyramid.renderers import JSON
    # automatically serialize bson ObjectId to Mongo extended JSON
    json_renderer = JSON()

    def objectId_adapter(obj, request):
        return json_util.default(obj)

    def datetime_adapter(obj, request):
        return json_util.default(obj)

    json_renderer.add_adapter(ObjectId, objectId_adapter)
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)


def objectmanager_include(config):
    from  mobyle.common.objectmanager import ObjectManager
    config.add_route('download', '/download/{uid}/*file')
    ObjectManager()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include(pyramid_beaker)
    config.include('pyramid_mako')
    config.include('pyramid_mailer')

    from mobyle.common.config import Config
    mobyle_config = Config().config()
    for setting in global_config:
        mobyle_config.set('app:main', setting, global_config[setting])
    for setting in settings:
        mobyle_config.set('app:main', setting, settings[setting])
    #end initialization

    config.include(data_include, route_prefix='/data-manager')

    config.scan()

    from mobyle.common.users import User
    from mobyle.common.project import Project

    config.include(objectmanager_include, route_prefix='/data-manager')

    #return config.make_wsgi_app()
    from wsgicors import CORS
    return CORS(config.make_wsgi_app(), headers="*", methods="*",
                                        maxage="180", origin="*")



