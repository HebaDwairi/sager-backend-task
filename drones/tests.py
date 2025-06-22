from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Drone, DroneData
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import status
from datetime import timedelta


class DroneAPITestCase(APITestCase):
  def setUp(self):
    now = timezone.now()

    self.drone_1 = Drone.objects.create(
      serial_number='Drone_01',
      last_location=Point(31.9783, 35.8309, srid=4326),
      last_height=50,
      last_speed=1,
      last_seen=now
    )
    self.drone_2 = Drone.objects.create(
      serial_number='Drone_02',
      last_location=Point(40.7128, -74.0060, srid=4326),
      last_height=501,
      last_speed=1,
      is_dangerous=True,
      dangerous_reason='Flying higher than 500 meters',
      last_seen=now - timedelta(minutes=2)
    )
    self.drone_3 = Drone.objects.create(
      serial_number='Drone_03',
      last_location=Point(32.9783, 35.8309, srid=4326),
      last_height=21,
      last_speed=16,
      is_dangerous=True,
      dangerous_reason='Moving faster than 10 m/s',
      last_seen=now - timedelta(seconds=30)
    )
    self.drone_4 = Drone.objects.create(
      serial_number='Drone_04',
      last_location=Point(31.9309, 35.8309, srid=4326),
      last_height=140,
      last_speed=4,
      last_seen=now - timedelta(seconds=1, minutes=1)
    )

    self.data_point_1 = DroneData.objects.create(
      drone=self.drone_1,
      location=Point(35.8309, 31.9783, srid=4326),
      timestamp=now - timedelta(minutes=10),
      latitude=31.9783,
      longitude=35.8309,
      horizontal_speed=1,
      height=10,
      raw_data={}
    )
    self.data_point_2 = DroneData.objects.create(
      drone=self.drone_1,
      location=Point(35.8300, 31.9790, srid=4326),
      timestamp=now - timedelta(minutes=9),
      latitude=31.9790,
      longitude=35.8300,
      horizontal_speed=1,
      height=10,
      raw_data={}
    )
    self.data_point_3 = DroneData.objects.create(
      drone=self.drone_1,
      location=Point(35.8283, 31.9801, srid=4326),
      timestamp=now - timedelta(minutes=8),
      latitude=31.9801,
      longitude=35.8283,
      horizontal_speed=1,
      height=10,
      raw_data={}
    )
  
  def test_list_all_drones(self):
    '''test retreiving a list of all drones'''

    url = reverse('drones-list')
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 4)
    

  def test_drone_by_serial(self):
    '''test retreiving a single drone by its exact serial number'''

    base_url = reverse('drones-list')
    url = f'{base_url}?serial={self.drone_3.serial_number}'
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 1)
    self.assertEqual(response_data[0]['serial_number'], self.drone_3.serial_number)


  def test_drone_by_part_of_serial(self):
    '''test filtering drones by a part of serial number'''

    base_url = reverse('drones-list')
    url = f'{base_url}?partial_serial={self.drone_1.serial_number[4:]}'
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 1)
    self.assertEqual(response_data[0]['serial_number'], self.drone_1.serial_number)


    #matching all drones
    url = f'{base_url}?partial_serial=Drone_0'
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 4)


  def test_list_online_drones(self):
    '''test retrieving all online drones, online drones are the ones that have sent data within the last minute'''

    url = reverse('online-drones-list')
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 2)
    
    online_drones_serials = [drone['serial_number'] for drone in response_data]
    self.assertIn(self.drone_1.serial_number, online_drones_serials)
    self.assertIn(self.drone_3.serial_number, online_drones_serials)
    self.assertNotIn(self.drone_2.serial_number, online_drones_serials)
    self.assertNotIn(self.drone_4.serial_number, online_drones_serials)
    
  
  def test_list_dangerous_drones(self):
    '''test retrieving all dangerous drones'''

    url = reverse('dangerous-drones-list')
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 2)
    
    dangerous_drones_serials = [drone['serial_number'] for drone in response_data]
    self.assertIn(self.drone_2.serial_number, dangerous_drones_serials)
    self.assertIn(self.drone_3.serial_number, dangerous_drones_serials)
    self.assertNotIn(self.drone_1.serial_number, dangerous_drones_serials)
    self.assertNotIn(self.drone_4.serial_number, dangerous_drones_serials)

  def test_drones_within_5km_success(self):
    '''test retreiving drones within 5 km from drone'''

    base_url = reverse('drones-within-5km-from-point')
    target_location = self.drone_1.last_location
    url = f'{base_url}?longitude={target_location.x}&latitude={target_location.y}'
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 2)

    serials = [drone['serial_number'] for drone in response_data]
    self.assertIn(self.drone_1.serial_number, serials)
    self.assertIn(self.drone_4.serial_number, serials)


  def test_drones_within_5km_failure(self):
    '''test retreiving drones within 5 km from a point farther than 5 km from any drone'''

    base_url = reverse('drones-within-5km-from-point')
    url = f'{base_url}?longitude=20.9309&latitude=40.8309'
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertEqual(len(response_data), 0)


  def test_drone_flight_path(self):
    '''test returning the flight path for drone as geojson'''

    url = reverse('drone-flight-path', kwargs={'serial_number': self.drone_1.serial_number})
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()

    self.assertIn('type', response_data)
    self.assertEqual('LineString', response_data['type'])
    self.assertIn('coordinates', response_data)
    self.assertIsInstance(response_data['coordinates'], list)

    self.assertEqual(response_data['coordinates'][0], [self.data_point_1.location.x, self.data_point_1.location.y])
    self.assertEqual(response_data['coordinates'][1], [self.data_point_2.location.x, self.data_point_2.location.y])
    self.assertEqual(response_data['coordinates'][2], [self.data_point_3.location.x, self.data_point_3.location.y])

  def test_within_5km_missing_params(self):
    """test that within-5km endpoint returns error when parameters are missing"""
    url = reverse('drones-within-5km-from-point')
    response = self.client.get(url)
    
    self.assertEqual(response.status_code, 400)
    self.assertIn('error', response.json())