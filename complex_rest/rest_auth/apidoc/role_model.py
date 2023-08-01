from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from .. import serializers


get_action_api_doc = extend_schema(
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
            name='plugin_name',
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name='action_id',
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

update_action_api_doc = extend_schema(
    summary='Change action default rule',
    request=serializers.ActionSerializer,
    responses=serializers.ActionSerializer,
    description="""
       Update action default rule 
       """,
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

auth_covered_action_api_doc = extend_schema(
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

get_groups_api_doc = extend_schema(
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
