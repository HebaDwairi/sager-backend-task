
import ssl
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
import json
from ...services import DroneService
from decouple import config

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
      DroneService.process_drone_message(serial_number=serial_number, data=data)
      print(data)
      
    broker = config('MQTT_BROKER_HOST')
    port = int(config('MQTT_BROKER_PORT'))
    username = config('MQTT_BROKER_USERNAME')
    password = config('MQTT_BROKER_PASSWORD')

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.tls_set(tls_version=ssl.PROTOCOL_TLS)
    mqttc.username_pw_set(username, password)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    

    mqttc.connect(broker, port, 60)
    print(broker, port)
    mqttc.loop_forever()