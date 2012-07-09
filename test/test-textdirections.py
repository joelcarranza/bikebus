import textdirections
import unittest
import datetime

class TextDirectionsTest(unittest.TestCase):
  def test_wrap(self):
    ipsum = '''Lorem Ipsum is simply dummy text of the printing and typesetting 
    industry. Lorem Ipsum has been the industry's standard dummy text ever since 
    the 1500s, when an unknown printer took a galley of type and scrambled it to 
    make a type specimen book. It has survived not only five centuries, but also 
    the leap into electronic typesetting, remaining essentially unchanged. It was 
    popularised in the 1960s with the release of Letraset sheets containing Lorem 
    Ipsum passages, and more recently with desktop publishing software like Aldus 
    PageMaker including versions of Lorem Ipsum.'''
    results = textdirections.wrap(ipsum,25)
    for line in results:
      self.assertTrue(len(line) <= 25)

  def test_date_parse(self):
    date = datetime.datetime(1980,8,11,14,40)
    d1 = textdirections.parse_natural_date('1 hr',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('20 min',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('8a',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('8:30',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('2:42',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('2p',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('12p',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('12a',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1
    d1 = textdirections.parse_natural_date('1210',date=date)
    self.assertIsNotNone(d1)
    self.assertTrue(d1>date)
    print d1

  def test_match_action(self):
    func,match = textdirections.match_action('help')
    self.assertEqual(func,'help')
    self.assertEqual(len(match),0)
    func,match = textdirections.match_action('bus directions from 2317 Jena St TO Canal Street')
    self.assertEqual(func,'directions1')
    self.assertEqual(match,('bus','2317 Jena St','Canal Street',None))
    func,match = textdirections.match_action('from 2317 Jena St TO Canal Street via bus')
    self.assertEqual(func,'directions2')
    self.assertEqual(match,('2317 Jena St','Canal Street','bus',None))
    func,match = textdirections.match_action('2317 Jena St TO Canal Street')
    self.assertEqual(func,'directions2')
    self.assertEqual(match,('2317 Jena St','Canal Street',None,None))

  # ensure all actions point to actual methods
  def test_actions(self):
    for pattern,action in textdirections.ACTIONS:
      self.assertIsNotNone(getattr(textdirections,action))

  def test_help_action(self):
    (code,messages,cookies) = textdirections.handle_text('help')
    self.assertEqual(code,'MSG')
    for m in messages:
      self.assertTrue(len(m)<=160)
    self.assertEqual(len(messages),1)

  def test_directions(self):
    (code,messages,cookies) = textdirections.handle_text('bike directions from 2317 Jena St TO Canal St')
    self.assertEqual(code,'OK')
    for m in messages:
      self.assertTrue(len(m)<=160)
    self.assertTrue(len(cookies)>0)

