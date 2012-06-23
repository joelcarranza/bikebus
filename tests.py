import random
import geocoder
import unittest
import textdirections

# These are some basic tests of the system - collapsed into a single file for 
# convience

class OtpTest(unittest.TestCase):
  def test_plan(self):
    print plan((29.976132,-90.080115),(29.949958,-90.109984),'BIKE')

class TextDirectionsTest(unittest.TestCase):
  def test_directions(self):
    print textdirections.handle_text('HELPPPP')
    print textdirections.handle_text('help')
    print textdirections.handle_text('2317 Jena St TO Canal St')

class GeocodeTests(unittest.TestCase):
  def test_geocode(self):
    print geocoder.geocode('New Orleans, LA')
    print geocoder.geocode('2317 Jena St')


if __name__ == '__main__':
    unittest.main()
