from  pyftpdlib.filesystems import AbstractedFS
import os
import time
from pyftpdlib._compat import PY3, u, unicode

import mobyle.common
from mobyle.common.connection import connection
from mobyle.common.project import ProjectData, Project

from mobyle.common.objectmanager import ObjectManager

from bson import ObjectId

from pyftpdlib.filesystems import _months_map, FilesystemError

try:
    from stat import filemode as _filemode  # PY 3.3
except ImportError:
    from tarfile import filemode as _filemode

import logging


class MobyleFileSystem(AbstractedFS):
    """Represents the Mobyle filesystem.

    """

    def __init__(self, root, cmd_channel):
        """
         - (str) root: the user "real" home directory (e.g. '/home/user')
         - (instance) cmd_channel: the FTPHandler class instance
        """
        super(MobyleFileSystem, self).__init__(root, cmd_channel)
        self._uid = root
        self._root = u('/')

    def validpath(self, path):
            # validpath was used to check symlinks escaping user home
            # directory; this is no longer necessary.
            return True

    def chdir(self, path):
        # No change possible for the moment
        #self._cwd = path
        if path == '/':
            path = u(path)
        self._cwd = u(self.fs2ftp(path))
        logging.debug("chdir to " + self._cwd)

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
        elts = path.split('/')
        try:
            #user = connection.User.find_one({ '_id' : ObjectId(self._uid) })
            # User root
            #if len(elts) == 1:
            if path == '/':
                return True
            # User project
            elif len(elts) == 2:
                return True
            # Dataset directory
            elif len(elts) == 3:
                return True
            # Next, should check if a sub dataset
        except Exception:
            return False
        return False

    def get_list_dir(self, path):
        """"Return an iterator object that yields a directory listing
        in a form suitable for LIST command.
        """
        logging.debug("cur dir is " + self._cwd)
        logging.debug("get_list_dir: " + path)
        if self.isdir(path):
            logging.debug("list a directory")
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
            logging.debug("list a file: " + path)
            # Should of course get fakedatas of user only
            data = connection.ProjectData.find_one({'_id': ObjectId(path)})

            return self.format_list(path, [data])

    def listdir(self, path):
        """List the content ie all fakedatas."""

        files = []
        # Should of course get fakedatas/projects of user only
        elts = path.split('/')
        logging.debug("listdir: path= " + str(elts))
        if path == '/':
            # Root dir, list projects
            projects = connection.Project.find({"users": {"$elemMatch": {'user': ObjectId(self._uid)}}})
            for project in projects:
                files.append({'type' : 'project', 'elt' : project})
        else:
            if len(elts)==2:
                project = elts[1].split('_')
                projectdata = connection.ProjectData.find({"project": ObjectId(project[0])})
                for data in projectdata:
                    files.append({'type' : 'datasets', 'elt' : data})
            else:
                dataset = elts[2].split('_')
                dataset = connection.ProjectData.fetch_one({"_id": ObjectId(dataset[0])})
                if 'value' in dataset['data']:
                    for subdata in dataset['data']['value']:
                        files.append({'type' : 'files', 'elt': { '_id':
                        str(dataset['_id']), 'name' : subdata['path']}})
                else:
                    files.append({'type' : 'files', 'elt': { '_id' :
                    str(dataset['_id']), 'name' : dataset['data']['path']}})

        logging.debug("list files " + str(files))
        return files

    def getsize(self, path):
        paths = path.split('/')
        filename = paths[2]
        filename = filename.split('_')[0]
        fakedata = connection.ProjectData.find_one({'_id': filename})
        if fakedata is not None:
            return fakedata['size']
        return None

    def getmtime(self, path):
        paths = path.split('/')
        paths = path.split('/')
        filename = paths[2]
        filename = filename.split('_')[0]
        mngr = ObjectManager()
        filename = mngr.get_file_path(filename)
        return os.path.getmtime(filename)

    def realpath(self, path):
        return path

    def lexists(self, path):
        return True

    def open(self, filename, mode):
        """Open a file returning its handler."""
        paths = filename.split('/')
        filename = paths[3]
        datasetid = filename.split('_')[0]
        filename = filename.split('_')[1]
        filename = os.path.join(ObjectManager.get_file_path(datasetid),filename)
        logging.debug("## open " + filename)
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
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        SIX_MONTHS = 180 * 24 * 60 * 60
        #readlink = getattr(self, 'readlink', None)
        now = time.time()
        for basename in listing:
            if basename['type'] is 'files':
                try:
                    mngr = ObjectManager()
                    st = self.lstat(os.path.join(mngr.get_file_path(
                    basename['elt']['_id']), basename['elt']['name']))
                    import stat
                    size = st[stat.ST_SIZE]
                except (OSError, FilesystemError):
                    if ignore_err:
                        continue
                    raise
                #size = basename['data']['size']  # file size
                perms = _filemode(st.st_mode)  # permissions
            if basename['type'] is 'project' or basename['type'] is 'datasets':
                # This is a project, fake a directory
                size = 0
                st = self.lstat(os.path.realpath(__file__))
                basename['_id'] = str(basename['elt']['_id'])
                perms = "drwxrwxrwx"
            nlinks = st.st_nlink  # number of links to inode
            if not nlinks:  # non-posix system, let's use a bogus value
                nlinks = 1
            size = st.st_size  # file size
            mtime = timefunc(st.st_mtime)

            uname = "mobyle"
            gname = "mobyle"

            # if modification time > 6 months shows "month year"
            # else "month hh:mm";  this matches proftpd format, see:
            # http://code.google.com/p/pyftpdlib/issues/detail?id=187
            if (now - st.st_mtime) > SIX_MONTHS:
                fmtstr = "%d  %Y"
            else:
                fmtstr = "%d %H:%M"
            try:
                mtimestr = "%s %s" % (_months_map[mtime.tm_mon],
                                      time.strftime(fmtstr, mtime))
            except ValueError:
                # It could be raised if last mtime happens to be too
                # old (prior to year 1900) in which case we return
                # the current time as last mtime.
                mtime = timefunc()
                mtimestr = "%s %s" % (_months_map[mtime.tm_mon],
                                      time.strftime("%d %H:%M", mtime))

            # formatting is matched with proftpd ls output
            line = "%s %3s %-8s %-8s %8s %s %s\r\n" % \
                (perms, nlinks, uname, gname, size, mtimestr,
                    str(basename['elt']['_id']) + "_" + basename['elt']['name'])
            logging.debug("out list: " + line)
            yield line.encode('utf8', self.cmd_channel.unicode_errors)
