from rest_framework import serializers

class AIRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True)