from django.contrib.gis.db import models

class Drone(models.Model):
  serial_number = models.CharField(max_length=100, unique=True, primary_key=True)
  created_at = models.DateTimeField(auto_now_add=True)
  last_seen = models.DateTimeField()
  last_location = models.PointField(geography=True)
  last_height = models.FloatField()
  last_speed = models.FloatField()
  is_dangerous = models.BooleanField(default=False)
  dangerous_reason = models.CharField(max_length=200, null=True, blank=True)

  def __str__(self):
    return self.serial_number



class DroneData(models.Model):
  drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name='osd_data')
  timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
  location = models.PointField(geography=True)
  latitude = models.FloatField()
  longitude = models.FloatField()
  height = models.FloatField()
  horizontal_speed = models.FloatField()
  raw_data = models.JSONField()

  def __str__(self):
    return f"{self.drone.serial_number}_{self.timestamp.isoformat()}"
  

class NoFlyZone(models.Model):
  name = models.CharField(max_length=255, unique=True)
  geometry = models.PolygonField(srid=4326, geography=True)

  def __str__(self):
    return f"{self.name}"
