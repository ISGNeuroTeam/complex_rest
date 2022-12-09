from rest_framework import serializers


class ResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=('success', 'error',))
    status_code = serializers.IntegerField()
    error = serializers.CharField()
