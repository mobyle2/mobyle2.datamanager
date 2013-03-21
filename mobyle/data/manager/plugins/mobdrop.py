import tempfile
# Include the Dropbox SDK libraries
import dropbox
from dropbox import client,rest,session

from yapsy.IPlugin import IPlugin

import logging

import mobyle.data.manager.plugins

from mobyle.common.config import Config
config = Config.config()

# Get your app key and secret from the Dropbox developer website
APP_KEY = config.get('app:main','drop_key')
APP_SECRET = config.get('app:main','drop_secret')

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
#sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

class MobDrop(IPlugin):
    '''Plugin to manage DropBox interactions'''
    
    
    def __init__(self):
        super(MobDrop, self).__init__()
        self.sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)


    def register(self):
        '''Register plugin with plugin manager (protocol and name)
        '''
        return ('dropbox','dropbox')

    def print_name(self):
        '''Print information name on plugin
        '''
        logging.info("DropBox data manager")

    def authorize(self):
        ''' Get authorization token from  DropBox
        '''
        request_token = self.sess.obtain_request_token()
        url = self.sess.build_authorize_url(request_token)
        return (request_token,url)

    def authorized(self,httpsession):
        ''' Check if application is authorized to upload/download files with plugin

        :param httpsession: HTTP Session
        :type httpsession: Pyramid HTTP session
        :return: Boolean, message
        '''
        if 'drop_access_token' not in httpsession:
            if 'drop_request_token' not in httpsession:
                (request_token,url) = self.authorize()
                httpsession['drop_request_token'] = request_token
                msg = 'Please authorize Mobyle application to access your DropBox account at url: <a href="'+url+'">'+url+'</a>, then try again the upload'
                return (False,msg)
            else:
                access_token = self.token(httpsession['drop_request_token'])
                httpsession['drop_request_token'] = None
                httpsession['drop_access_token'] =  access_token
        else:
            self.sess.set_token(httpsession['drop_access_token'].key,httpsession['drop_access_token'].secret)
        return (True,None)


    def token(self,request_token):
        access_token = self.sess.obtain_access_token(request_token)
        return access_token


    def upload(self,file):
        '''Plugin interface method to upload a file

        :param file: Path to the file to upload
        :type file: str
        '''
        f = open(file)
        from dropbox import client
        client = client.DropboxClient(self.sess)
        response = client.put_file('/'+file, f)


    def set_options(self,httpsession , options):
        options['drop_access_token'] = httpsession['drop_access_token']
        return options

    def download(self,file,options):
        '''Plugin interface method to download a file and create a new dataset

        :param file: Path to the remote file to download
        :type file: str
        :param options: context parameters
        :type options: list
        :return: tmp file path
        '''
        from dropbox import client
        self.sess.set_token(options['drop_access_token'].key,options['drop_access_token'].secret)
        client = client.DropboxClient(self.sess)
        logging.warn("DropBox - download request for "+file)
        folder_metadata = client.metadata('/')
        logging.warn("/ content "+str(folder_metadata))
        f, metadata = client.get_file_and_metadata(file)
        (out,file_path) = tempfile.mkstemp()
        output_file = open(file_path, 'wb')
        output_file.write(f.read())
        return file_path

