import json
from core.globals import global_vars
from rest.test import APITestCase, create_test_users, TransactionTestCase
from rest_auth.models import Group, User, Role, SecurityZone, Action, Plugin, Permit
from rest_auth.apps import on_ready_actions as rest_auth_on_ready_actions
from rolemodel_test.models import SomePluginAuthCoveredModel, PluginKeychain


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
        self.login('admin', 'admin')

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


class KeyChainApiTest(TransactionTestCase, APITestCase):
    auth_covered_object_class = 'rolemodel_test.models.SomePluginAuthCoveredModel'

    def setUp(self):
        self.admin, self.test_users = create_test_users(1)
        # create 2 groups
        self.admin_group = Group(name='admin')
        self.admin_group.save()

        self.admin.groups.add(self.admin_group)
        global_vars.set_current_user(self.admin)
        zone = SecurityZone(name='main_zone')
        zone.save()
        for _ in range(5):
            keychain = PluginKeychain()
            keychain.zone = zone
            for _ in range(5):
                auth_covered_object = SomePluginAuthCoveredModel()
                auth_covered_object.keychain = keychain

        self.login('admin', 'admin')

    def test_key_chain_object_list(self):
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/',
            format='json'
        )
        self.assertEquals(response.status_code, 200)
        keychain_list = response.data
        self.assertEquals(len(keychain_list), 5)

    def test_key_chain_object_retrieve(self):
        keychain_id = PluginKeychain.objects.all().first().id
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain_id}/',
            format='json'
        )
        self.assertEquals(response.status_code, 200)
        keychain = response.data
        auth_covered_objects_ids = keychain['auth_covered_objects']
        self.assertListEqual(auth_covered_objects_ids, ['1', '2', '3', '4', '5'])

    def test_key_chain_object_create(self):
        zone = SecurityZone(name='test_zone1')
        zone.save()
        new_auth_covered_objects_ids = list()
        for _ in range(5):
            auth_covered_object = SomePluginAuthCoveredModel()
            auth_covered_object = SomePluginAuthCoveredModel.objects.get(id=auth_covered_object.id)
            new_auth_covered_objects_ids.append(str(auth_covered_object.id))

        zone = SecurityZone(name='test_zone1')
        zone.save()
        response = self.client.post(
            f'/auth/keychains/{self.auth_covered_object_class}/',
            {
                'security_zone': zone.id,
                'auth_covered_objects': new_auth_covered_objects_ids,
            },
            format='json'
        )
        new_keychain_id = response.data['id']
        self.assertEquals(response.status_code, 201)
        for obj_id in new_auth_covered_objects_ids:
            obj = SomePluginAuthCoveredModel.objects.get(id=obj_id)
            self.assertEquals(obj.keychain.id, new_keychain_id)
            self.assertEquals(obj.keychain.zone.id, zone.id)

    def test_key_chain_object_update(self):
        keychain = PluginKeychain.objects.all().first()
        self.assertEquals(keychain.zone.name, 'main_zone')
        zone = SecurityZone(name='test_zone1')
        zone.save()
        new_auth_covered_objects_ids = list()
        for _ in range(5):
            auth_covered_object = SomePluginAuthCoveredModel()
            auth_covered_object = SomePluginAuthCoveredModel.objects.get(id=auth_covered_object.id)
            new_auth_covered_objects_ids.append(str(auth_covered_object.id))
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{str(keychain.id)}/',
        )
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        self.assertListEqual(auth_covered_objects_ids, ['1', '2', '3', '4', '5'])
        # replace security zone and keychains
        response = self.client.put(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
            {
                'security_zone': zone.id,
                'auth_covered_objects': new_auth_covered_objects_ids,
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertEqual(security_zone_id, zone.id)
        self.assertListEqual(auth_covered_objects_ids, new_auth_covered_objects_ids)
        # delete security zones and objects from keychain
        response = self.client.put(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
            {
                'security_zone': None,
                'auth_covered_objects': [],
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertIsNone(security_zone_id)
        self.assertListEqual(auth_covered_objects_ids, [])

    def test_key_chain_object_partial_update(self):
        keychain = PluginKeychain.objects.all().first()
        self.assertEquals(keychain.zone.name, 'main_zone')
        zone = SecurityZone(name='test_zone1')
        zone.save()
        new_auth_covered_objects_ids = list()
        for _ in range(5):
            auth_covered_object = SomePluginAuthCoveredModel()
            auth_covered_object = SomePluginAuthCoveredModel.objects.get(id=auth_covered_object.id)
            new_auth_covered_objects_ids.append(str(auth_covered_object.id))
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{str(keychain.id)}/',
        )
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        self.assertListEqual(auth_covered_objects_ids, ['1', '2', '3', '4', '5'])
        # replace security zone and keychains
        response = self.client.patch(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
            {
                'security_zone': zone.id,
                'auth_covered_objects': new_auth_covered_objects_ids,
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data

        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertEqual(security_zone_id, zone.id)
        self.assertListEqual(auth_covered_objects_ids, new_auth_covered_objects_ids)

        # delete security zones and objects from keychain
        response = self.client.patch(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
            {
                'security_zone': None,
                'auth_covered_objects': None,
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertEquals(security_zone_id, zone.id)

    def test_key_chain_object_delete(self):
        keychain_id = PluginKeychain.objects.all().first().id
        response = self.client.delete(
            f'/auth/keychains/{self.auth_covered_object_class}/{keychain_id}/',
        )
        self.assertEquals(response.status_code, 200)
        with self.assertRaises(PluginKeychain.DoesNotExist):
            PluginKeychain.objects.get(id=keychain_id)


class PermissionApiTest(TransactionTestCase, APITestCase):
    auth_covered_object_class = 'rolemodel_test.models.SomePluginAuthCoveredModel'

    def setUp(self):
        self.admin, self.test_users = create_test_users(1)
        # create 2 groups
        self.admin_group = Group(name='admin')
        self.admin_group.save()
        global_vars.set_current_user(self.admin)
        self.login('admin', 'admin')
        rest_auth_on_ready_actions()

    def test_create_permission(self):
        action_create = Action.objects.get(plugin__name='rolemodel_test', name='test.create')
        user = User.objects.get(username='test_user1')
        group = Group(name='test_group')
        group.save()
        role = Role(name='test_role')
        role.save()
        role.groups.add(group)
        user.groups.add(group)

        keychain = PluginKeychain()
        keychain.save()
        obj = SomePluginAuthCoveredModel()
        obj.keychain = keychain
        obj.save()

        response = self.client.post(
            f'/auth/permits/{self.auth_covered_object_class}/',
            {
                'access_rules': [
                    {
                        'action': action_create.id,
                        'rule': True,
                        'by_owner_only': False
                    }, ],
                'roles': [role.id, ],
                'keychain_ids': [str(keychain.id), ],


            },
            format='json'
        )
        self.assertEquals(response.status_code, 201)
        permit = Permit.objects.all().first()
        self.assertEquals(permit.roles.all().first().id, role.id)
        self.assertEquals(permit.keychain_ids, [str(keychain.id), ])


class AuthCoveredClassApiTest(TransactionTestCase, APITestCase):
    def setUp(self):
        self.admin, self.test_users = create_test_users(1)
        # create 2 groups
        self.admin_group = Group(name='admin')
        self.admin_group.save()
        global_vars.set_current_user(self.admin)
        self.login('admin', 'admin')
        rest_auth_on_ready_actions()

    def test_auth_covered_classes_list(self):
        response = self.client.get(
            f'/auth/auth_covered_classes/rolemodel_test/'
        )
        auth_covered_class = response.data[0]
        self.assertEquals(auth_covered_class['class_import_str'], 'rolemodel_test.models.SomePluginAuthCoveredModel')
