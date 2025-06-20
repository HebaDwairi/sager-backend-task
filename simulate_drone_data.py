import paho.mqtt.publish as publish
import time
import json
import string
import random
import argparse



class SimulatedDrone:
  def __init__(self, serial):
    self.serial = serial
    self.latitude = random.choice([31.9783, 31.9784, 31.9785])
    self.longitude = random.choice([35.8309, 35.8310, 35.8311])
    self.height = random.choice([10, 50, 150, 20, 460])
    self.speed = random.uniform(1, 5)

  def update(self):
    self.latitude = self.latitude + random.uniform(-0.001, 0.001)
    self.longitude = self.longitude + random.uniform(-0.001, 0.001)
    self.height = max(0, self.height + random.uniform(-5, 7))
    self.speed = max(0, self.speed + random.uniform(-3, 3))
    
  def generate_data(self):
    return {
      "elevation": 0,
      "gear": 1,
      "height": self.height,
      "height_limit": 100,
      "home_distance": 0,
      "horizontal_speed":self.speed,
      "is_near_area_limit": 0,
      "is_near_height_limit": 0,
      "latitude": self.latitude,
      "longitude": self.longitude,
      "rc_lost_action": 2,
      "rid_state": False,
      "rth_altitude": 20,
      "storage": {
        "total": 60368000,
        "used": random.randint(1000, 6000)
      },
      "total_flight_distance": 1,
      "total_flight_sorties": 1,
      "total_flight_time": 1,
      "track_id": "",
      "vertical_speed":1,
      "wind_direction": 1,
      "wind_speed": 1
    }
    
def random_string(len=22):
  chars = string.ascii_uppercase + string.digits
  return ''.join(random.choices(chars, k=len))
      
def main(count=3, delay=2):
  print(f"starting with {count} drones")

  

  drones = [SimulatedDrone(random_string()) for i in range(count)]

  while True:
    for drone in drones:
      drone.update()
      data = drone.generate_data()

      publish.single(
        f"thing/product/{drone.serial}/osd",
        payload=json.dumps(data),
        hostname="localhost",
        port=1883
      )
    time.sleep(delay)




if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--count", type=int, default=1, help="Number of drones to simulate")
  parser.add_argument("--delay", type=int, default=2, help="Delay between message batches (in seconds)")
  args = parser.parse_args()

  main(count=args.count, delay=args.delay)
  
