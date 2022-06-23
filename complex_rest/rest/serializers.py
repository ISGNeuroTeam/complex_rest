from rest_framework import serializers


class ResponseSerializer(serializers.Serializer):
    success = serializers.ChoiceField(choices=('success', 'error',))
    status_code = serializers.IntegerField()
    error = serializers.CharField()
