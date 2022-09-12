from rest.test import APITestCase, create_test_users
from rest_auth.models import Group, User


class GroupApiTest(APITestCase):
    def setUp(self):
        self.admin, self.test_users = create_test_users(10)
        # create 2 groups
        self.admin_group = Group(name='admin')
        self.admin_group.save()

        self.ordinary_group = Group(name='ordinary_group')
        self.ordinary_group.save()

        for user in self.test_users:
            user.groups.add(self.ordinary_group)

        self.admin.groups.add(self.admin_group)

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
