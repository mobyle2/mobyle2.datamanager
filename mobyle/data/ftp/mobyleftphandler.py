from  pyftpdlib.handlers import FTPHandler
import logging


class MobyleFTPHandler(FTPHandler):
    """Represents the Mobyle FTP Handler.

    """

    def __init__(self, conn, server, ioloop=None):
        super(MobyleFTPHandler, self).__init__(conn, server, ioloop)


    def on_file_sent(self, file):
        """Called every time a file has been succesfully sent.
        "file" is the absolute name of the file just being sent.
        """
        logging.debug("File sent: "+file)
        

    def on_file_received(self, file):
        """Called every time a file has been succesfully received.
        "file" is the absolute name of the file just being received.
        """
        logging.debug("File received: "+file)

