from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from . import serializers


login_api_doc = extend_schema(
    summary='login',
    request=serializers.AccessTokenSerializer,
    responses=serializers.TokenResponseSerializer,
    description="""
       Takes user login and password, returns user access token
       Sets cookie 'auth_token' with value 'Bearer <token>'
       """,
    examples=[
        OpenApiExample(
            name='Login request',
            value={
                "login": "admin",
                "password": "admin"
            },
            request_only=True,

        ),
        OpenApiExample(
            name="Success response",
            value={
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjU2MDE1NjQ3LCJpYXQiOjE2NTU5NzI0NDcsImp0aSI6ImNkNTlmMDgxYzM5YzQ5OTBhNGU3NWU1NzM2NzYxNDQ0IiwiZ3VpZCI6IjMxNjk5OWFmLWU3NTctNDE2ZC1hZjQ2LTliNDJhNDY5ZjYwNiIsImxvZ2luIjoiYWRtaW4ifQ.xyJrmq7dSCnV3pnFFKUjj_jf4Md1rCb9pcFIq-61ZWE",
                "status": "success",
                "status_code": 200,
                "error": ""
            },
            response_only=True
        ),
        OpenApiExample(
            name='Login failed',
            value={
                "detail": "No active account found with the given credentials",
                "status_code": 401,
                "status": "error",
                "error": "Unauthorized"
            },
            response_only=True
        )
    ]
)

logout_api_doc = extend_schema(

    summary='logout',
    description="logout by removing http only cookie",
    responses={
        200: OpenApiResponse(
            response=serializers.LogoutResponseSerializer,
            description='User logged out'
        )

    },
    examples=[
        OpenApiExample(
            name='Success response',
            value={
                "message": "admin logged out",
                "status": "success",
                "status_code": 200,
                "error": ""
            },
            response_only=True
        ),
    ]
)
