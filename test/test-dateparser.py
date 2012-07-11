import dateparser
import unittest
import datetime

class DateParserTest(unittest.TestCase):
  def test_parse_time(self):
    date = datetime.datetime(1980,8,11,14,40)
    d1 = dateparser.parse_time('1 hr',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('20 min',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('8a',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('8:30',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('2:42',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('2p',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('12p',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('12a',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = dateparser.parse_time('1210',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
