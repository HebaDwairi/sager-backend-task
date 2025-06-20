from django.urls import path
from .views import ListDronesView

urlpatterns = [
  path('', ListDronesView.as_view(), name='drones-list')
]