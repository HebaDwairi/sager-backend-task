from rest_framework import serializers
from .models import Drone, DroneData

class DroneSerializer(serializers.ModelSerializer):
  class Meta:
    model = Drone
    fields = "__all__"


class DangerousDroneSerializer(serializers.ModelSerializer):
  class Meta:
    model = Drone
    fields = ['serial_number', 'is_dangerous', 'dangerous_reason']