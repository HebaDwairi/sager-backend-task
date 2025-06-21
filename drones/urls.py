from django.urls import path
from .views import ListDronesView, ListOnlineDronesView, DronesWithin5KmView, DangerousDronesView, DroneFlightPathView

urlpatterns = [
  path('', ListDronesView.as_view(), name='drones-list'),
  path('online/', ListOnlineDronesView.as_view(), name='online-drones-list'),
  path('within-5km/', DronesWithin5KmView.as_view(), name='drones-within-5km-from-point'),
  path('dangerous/', DangerousDronesView.as_view(), name='dangerous-drones-list'),
  path('<str:serial_number>/flight-path/', DroneFlightPathView.as_view(), name='drone-flight-path')
]