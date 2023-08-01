from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from .. import serializers


get_action = extend_schema(
    summary='Get actions',
    responses=serializers.ActionSerializer(many=True),
    description="""
       Returns all action registered in role model
       Path parameters:
        plugin_name(str): Only action for plugin 
        action_id(int): get specified action
       """,
    parameters=[
        OpenApiParameter(
            name='var',
            required=False,
            description='plugin_name or action_id',
            location=OpenApiParameter.PATH,
        ),
    ],
    examples=[
        OpenApiExample(
            name='All actions request',
            value=[
                {
                    "id": 1,
                    "name": "create",
                    "default_rule": False,
                    "plugin_name": "dtcd_workspaces"
                },
                {
                    "id": 2,
                    "name": "read",
                    "default_rule": True,
                    "plugin_name": "dtcd_workspaces"
                },
                {
                    "id": 3,
                    "name": "update",
                    "default_rule": False,
                    "plugin_name": "dtcd_workspaces"
                },
                {
                    "id": 4,
                    "name": "delete",
                    "default_rule": False,
                    "plugin_name": "dtcd_workspaces"
                },
                {
                    "id": 5,
                    "name": "move",
                    "default_rule": False,
                    "plugin_name": "dtcd_workspaces"
                }
            ],
            response_only=True,

        ),

    ]
)

update_action = extend_schema(
    summary='Change action default rule',
    request=serializers.ActionSerializer,
    responses=serializers.ActionSerializer,
    description="""
       Update action default rule 
       """,
    parameters=[
        OpenApiParameter(
            name='var',
            required=True,
            description='action_id',
            location=OpenApiParameter.PATH,
        ),
    ],
    examples=[
        OpenApiExample(
            name='Update default rule',
            value={
                "default_rule": True,
            },
            request_only=True,
        ),
    ],
)

get_auth_covered_class = extend_schema(
    responses=serializers.AuthCoveredClassSerializer,
    description="""
       Returns auth_covered_classes 
       """,
    parameters=[
        OpenApiParameter(
            name='plugin_name',
            location=OpenApiParameter.PATH,
        )
    ],
    examples=[
        OpenApiExample(
            name='Auth covered classes',
            value=[
                {
                    "id": 1,
                    "plugin": "dtcd_workspaces",
                    "class_import_str": "dtcd_workspaces.workspaces.directory_content.DirectoryContent"
                },
                {
                    "id": 2,
                    "plugin": "rolemodel_test",
                    "class_import_str": "rolemodel_test.models.SomePluginAuthCoveredModel"
                },
                {
                    "id": 3,
                    "plugin": "rolemodel_test",
                    "class_import_str": "rolemodel_test.models.SomePluginAuthCoveredModelUUID"
                }
            ],
            response_only=True,
        ),
    ],
)

