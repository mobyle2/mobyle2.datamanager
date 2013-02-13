# -*- coding: utf-8 -*-
from pyramid.config import Configurator

from pyramid.events import subscriber
from pyramid.events import NewRequest, BeforeRender, NewResponse
from pyramid.security import authenticated_userid


import pyramid_beaker
import pymongo

from hashlib import sha1
from random import randint

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include(pyramid_beaker)
    config.include('pyramid_mailer')

    db_uri = settings['db_uri']
    conn = pymongo.Connection(db_uri, safe=True)
    config.registry.settings['db_conn'] = conn
    db = conn[config.registry.settings['db_name']]

    from mobyle.common.config import Config
    mobyle_config = Config().config()
    for setting in settings:
      mobyle_config.set('app:main',setting,settings[setting])
    import mobyle.common.connection
    mobyle.common.connection.init_mongo(settings['db_uri'])
    #end initialization
    
    config.add_route('main', '/')

    config.add_route('upload_data','/data')
    config.add_route('upload_remote_data','/remotedata')

    config.add_route('login', '/login')
    config.add_route('logout','/logout')
    config.add_route('my','/my')
    config.add_route('my.json','/my.json')


    config.add_static_view('static', 'mobyle.data.manager:static', cache_max_age=3600)
    
    config.scan()

    return config.make_wsgi_app()



