import geocoder
import unittest

class GeocodeTests(unittest.TestCase):
  def test_geocode_latlon(self):
    code,(lat,lon) =  geocoder.geocode('29.949803,-90.068858')
    self.assertEqual(code,'OK')
    self.assertAlmostEqual(lat,29.949803)
    self.assertAlmostEqual(lon,-90.068858)

  def test_geocode_fail(self):
    # not specific
    code,result =  geocoder.geocode('New Orleans, LA')
    self.assertNotEqual(code,'OK')
    self.assertIsNone(result)
    # ambiguous results
    code,result =  geocoder.geocode('Starbucks')
    self.assertNotEquals(code,'OK')
    self.assertIsNone(result)

  def test_geocode_pass(self):
    code,(lat,lon) =  geocoder.geocode('Audubon Park')
    self.assertEqual(code,'OK')
    code,(lat,lon) =  geocoder.geocode('Superdome')
    self.assertEqual(code,'OK')
    code,(lat,lon) =  geocoder.geocode('643 Magazine Street')
    self.assertEqual(code,'OK')

