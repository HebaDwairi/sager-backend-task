from rest_framework import serializers
from .models import Drone, DroneData

class DroneSerializer(serializers.ModelSerializer):
  class Meta:
    model = Drone
    fields = "__all__"

class FlightPathSerializer(serializers.ModelSerializer):
  class Meta:
    model = DroneData
    fields = ['longitude', 'latitude', 'timestamp']