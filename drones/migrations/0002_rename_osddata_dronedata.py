# Generated by Django 5.2.3 on 2025-06-21 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drones', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OSDData',
            new_name='DroneData',
        ),
    ]
