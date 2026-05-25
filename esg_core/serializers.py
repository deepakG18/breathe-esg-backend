from rest_framework import serializers
from .models import ActivityRecord, IngestionRun

class IngestionRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionRun
        fields = '__all__'

class ActivityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRecord
        fields = '__all__'