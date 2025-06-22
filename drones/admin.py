from django.contrib import admin
from .models import Drone, DroneData, NoFlyZone

admin.site.register(Drone)
admin.site.register(DroneData)
admin.site.register(NoFlyZone)