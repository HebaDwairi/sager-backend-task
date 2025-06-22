from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import Drone, DroneData
from .serializers import DroneSerializer, DangerousDroneSerializer
from django.contrib.gis.geos import Point
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .services import DroneService, validate_coordinate_params

@extend_schema(
    parameters=[
      OpenApiParameter(
        name='serial',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False, 
      ),
      OpenApiParameter(
        name='partial_serial',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False, 
      ),
    ]
)
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
    return DroneService.get_online_drones()


@extend_schema(
    parameters=[
      OpenApiParameter(
        name='longitude',
        type=OpenApiTypes.FLOAT,
        location=OpenApiParameter.QUERY,
        required=True
      ),
      OpenApiParameter(
        name='latitude',
        type=OpenApiTypes.FLOAT,
        location=OpenApiParameter.QUERY,
        required=True
      ),
    ]
)
class DronesWithin5KmView(ListAPIView):
  serializer_class = DroneSerializer

  def get_queryset(self):
    target_longitude, target_latitude = validate_coordinate_params(self.request.query_params)

    target_point = Point(target_longitude, target_latitude, srid=4326)
    radius_meters = 5000

    queryset = Drone.objects.filter(last_location__dwithin=(target_point, radius_meters))

    return queryset


class DroneFlightPathView(APIView):
  def get(self, request, serial_number, *args, **kwargs):
    serial = self.kwargs['serial_number']
    drone = get_object_or_404(Drone, serial_number=serial)

    flight_path = DroneService.get_flight_path(drone)

    if not flight_path:
      return Response({"detail": "This drone has no flight path data yet."}, status=204)
  
    return Response(flight_path)


class DangerousDronesView(ListAPIView):
  serializer_class = DangerousDroneSerializer
  queryset = Drone.objects.filter(is_dangerous=True)
