
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from drones.models import Drone, DroneData, NoFlyZone
from django.contrib.gis.geos import Point
import json
from ...services import process_drone_message

class Command(BaseCommand):
  def handle(self, *args, **options):
    def on_connect(client, userdata, flags, reason_code, properties):
      if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
      else:
        print("Connected with result code", reason_code)
        client.subscribe("thing/product/+/osd")
    

    def on_message(client, userdata, message):
      try:
        data = json.loads(message.payload)
      except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from MQTT message on topic {message.topic}: {e}. Payload: {message.payload.decode()}")
        return
      
      serial_number = message.topic.split("/")[2]
      process_drone_message(serial_number=serial_number, data=data)
      
    
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("mosquitto", 1883, 60)
    mqttc.loop_forever()