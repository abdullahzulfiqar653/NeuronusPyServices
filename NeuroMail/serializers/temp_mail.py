from rest_framework import serializers


class TempEmailFakeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    inbox = serializers.ListField(child=serializers.JSONField())
