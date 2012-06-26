import unittest
import otp

# These are some basic tests of the system - collapsed into a single file for 
# convience

class OtpTest(unittest.TestCase):
  def test_plan(self):
    print otp.plan((29.976132,-90.080115),(29.949958,-90.109984),'BIKE',None)

