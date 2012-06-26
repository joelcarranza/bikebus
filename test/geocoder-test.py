import geocoder
import unittest

class GeocodeTests(unittest.TestCase):
  def test_geocode(self):
    print geocoder.geocode('New Orleans, LA')
    print geocoder.geocode('2317 Jena St')
    print geocoder.geocode('Starbucks')

