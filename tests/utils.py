from typing import List
from rest_auth.models import User


def create_test_users(ordinary_users: int = 1) -> (User, List[User]):
    """
    Creates and returns admin user and several ordinary users with names test_user1, test_user2 ...
    Args:
        ordinary_users: number of ordinary users
    """

    admin_user = User(username='admin', is_staff=True, is_active=True)
    admin_user.set_password('admin')
    admin_user.save()
    test_users = []
    for i in range(ordinary_users):
        test_user = User(username=f'test_user{i+1}')
        test_user.set_password('user11q2w3e4r5t')
        test_user.save()
        test_users.append(test_user)
    return admin_user, test_users
