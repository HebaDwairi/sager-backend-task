import paho.mqtt.publish as publish
import time
import json
import string
import random
import argparse
import math

# Earth's radius in meters
EARTH_RADIUS_METERS = 6378137 

class SimulatedDrone:
  """
  A class to simulate a single drone with more natural movement.
  """
  def __init__(self, serial):
    """
    Initializes the drone's state.
    """
    self.serial = serial
    # Starting location (randomly chosen from a few points)
    self.latitude = random.choice([31.9783, 40.7128, 32.2741])
    self.longitude = random.choice([35.8309, -74.0060, 35.8920])
    # Initial flight parameters
    self.height = random.uniform(10, 50)
    self.speed = random.uniform(3, 8) # m/s
    self.heading = random.uniform(0, 360) # degrees

  def update(self, delay):
    """
    Updates the drone's state for the next time step.
    Movement is based on current speed and heading, with random variations.
    """
    # 25% chance for a significant burst in height or speed
    if random.random() < 0.25:
      if random.choice([True, False]): # 50/50 chance between height or speed burst
        self.height = random.uniform(200, 550)
        # print(f"Drone {self.serial}: Height burst! New height: {self.height:.2f}m")
      else:
        self.speed = random.uniform(10, 15)
        # print(f"Drone {self.serial}: Speed burst! New speed: {self.speed:.2f}m/s")
    else:
      # 75% chance for normal, gentle flight adjustments
      self.speed = max(1, min(9.9, self.speed + random.uniform(-0.5, 0.5)))
      self.height = max(10, self.height + random.uniform(-2, 2))

    # Simulate a gentle turn by adjusting the heading
    self.heading = (self.heading + random.uniform(-15, 15)) % 360

    # --- Calculate new position based on heading and speed ---
    distance_meters = self.speed * delay
    bearing_rad = math.radians(self.heading)
    lat_rad = math.radians(self.latitude)

    # Calculate change in latitude and longitude
    delta_lat_rad = (distance_meters * math.cos(bearing_rad)) / EARTH_RADIUS_METERS
    delta_lon_rad = (distance_meters * math.sin(bearing_rad)) / (EARTH_RADIUS_METERS * math.cos(lat_rad))

    # Update coordinates
    self.latitude += math.degrees(delta_lat_rad)
    self.longitude += math.degrees(delta_lon_rad)
    
  def generate_data(self):
    """
    Generates the data payload in the required format.
    """
    return {
      "elevation": 0,
      "gear": 1,
      "height": self.height,
      "height_limit": 100,
      "home_distance": 0,
      "horizontal_speed": self.speed,
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
      "vertical_speed": 1,
      "wind_direction": 1,
      "wind_speed": 1
    }
    
def random_string(len=22):
  """
  Generates a random alphanumeric string for the drone serial.
  """
  chars = string.ascii_uppercase + string.digits
  return ''.join(random.choices(chars, k=len))
      
def main(count=3, delay=2, broker="mosquitto"):
  """
  Main function to create drones and publish their data.
  """
  print(f"Starting simulation with {count} drones...")
  print(f"Publishing to MQTT broker at {broker}:1883 every {delay} seconds.")
  
  drones = [SimulatedDrone(random_string()) for _ in range(count)]

  while True:
    for drone in drones:
      # Update the drone's position and state
      drone.update(delay)
      data = drone.generate_data()

      topic = f"thing/product/{drone.serial}/osd"
      payload = json.dumps(data, indent=2)

      try:
        publish.single(
          topic,
          payload=payload,
          hostname=broker,
          port=1883
        )
        print(f"Published to {topic}: Lat={data['latitude']:.4f}, Lon={data['longitude']:.4f}, H={data['height']:.1f}m, S={data['horizontal_speed']:.1f}m/s")
      except Exception as e:
        print(f"Could not publish to broker at {broker}. Is it running? Error: {e}")
        time.sleep(5) # Wait before retrying if broker is down

    time.sleep(delay)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Simulate drone telemetry data and publish to MQTT.")
  parser.add_argument("--count", type=int, default=3, help="Number of drones to simulate.")
  parser.add_argument("--delay", type=int, default=2, help="Delay between message batches (in seconds).")
  parser.add_argument("--broker", type=str, default="mosquitto", help="Hostname of the MQTT broker.")
  args = parser.parse_args()

  main(count=args.count, delay=args.delay, broker=args.broker)
