from  pyftpdlib.filesystems import AbstractedFS
import os
import time
import tempfile
from pyftpdlib._compat import PY3, u, unicode, property

from mobyle.data.manager.objectmanager import FakeData

from bson import ObjectId

from pyftpdlib.filesystems import _months_map

import logging

class MobyleFileSystem(AbstractedFS):
    """Represents the Mobyle filesystem.

    """


    def validpath(self, path):
            # validpath was used to check symlinks escaping user home
            # directory; this is no longer necessary.
            return True

    def chdir(self, path):
        # No change possible for the moment
        self._cwd = self._cwd

    def mkdir(self, path):
        # Not possible
        return False

    def rmdir(self, path):
        # Not possible
        return False

    def isfile(self, path):
        return True

    def islink(self, path):
        return False

    def isdir(self, path):
        """If path is a user id, then it is root dir"""
        import mobyle.common
        mobyle.common.session.register([FakeData])
        try:
            user = mobyle.common.session.User.find_one({ '_id' : ObjectId(path) })
            return True
        except Exception:
            return False
        return False

    def get_list_dir(self, path):
        """"Return an iterator object that yields a directory listing
        in a form suitable for LIST command.
        """
        assert isinstance(path, unicode), path
        logging.warn("get_list_dir: "+path)
        if self.isdir(path):
            listing = self.listdir(path)
            try:
                listing.sort()
            except UnicodeDecodeError:
                # (Python 2 only) might happen on filesystem not
                # supporting UTF8 meaning os.listdir() returned a list
                # of mixed bytes and unicode strings:
                # http://goo.gl/6DLHD
                # http://bugs.python.org/issue683592
                pass
            return self.format_list(path, listing)
        # if path is a file or a symlink we return information about it
        else:
            import mobyle.common
            mobyle.common.session.register([FakeData])
            # Should of course get fakedatas of user only
            fakedata = mobyle.common.session.FakeData.find_one({ 'uid' : path })
             
            return self.format_list(basedir, [fakedata])

    def listdir(self, path):
        """List the content ie all fakedatas."""

        import mobyle.common
        mobyle.common.session.register([FakeData])
        # Should of course get fakedatas of user only
        fakedata = mobyle.common.session.FakeData.find()
        files = []
        for data in fakedata:
            #files.append(data['uid'])
            if 'uid' in data:
                files.append(data)
        logging.warn("list files "+str(files))
        return files

    def getsize(self,path):
        import mobyle.common
        mobyle.common.session.register([FakeData])
        paths = path.split('/') 
        fakedata = mobyle.common.session.FakeData.find_one( {'uid' : path[1]})
        if fakedata is not None:
            return fakedata['size']
        return None

    def getmtime(self,path):
        import mobyle.common
        mobyle.common.session.register([FakeData])
        paths = path.split('/')
        fakedata = mobyle.common.session.FakeData.find_one( {'uid' : path[1]})
        #return fakedata['_id'].getTimestamp()
        # for the moment return current date
        paths = path.split('/')
        filename = paths[1]
        fakedata = mobyle.common.session.FakeData.find_one( {'uid' : filename})
        from mobyle.common.config import Config
        config = Config().config()
        filename = config.get("app:main","store")+"/pairtree_root/"+fakedata['path']
        return os.path.getmtime(filename)


    def realpath(self, path):
        return path

    def lexists(self, path):
        return True

    def open(self, filename, mode):
        """Open a file returning its handler."""
        import mobyle.common
        mobyle.common.session.register([FakeData])
        paths = filename.split('/')
        filename = paths[1]
        fakedata = mobyle.common.session.FakeData.find_one( {'uid' : filename})
        from mobyle.common.config import Config
        config = Config().config()
        filename = config.get("app:main","store")+"/pairtree_root/"+fakedata['path']
        logging.warn("## open "+filename)
        return open(filename, mode)

    def format_list(self, basedir, listing, ignore_err=True):
        """Return an iterator object that yields the entries of given
        directory emulating the "/bin/ls -lA" UNIX command output.

         - (str) basedir: the absolute dirname.
         - (list) listing: the names of the entries in basedir
         - (bool) ignore_err: when False raise exception if os.lstat()
         call fails.

        On platforms which do not support the pwd and grp modules (such
        as Windows), ownership is printed as "owner" and "group" as a
        default, and number of hard links is always "1". On UNIX
        systems, the actual owner, group, and number of links are
        printed.

        This is how output appears to client:

        -rw-rw-rw-   1 owner   group    7045120 Sep 02  3:47 music.mp3
        drwxrwxrwx   1 owner   group          0 Aug 31 18:50 e-books
        -rw-rw-rw-   1 owner   group        380 Sep 02  3:40 module.py
        """
        assert isinstance(basedir, unicode), basedir
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        SIX_MONTHS = 180 * 24 * 60 * 60
        readlink = getattr(self, 'readlink', None)
        now = time.time()
        for basename in listing:
            if not PY3:
                try:
                    file = os.path.join(basedir, basename['uid'])
                except UnicodeDecodeError:
                    # (Python 2 only) might happen on filesystem not
                    # supporting UTF8 meaning os.listdir() returned a list
                    # of mixed bytes and unicode strings:
                    # http://goo.gl/6DLHD
                    # http://bugs.python.org/issue683592
                    file = os.path.join(bytes(basedir), bytes(basename['uid']))
                    if not isinstance(basename['uid'], unicode):
                        basename = unicode(basename, 'utf8')
            else:
                file = os.path.join(basedir, basename['uid'])

            perms = ""  # permissions
            size = basename['size']  # file size
            uname = ""
            gname = ""
            #mtime = timefunc(basename['_id'].getTimestamp())
            from datetime import datetime
            mtime = datetime.now()
            
            # if modification time > 6 months shows "month year"
            # else "month hh:mm";  this matches proftpd format, see:
            # http://code.google.com/p/pyftpdlib/issues/detail?id=187
            fmtstr = "%Y %m %d %H:%M"
            try:
                mtimestr = "%s" % (mtime.strftime(fmtstr))
            except ValueError:
                # It could be raised if last mtime happens to be too
                # old (prior to year 1900) in which case we return
                # the current time as last mtime.
                mtime = timefunc()
                mtimestr = "%s %s" % (_months_map[mtime.tm_mon],
                                      time.strftime("%d %H:%M", mtime))

            # formatting is matched with proftpd ls output
            line = "%s %s %-8s %-8s %8s %s %s\r\n" % (perms, basename['name'], uname, gname,
                                                       size, mtimestr, basename['uid'])
            yield line.encode('utf8', self.cmd_channel.unicode_errors)
