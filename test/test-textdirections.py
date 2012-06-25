import textdirections
import unittest

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
    

  def test_match_action(self):
    func,match = textdirections.match_action('help')
    self.assertEquals(func,'help')
    func,match = textdirections.match_action('bus directions from 2317 Jena St TO Canal Street')
    self.assertEquals(func,'directions1')
    func,match = textdirections.match_action('from 2317 Jena St TO Canal Street via bus')
    self.assertEquals(func,'directions2')
    func,match = textdirections.match_action('2317 Jena St TO Canal Stel')
    self.assertEquals(func,'directions2')

  def test_directions(self):
    print textdirections.handle_text('HELPPPP')
    print textdirections.handle_text('help')
    print textdirections.handle_text('bike directions from 2317 Jena St TO Canal St')

