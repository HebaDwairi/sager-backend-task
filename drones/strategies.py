from abc import ABC, abstractmethod
from .models import NoFlyZone

class DangerClassificationStrategy(ABC):
  @abstractmethod
  def is_dangerous(self, height, speed, location):
    pass

class HeightDangerStrategy(DangerClassificationStrategy):
  def is_dangerous(self, height, speed, location):
    if height is not None and height > 500:
      return True, 'Flying higher than 500 meter'
    return False, None
  
class SpeedDangerStrategy(DangerClassificationStrategy):
  def is_dangerous(self, height, speed, location):
    if speed is not None and speed > 10:
      return True, 'Moving faster than 10 m/s'
    return False, None
    
class NoFlyZoneDangerStrategy(DangerClassificationStrategy):
  def is_dangerous(self, height, speed, location):
    overlapping_zones = NoFlyZone.objects.filter(geometry__contains=location)
    if overlapping_zones:
      zone_names = ', '.join([zone.name for zone in overlapping_zones])
      return True, f'Entering no fly zone: {zone_names}'
    return False, None

class DangerClassifier:
  def __init__(self):
    self.strategies = [
      HeightDangerStrategy(),
      SpeedDangerStrategy(),
      NoFlyZoneDangerStrategy()
    ]
  
  def classify_danger(self, height, speed, location):
    reasons = []
    is_dangerous = False

    for strategy in self.strategies:
      dangerous, reason = strategy.is_dangerous(height, speed, location)
      if dangerous:
        is_dangerous = True
        reasons.append(reason)
    
    if reasons:
      return is_dangerous, ' and '.join(reasons)
    else:
      return False, None