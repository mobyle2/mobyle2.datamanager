from pyftpdlib.authorizers import AuthenticationFailed

import mobyle.common
from mobyle.common.connection import connection

class MobyleAuthorizer(object):
    """Basic "mobyle" authorizer class

    """

    read_perms = "elr"
    write_perms = "adfmwM"


    def validate_authentication(self, username, password, handler):
        """Raises AuthenticationFailed if supplied username and
        password don't match the stored credentials, else return
        None.
        """
        user = connection.User.find_one({ 'email' : str(username) , 'apikey' : str(password)})
        if user is None:
            msg = "Authentication failed."
            raise AuthenticationFailed(msg)

    def has_user(self, username):
        user = connection.User.find_one({ 'email' : str(username) , 'apikey' : str(password)})
        if user is not None:
            return True
        else:
            return False

    def get_home_dir(self, username):
        """Return the user's home directory.
        Since this is called during authentication (PASS),
        AuthenticationFailed can be freely raised by subclasses in case
        the provided username no longer exists.
        """
        user = connection.User.find_one({ 'email' : str(username) })
        return str(user['_id'])

    def impersonate_user(self, username, password):
        """Impersonate another user (noop).

        It is always called before accessing the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to change the
        current user.
        """

    def terminate_impersonation(self, username):
        """Terminate impersonation (noop).

        It is always called after having accessed the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to switch back
        to the original user.
        """

    def get_perms(self, username):
        return "elradfmw"

    def has_perm(self, username, perm, path=None):
        return perm in self.get_perms(username)

    def get_msg_login(self, username):
        """Return the user's login message."""
        return "Welcome"

    def get_msg_quit(self, username):
        """Return the user's quitting message."""
        return "Bye bye"

    def _check_permissions(self, username, perm):
        warned = 0

    def _issubpath(self, a, b):
        """Return True if a is a sub-path of b or if the paths are equal."""
        p1 = a.rstrip(os.sep).split(os.sep)
        p2 = b.rstrip(os.sep).split(os.sep)
        return p1[:len(p2)] == p2
