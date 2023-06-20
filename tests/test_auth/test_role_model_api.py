import json
from collections import defaultdict
from core.globals import global_vars
from rest.test import APITestCase, create_test_users, TransactionTestCase
from rest_auth.models import Group, User, Role, SecurityZone, Action, Plugin, Permit
from rest_auth.apps import on_ready_actions as rest_auth_on_ready_actions
from rolemodel_test.models import SomePluginAuthCoveredModel, PluginKeychain, SomePluginAuthCoveredModelUUID


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
    auth_covered_class_import_str = 'rolemodel_test.models.SomePluginAuthCoveredModel'
    auth_covered_class = SomePluginAuthCoveredModel

    def setUp(self):
        self.admin, self.test_users = create_test_users(1)
        # create 2 groups
        self.admin_group = Group(name='admin')
        self.admin_group.save()

        self.admin.groups.add(self.admin_group)
        global_vars.set_current_user(self.admin)
        zone = SecurityZone(name='main_zone')
        zone.save()
        self.test_auth_covered_object_ids = defaultdict(set)
        for i in range(5):
            keychain = self.auth_covered_class.keychain_model()
            keychain.name = f'test_keychaon_{i}'
            keychain.zone = zone

            for _ in range(5):
                auth_covered_object = self.auth_covered_class()
                keychain.add_auth_object(auth_covered_object)
                self.test_auth_covered_object_ids[keychain.auth_id].add(str(auth_covered_object.auth_id))

        self.login('admin', 'admin')

    def test_key_chain_object_list(self):
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/',
            format='json'
        )
        self.assertEquals(response.status_code, 200)
        keychain_list = response.data
        self.assertEquals(len(keychain_list), 5)

    def test_key_chain_object_retrieve(self):
        keychain_id = self.auth_covered_class.keychain_model.objects.all().first().id
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain_id}/',
            format='json'
        )
        self.assertEquals(response.status_code, 200)
        keychain = response.data
        auth_covered_objects_ids = keychain['auth_covered_objects']
        self.assertSetEqual(set(auth_covered_objects_ids), self.test_auth_covered_object_ids[keychain_id])

    def test_key_chain_object_create(self):
        zone = SecurityZone(name='test_zone1')
        zone.save()
        new_auth_covered_objects_ids = list()
        for _ in range(5):
            auth_covered_object = self.auth_covered_class()
            auth_covered_object = self.auth_covered_class.objects.get(id=auth_covered_object.id)
            new_auth_covered_objects_ids.append(str(auth_covered_object.id))

        zone = SecurityZone(name='test_zone1')
        zone.save()
        response = self.client.post(
            f'/auth/keychains/{self.auth_covered_class_import_str}/',
            {
                'security_zone': zone.id,
                'name': 'test_name',
                'auth_covered_objects': new_auth_covered_objects_ids,
            },
            format='json'
        )
        new_keychain_id = response.data['id']
        self.assertEquals(response.status_code, 201)
        for obj_id in new_auth_covered_objects_ids:
            obj = self.auth_covered_class.objects.get(id=obj_id)
            self.assertEquals(obj.keychain.id, new_keychain_id)
            self.assertEquals(obj.keychain.zone.id, zone.id)
            self.assertEquals(obj.keychain.name, 'test_name')

    def test_key_chain_object_update(self):
        keychain = self.auth_covered_class.keychain_model.objects.all().first()
        self.assertEquals(keychain.zone.name, 'main_zone')
        zone = SecurityZone(name='test_zone1')
        zone.save()
        new_auth_covered_objects_ids = list()
        for _ in range(5):
            auth_covered_object = self.auth_covered_class()

            auth_covered_object = self.auth_covered_class.objects.get(id=auth_covered_object.id)
            new_auth_covered_objects_ids.append(auth_covered_object.auth_id)
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{str(keychain.id)}/',
        )
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']

        self.assertSetEqual(set(auth_covered_objects_ids), set(self.test_auth_covered_object_ids[keychain.auth_id]))
        # replace security zone and keychains
        response = self.client.put(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
            {
                'security_zone': zone.id,
                'auth_covered_objects': new_auth_covered_objects_ids,
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertEqual(security_zone_id, zone.id)
        self.assertSetEqual(set(auth_covered_objects_ids), set(new_auth_covered_objects_ids))
        # delete security zones and objects from keychain
        response = self.client.put(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
            {
                'security_zone': None,
                'auth_covered_objects': [],
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertIsNone(security_zone_id)
        self.assertListEqual(auth_covered_objects_ids, [])

    def test_key_chain_object_partial_update(self):
        keychain = self.auth_covered_class.keychain_model.objects.all().first()
        self.assertEquals(keychain.zone.name, 'main_zone')
        zone = SecurityZone(name='test_zone1')
        zone.save()
        new_auth_covered_objects_ids = list()
        for _ in range(5):
            auth_covered_object = self.auth_covered_class()
            auth_covered_object = self.auth_covered_class.objects.get(id=auth_covered_object.id)
            new_auth_covered_objects_ids.append(str(auth_covered_object.id))
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{str(keychain.id)}/',
        )
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        self.assertSetEqual(set(auth_covered_objects_ids), self.test_auth_covered_object_ids[keychain.id])
        # replace security zone and keychains
        response = self.client.patch(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
            {
                'security_zone': zone.id,
                'auth_covered_objects': new_auth_covered_objects_ids,
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data

        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertEqual(security_zone_id, zone.id)
        self.assertSetEqual(set(auth_covered_objects_ids), set(new_auth_covered_objects_ids))

        # delete security zones and objects from keychain
        response = self.client.patch(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
            {
                'security_zone': None,
                'auth_covered_objects': None,
            },
            format='json'
        )
        response = self.client.get(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain.id}/',
        )
        # check that security zone and keychain updated
        self.assertEquals(response.status_code, 200)
        keychain_data = response.data
        auth_covered_objects_ids = keychain_data['auth_covered_objects']
        security_zone_id = keychain_data['security_zone']
        self.assertEquals(security_zone_id, zone.id)

    def test_key_chain_object_delete(self):
        keychain_id = self.auth_covered_class.keychain_model.objects.all().first().id
        response = self.client.delete(
            f'/auth/keychains/{self.auth_covered_class_import_str}/{keychain_id}/',
        )
        self.assertEquals(response.status_code, 200)
        with self.assertRaises(self.auth_covered_class.keychain_model.DoesNotExist):
            self.auth_covered_class.keychain_model.objects.get(id=keychain_id)


class KeyChainApiTestUUID(KeyChainApiTest):
    auth_covered_class_import_str = 'rolemodel_test.models.SomePluginAuthCoveredModelUUID'
    auth_covered_class = SomePluginAuthCoveredModelUUID


class PermissionApiTest(TransactionTestCase, APITestCase):
    auth_covered_object_class_import_str = 'rolemodel_test.models.SomePluginAuthCoveredModel'
    auth_covered_class = SomePluginAuthCoveredModel

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

        keychain = self.auth_covered_class.keychain_model()
        keychain.save()
        obj = self.auth_covered_class()
        keychain.add_auth_object(obj)
        obj.save()

        response = self.client.post(
            f'/auth/permits/{self.auth_covered_object_class_import_str}/',
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

    def test_update_permission(self):
        self.test_create_permission()
        action_2 = Action.objects.get(plugin__name='rolemodel_test', name='test.protected_action1')
        permit = Permit.objects.all().first()
        role = Role(name='test_role_update')
        role.save()
        response = self.client.put(
            f'/auth/permits/{self.auth_covered_object_class_import_str}/{permit.id}/',
            {
                'access_rules': [
                    {
                        'action': action_2.id,
                        'rule': False,
                        'by_owner_only': False
                    }, ],
                'roles': [role.id, ],
                'keychain_ids': [],
            },
            format='json'
        )
        self.assertEquals(permit.actions.all().first().name, 'test.protected_action1')
        self.assertListEqual(permit.keychain_ids, [])
        self.assertEquals(permit.roles.all().first().id, role.id)

    def test_partial_update(self):
        self.test_create_permission()
        action_2 = Action.objects.get(plugin__name='rolemodel_test', name='test.protected_action1')
        permit = Permit.objects.all().first()
        role = Role.objects.get(name='test_role')
        response = self.client.patch(
            f'/auth/permits/{self.auth_covered_object_class_import_str}/{permit.id}/',
            {
                'access_rules': [
                    {
                        'action': action_2.id,
                        'rule': False,
                        'by_owner_only': False
                    }, ],
            },
            format='json'
        )
        # check that updated only actions
        self.assertEquals(permit.actions.all().first().name, 'test.protected_action1')
        self.assertEquals(len(permit.keychain_ids), 1)
        self.assertEquals(permit.roles.all().first().id, role.id)

        # remove keychains
        response = self.client.patch(
            f'/auth/permits/{self.auth_covered_object_class_import_str}/{permit.id}/',
            {
                'keychain_ids': []
            },
            format='json'
        )
        self.assertEquals(len(permit.keychain_ids), 0)

    def test_delete(self):
        self.test_create_permission()
        permit = Permit.objects.all().first()
        response = self.client.delete(
            f'/auth/permits/{self.auth_covered_object_class_import_str}/{permit.id}/',
        )
        self.assertEquals(Permit.objects.all().count(), 0)


class PermissionApiTestUUID(PermissionApiTest):
    auth_covered_object_class_import_str = 'rolemodel_test.models.SomePluginAuthCoveredModelUUID'
    auth_covered_class = SomePluginAuthCoveredModelUUID


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
