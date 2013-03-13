# http://code.google.com/p/pyftpdlib/wiki/Tutorial#4.0_-_Customizing_your_FTP_server

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


import logging

"""
FTP server accessing the Mobyle datasets owned or accessible by a user.
For the moment it manages only single/simple datasets (not a datasets containing other ones, like a blastdb or a dir with files)
It also takes all datasets, not just the user ones.

FTP PUT and DELETE are not implemented yet, only GET

"""

def main():
    from mobyle.common.config import Config
    mobyle_config = Config('/Users/osallou/Development/NOSAVE/mobyle2/web/datamanager/src/mobyle2.datamanager/development.ini').config()
    #mobyle_config = Config().config()

    from mobyle.data.ftp.mobyleauthorizer import MobyleAuthorizer
    from mobyle.data.ftp.mobylefilesystem import MobyleFileSystem

    from mobyle.common.users import User
    from mobyle.common.project import Project

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = MobyleAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    # anonymous user

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.abstracted_fs = MobyleFileSystem

    # Define a customized banner (string returned when client connects)
    handler.banner = "Mobyle ftp server."

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    #handler.masquerade_address = '151.25.42.11'
    #handler.passive_ports = range(60000, 65535)

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    address = ('', 2121)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()

if __name__ == '__main__':
    main()