get_groups = extend_schema(
    description="""
       Get group view set
       """,

    examples=[
        OpenApiExample(
            name='Get groups',
            value=[
                {
                    "id": 1,
                    "name": "creators",
                    "users": [
                        2,
                        3
                    ],
                    "roles": [
                        {
                            "id": 1,
                            "name": "creators",
                            "created_time": "2023-06-27T15:09:07.549348+03:00",
                            "modified_time": "2023-06-27T15:09:07.549375+03:00",
                            "permits": [
                                2
                            ],
                            "groups": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "ordinary_group1",
                    "users": [
                        5,
                        6,
                        4
                    ],
                    "roles": [
                        {
                            "id": 2,
                            "name": "ordinary_role1",
                            "created_time": "2023-06-27T15:09:08.967424+03:00",
                            "modified_time": "2023-06-27T15:09:08.967443+03:00",
                            "permits": [
                                4
                            ],
                            "groups": [
                                2
                            ]
                        }
                    ]
                },
            ],
            response_only=True,
        ),
    ],
)

add_users_to_group = extend_schema(
    responses=serializers.GroupSerializer,
    description="""
       Adds users with ids to group
       """,

    examples=[
        OpenApiExample(
            name='Add users example',
            value={
                'user_ids': [1, 2, 3, 4]
            },
            request_only=True,
        ),
    ],
)


remove_users_from_group = extend_schema(
    responses=serializers.GroupSerializer,
    description="""
       Delete users with ids from group
       """,

    examples=[
        OpenApiExample(
            name='Delete users d example',
            value={
                'user_ids': [3, 4]
            },
            request_only=True,
        ),
    ],
)


update_users_in_group = extend_schema(
    responses=serializers.GroupSerializer,
    description="""
       Ensure that users with ids  will be in group
       """,

    examples=[
        OpenApiExample(
            name='Update users group example',
            value={
                'user_ids': [3, 4]
            },
            request_only=True,
        ),
    ],
)

add_roles_to_group = extend_schema(
    responses=serializers.GroupSerializer,
    description="""
       Adds roles with ids to group
       """,

    examples=[
        OpenApiExample(
            name='Add roles example',
            value={
                'roles_ids': [1, 2, 3, 4]
            },
            request_only=True,
        ),
    ],
)


remove_roles_from_group = extend_schema(
    responses=serializers.GroupSerializer,
    description="""
       Delete roles with ids from group
       """,

    examples=[
        OpenApiExample(
            name='Delete roles from group example',
            value={
                'roles_ids': [3, 4]
            },
            request_only=True,
        ),
    ],
)


update_roles_in_group = extend_schema(
    responses=serializers.GroupSerializer,
    description="""
       Ensure that roles with ids  will be in group
       """,

    examples=[
        OpenApiExample(
            name='Update roles group example',
            value={
                'roles_ids': [3, 4]
            },
            request_only=True,
        ),
    ],
)

get_keychain_list = extend_schema(
    responses=serializers.KeyChainSerializer(many=True),
    description="""
    Returns all keychain for auth covered class
    """,
    examples=[
        OpenApiExample(
            name='Get keychains',
            value=
            [
                {
                    "id": "1",
                    "name": "root_access_zone_keychain",
                    "security_zone": 1,
                    "permits": [],
                    "auth_covered_objects": []
                },
                {
                    "id": "3",
                    "name": "keychain2",
                    "security_zone": 1,
                    "permits": [
                        4
                    ],
                    "auth_covered_objects": [
                        "test_workspace4",
                        "test_workspace5"
                    ]
                },
                {
                    "id": "2",
                    "name": "keychain1",
                    "security_zone": 1,
                    "permits": [
                        3
                    ],
                    "auth_covered_objects": [
                        "test_workspace2",
                        "test_workspace3",
                        "test_workspace1"
                    ]
                }
            ],
            response_only=True,
        ),
    ],
)

create_keychain = extend_schema(
    description="""
    Create keychain for auth covered class 
    """,
    examples=[
        OpenApiExample(
            name='Create keychain request',
            value={
                "security_zone": 1,
                "name": "keychain1",
                "auth_covered_objects": ["test_workspace1", "test_workspace2", "test_workspace3"]
            },
            request_only=True,
        ),
        OpenApiExample(
            name='Create keychain response',
            value={
                "id": 5,
                "permits": [],
                "auth_covered_objects": [
                    "test_workspace1",
                    "test_workspace2",
                    "test_workspace3"
                ],
                "security_zone": 1,
                "name": "keychain11"
            },
            response_only=True,
        ),
    ],
)

get_keychain = extend_schema(
    responses=serializers.KeyChainSerializer,
    description="""
    Return keychain with specified id
    """,
    examples=[
        OpenApiExample(
            name='Get keychain',
            value={
                "permits": [
                    4,
                    5
                ],
                "security_zone": 1,
                "id": "3",
                "name": "keychain2",
                "auth_covered_objects": [
                    "test_workspace4",
                    "test_workspace5"
                ]
            },
            response_only=True,
        ),
    ],
)

update_keychain = extend_schema(
    responses=serializers.KeyChainSerializer,
    description="""
    Update keychain with specified id
    """,
    examples=[
        OpenApiExample(
            name='Update keychain',
            value={
                "permits": [4],
                "security_zone": 1,
                "name": "keychain2",
                "auth_covered_objects": [
                    "test_workspace4",
                    "test_workspace5"
                ]
            },
            request_only=True,
        ),
        OpenApiExample(
            name='Update keychain response',
            value={
                "id": 3,
                "name": "keychain2",
                "permits": [
                    4
                ],
                "auth_covered_objects": [
                    "test_workspace4",
                    "test_workspace5"
                ],
                "security_zone": 1
            },
            response_only=True,
        ),

    ],
)

partial_update_keychain = extend_schema(
    responses=serializers.KeyChainSerializer,
    description="""
    Partial update keychain with specified id
    """,
    examples=[
        OpenApiExample(
            name='Update keychain permits',
            value={
                "permits": [4, 5],
            },
            request_only=True,
        ),
        OpenApiExample(
            name='Update keychain response',
            value={
                "id": 3,
                "name": "keychain2",
                "permits": [
                    4, 5
                ],
                "auth_covered_objects": [
                    "test_workspace4",
                    "test_workspace5"
                ],
                "security_zone": 1
            },
            response_only=True,
        ),

    ],
)

create_permits = extend_schema(
    description="""
    Create permit
    """,
    examples=[
        OpenApiExample(
            name='Create permit',
            value={
                "access_rules": [
                    {
                        "action": 3,
                        "rule": True,
                        "by_owner_only": True
                    },
                    {
                        "action": 5,
                        "rule": True,
                        "by_owner_only": True
                    },
                    {
                        "action": 1,
                        "rule": True
                    }
                ],
                "roles": [1]
            },
            request_only=True,
        ),
        OpenApiExample(
            name='Create permit response',
            value={
                "id": 6,
                "access_rules": [
                    {
                        "id": 12,
                        "action": 3,
                        "rule": True,
                        "by_owner_only": True
                    },
                    {
                        "id": 13,
                        "action": 5,
                        "rule": True,
                        "by_owner_only": True
                    },
                    {
                        "id": 14,
                        "action": 1,
                        "rule": True,
                        "by_owner_only": False
                    }
                ],
                "roles": [
                    1
                ],
                "keychain_ids": [],
                "security_zone_name": None,
                "created_time": "2023-08-01T11:02:50.343408+03:00",
                "modified_time": "2023-08-01T11:02:50.343427+03:00",
                "actions": [
                    1,
                    5,
                    3
                ]
            },
            response_only=True,
        ),

    ],
)

get_permit = extend_schema(
    description="""
    Get permit
    """,
    examples=[
        OpenApiExample(
            name='Get permit',
            value={
                "id": 6,
                "access_rules": [
                    {
                        "id": 12,
                        "action": 3,
                        "rule": True,
                        "by_owner_only": True
                    },
                    {
                        "id": 13,
                        "action": 5,
                        "rule": True,
                        "by_owner_only": True
                    },
                    {
                        "id": 14,
                        "action": 1,
                        "rule": True,
                        "by_owner_only": False
                    }
                ],
                "roles": [
                    1
                ],
                "keychain_ids": [],
                "security_zone_name": None,
                "created_time": "2023-08-01T11:02:50.343408+03:00",
                "modified_time": "2023-08-01T11:02:50.343427+03:00",
                "actions": [
                    1,
                    5,
                    3
                ]
            },
            response_only=True,
        ),
    ],
)

