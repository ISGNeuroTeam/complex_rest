import json
from core.globals import global_vars
from rest.test import APITestCase, create_test_users
from rest_auth.models import Group, User, Role


class GroupApiTest(APITestCase):
    def setUp(self):
        self.admin, self.test_users = create_test_users(10)
        # create 2 groups
        self.admin_group = Group(name='admin')
        self.admin_group.save()

        self.ordinary_group = Group(name='ordinary_group')
        self.ordinary_group.save()
        # create 5 roles in ordinary group
        for i in range(5):
            r = Role(name=f'test_role{i}')
            r.save()
            self.ordinary_group.roles.add(r)

        for user in self.test_users:
            user.groups.add(self.ordinary_group)

        self.admin.groups.add(self.admin_group)

        global_vars.set_current_user(self.admin)

    def test_get(self):
        response = self.client.get('/auth/groups/')
        self.assertEquals(len(response.data), 2, 'Two groups were created')

    def test_get_group(self):
        response = self.client.get('/auth/groups/1/')
        self.assertEquals(response.data['name'], 'admin', 'Group with id = 1 is admin group')
        self.assertListEqual(response.data['users'], [1, ])

    def test_put_group(self):
        response = self.client.put('/auth/groups/1/', data={
            'name': 'admin',
            'users': [
                2, 3
            ]
        })
        self.assertEquals(response.status_code, 200, 'Put response success')
        response = self.client.get('/auth/groups/1/')
        self.assertListEqual(response.data['users'], [2, 3], 'Second and third users in admin group')

    def test_post_group(self):
        response = self.client.post('/auth/groups/', data={
            'name': 'new_group', 'users': [2, 3, 4, 5]
        })
        self.assertEquals(response.status_code, 201, 'Group  created successfully')

        response = self.client.get('/auth/groups/3/')
        self.assertEquals(response.data['name'], 'new_group')
        self.assertListEqual(response.data['users'], [2, 3, 4, 5])

    def test_post_group_without_users(self):
        response = self.client.post('/auth/groups/', data={
            'name': 'new_group',
        })
        self.assertEquals(response.status_code, 201, 'Group  created successfully')

        response = self.client.get('/auth/groups/3/')
        self.assertEquals(response.data['name'], 'new_group')
        self.assertListEqual(response.data['users'], [])

    def test_add_users(self):
        response = self.client.post(
            '/auth/groups/1/users/add_users/',
            {
                'user_ids': [2, 3, 4]
            }, format='json'
        )
        self.assertEquals(response.status_code, 200, 'Users successfully added to admin group')
        response = self.client.get('/auth/groups/1/users/')
        self.assertEquals(response.status_code, 200, 'User list request successful')
        self.assertEquals(len(response.data), 4, '4 users in admin group')

    def test_remove_users(self):
        response = self.client.delete(
            f'/auth/groups/{self.ordinary_group.pk}/users/remove_users/',
            {"user_ids": [2, 3, 4]},
            format='json'
        )
        self.assertEquals(response.status_code, 200)
        response = self.client.get(
            f'/auth/groups/{self.ordinary_group.pk}/users/'
        )
        self.assertEquals(response.status_code, 200, 'User list request successful')
        self.assertEquals(len(response.data), 7, '7 users in ordinary group')

    def test_add_roles(self):
        response = self.client.post(
            '/auth/groups/1/roles/add_roles/',
            {
                'roles_ids': [2, 3, 4]
            }, format='json'
        )
        self.assertEquals(response.status_code, 200, 'Roles successfully added to admin group')
        response = self.client.get('/auth/groups/1/roles/')
        self.assertEquals(response.status_code, 200, 'Role list request successful')
        self.assertEquals(len(response.data), 3, '3 roles in admin group')

    def test_remove_roles(self):
        response = self.client.delete(
            f'/auth/groups/{self.ordinary_group.pk}/roles/remove_roles/',
            {"roles_ids": [2, 3, 4]},
            format='json'
        )
        self.assertEquals(response.status_code, 200)
        response = self.client.get(
            f'/auth/groups/{self.ordinary_group.pk}/roles/'
        )
        self.assertEquals(response.status_code, 200, 'Role list request successful')
        self.assertEquals(len(response.data), 2, '2 roles in ordinary group')