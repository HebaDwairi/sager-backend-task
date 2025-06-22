from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import Drone, DroneData
from django.utils import timezone
from .serializers import DroneSerializer, FlightPathSerializer, DangerousDroneSerializer
from datetime import timedelta
from django.contrib.gis.geos import Point
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

class ListDronesView(ListAPIView):
  serializer_class = DroneSerializer

  def get_queryset(self):
    queryset = Drone.objects.all()

    serial = self.request.query_params.get('serial', None)
    partial_serial = self.request.query_params.get('partial_serial', None)

    if serial:
      queryset = queryset.filter(serial_number=serial)
    elif partial_serial:
      queryset = queryset.filter(serial_number__icontains=partial_serial)
    
    return queryset


class ListOnlineDronesView(ListAPIView):
  serializer_class = DroneSerializer

  def get_queryset(self):
    time_now = timezone.now()
    one_min = timedelta(minutes=1)
    one_min_ago = time_now - one_min

    queryset = Drone.objects.filter(last_seen__gte=one_min_ago)

    return queryset


class DronesWithin5KmView(ListAPIView):
  serializer_class = DroneSerializer

  def get_queryset(self):
    if 'longitude' not in self.request.query_params or 'latitude' not in self.request.query_params:
      raise ValidationError({
          "error": "Both longitude and latitude parameters are required"
      })
      
    try:
      target_longitude = float(self.request.query_params.get('longitude'))
      target_latitude = float(self.request.query_params.get('latitude'))
    except ValueError:
      raise ValidationError({
          "error": "Longitude and latitude must be valid numbers"
      })
    
    target_point = Point(target_longitude, target_latitude, srid=4326)
    radius_meters = 5000

    queryset = Drone.objects.filter(last_location__dwithin=(target_point, radius_meters))

    return queryset


class DroneFlightPathView(APIView):
  def get(self, request, serial_number, *args, **kwargs):
    serial = self.kwargs['serial_number']
    drone = get_object_or_404(Drone, serial_number=serial)

    queryset = DroneData.objects.filter(drone=drone).order_by('timestamp')

    serializer = FlightPathSerializer(queryset, many=True)

    coordinates_list = []

    for point in serializer.data:
      coordinates_list.append([point['longitude'], point['latitude']])
    
    geo_json_obj = {
      "type": "LineString",
      "coordinates": coordinates_list
    }
    if not queryset.exists():
      return Response({"detail": "This drone has no flight path data yet."}, status=204)
  
    return Response(geo_json_obj)


class DangerousDronesView(ListAPIView):
  serializer_class = DangerousDroneSerializer
  queryset = Drone.objects.filter(is_dangerous=True)
