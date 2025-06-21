from django.utils import timezone
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from drones.models import Drone, DroneData
from django.contrib.gis.geos import Point
import json

def classify_danger(height, speed):
  is_dangerous = False
  dangerous_reason = None

  reasons = []

  if height is not None and height > 500:
    reasons.append('Flying higher than 500 meters')

  if speed is not None and speed > 10:
    reasons.append('Moving faster than 10 m/s')

  if reasons:
    is_dangerous = True
    dangerous_reason = ' and'.join(reasons)

  return is_dangerous, dangerous_reason

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
      is_dangerous, dangerous_reason = classify_danger(height, speed)

      drone, created = Drone.objects.update_or_create(
          serial_number=serial_number,
          defaults={
              'last_seen': timezone.now(),
              'last_location': location,
              'last_height': height,
              'last_speed': speed,
              'is_dangerous': is_dangerous,
              'dangerous_reason': dangerous_reason
          }
      )

      DroneData.objects.create(
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