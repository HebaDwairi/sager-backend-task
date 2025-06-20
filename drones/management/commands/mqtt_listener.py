from django.utils import timezone
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from drones.models import Drone, OSDData
from django.contrib.gis.geos import Point
import json


class Command(BaseCommand):
  def handle(self, *args, **options):
    def on_connect(client, userdata, flags, reason_code, properties):
      if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
      else:
        print("Connected with result code", reason_code)
        client.subscribe("thing/product/+/osd")
    

    def on_message(client, userdata, message):
      data = json.loads(message.payload)
      serial_number = message.topic.split("/")[2]

      longitude = data['longitude']
      latitude = data['latitude']
      height = data['height']
      speed = data['horizontal_speed']
      location = Point(longitude, latitude)

      drone, created = Drone.objects.update_or_create(
          serial_number=serial_number,
          defaults={
              'last_seen': timezone.now(),
              'last_location': location,
              'last_height': height,
              'last_speed': speed,
          }
      )

      OSDData.objects.create(
        drone=drone,
        location = location,
        latitude = latitude,
        longitude = longitude,
        height = height,
        horizontal_speed = speed,
        raw_data = data
      )
      
    
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("mosquitto", 1883, 60)
    mqttc.loop_forever()