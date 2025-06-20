from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from .models import Drone, OSDData
from .serializers import DroneSerializer

class ListDronesView(ListAPIView):
  serializer_class = DroneSerializer
  queryset = Drone.objects.all()

