# -*- coding: utf-8 -*-
from pyramid.config import Configurator

from pyramid.events import subscriber
from pyramid.events import NewRequest, BeforeRender, NewResponse
from pyramid.security import authenticated_userid


import pyramid_beaker
import pymongo

from hashlib import sha1
from random import randint

def data_include(config):
    config.add_route('main', '/')

    config.add_route('upload_data','/data')
    config.add_route('upload_remote_data','/remotedata')

    config.add_route('login', '/login')
    config.add_route('logout','/logout')
    config.add_route('my','/my')
    config.add_route('my.json','/my.json')
    config.add_route('data','/data/{uid}')

    config.add_static_view('static', 'mobyle.data.webmanager:static', cache_max_age=3600)

    config.add_route('data_plugin','/plugin')
    config.add_route('data_plugin_upload','/plugin/{plugin}/upload')
    config.add_route('data_plugin_download','/plugin/{plugin}/download')


def objectmanager_include(config):
    from  mobyle.data.manager.objectmanager import ObjectManager
    objectmanager = ObjectManager()
    config.add_static_view(name='download', path=objectmanager.get_storage_path())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include(pyramid_beaker)
    config.include('pyramid_mailer')


    from mobyle.common.config import Config
    mobyle_config = Config().config()
    for setting in settings:
      mobyle_config.set('app:main',setting,settings[setting])
    #end initialization

    config.include(data_include, route_prefix='/data-manager')

    config.scan()

    from mobyle.common.users import User
    from mobyle.common.project import Project

    config.include(objectmanager_include, route_prefix='/data-manager')

    return config.make_wsgi_app()



