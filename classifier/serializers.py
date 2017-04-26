from rest_framework import serializers
from classifier.models import Classification


class ClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classification
        fields = ('user', 'data', 'result', 'date', 'ip_address')
