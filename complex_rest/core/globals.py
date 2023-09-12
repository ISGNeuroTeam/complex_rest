import threading
from collections import defaultdict
from rest_auth.models import AnonymousUser
from rest_auth.models import User


class GlobalVars:
    """
    Class contains global variables. Variables are set by GlobalSetMiddleware.
    """
    _threadmap = defaultdict(dict)

    def __getitem__(self, item):
        return GlobalVars._threadmap[threading.get_ident()][item]

    def __setitem__(self, key, value):
        GlobalVars._threadmap[threading.get_ident()][key] = value

    @staticmethod
    def get_current_user() -> User:
        """
        Returns current user from global variables
        """
        glob_dict = GlobalVars._threadmap[threading.get_ident()]
        if 'user' not in glob_dict:
            return AnonymousUser()
        return glob_dict['user']

    @staticmethod
    def set_current_user(user: User):
        """
        Sets user to global variables
        """
        GlobalVars._threadmap[threading.get_ident()]['user'] = user

    @staticmethod
    def delete_all():
        """
        Deletes all global variables
        """
        try:
            del GlobalVars._threadmap[threading.get_ident()]
        except KeyError:
            pass


global_vars = GlobalVars()
