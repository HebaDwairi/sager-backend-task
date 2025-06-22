from rest_framework.exceptions import ValidationError
from drones.models import Drone, DroneData
from django.contrib.gis.geos import Point
from django.utils import timezone
from .strategies import DangerClassifier
from datetime import timedelta


class DroneService:
  @staticmethod
  def classify_danger(height, speed, location):
    classifier = DangerClassifier()
    return classifier.classify_danger(height, speed, location)
  

  @staticmethod
  def process_drone_message(serial_number, data):
    longitude = data['longitude']
    latitude = data['latitude']
    height = data['height']
    speed = data['horizontal_speed']
    location = Point(longitude, latitude)
    is_dangerous, dangerous_reason = DroneService.classify_danger(height, speed, location)

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
  

  @staticmethod
  def get_online_drones():
    time_now = timezone.now()
    one_min = timedelta(minutes=1)
    one_min_ago = time_now - one_min

    return Drone.objects.filter(last_seen__gte=one_min_ago)
  
  @staticmethod
  def get_flight_path(drone):
    flight_data = DroneData.objects.filter(drone=drone).order_by('timestamp')

    coordinates_list = []
    for point in flight_data:
      coordinates_list.append([point.longitude, point.latitude])
    
    geo_json_obj = {
      "type": "LineString",
      "coordinates": coordinates_list
    }

    return geo_json_obj

  


def validate_coordinate_params(params):
  if 'longitude' not in params or 'latitude' not in params:
    raise ValidationError({
      "error": "both longitude and latitude parameters are required"
    })
      
  try:
    longitude = float(params.get('longitude'))
    latitude = float(params.get('latitude'))
  except ValueError:
    raise ValidationError({
        "error": "Longitude and latitude must be valid numbers"
    })
      
  if longitude < -180 or longitude > 180:
      raise ValidationError({"error": "longitude must be between -180 and 180"})
      
  if latitude < -90 or latitude > 90:
      raise ValidationError({"error": "latitude must be between -90 and 90"})
  
  return longitude, latitude