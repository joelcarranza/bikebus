import xml.etree.ElementTree as ET
import os
import datetime
import re
from geocoder import geocode
import re
import otp
import dateparser
import dateutil.parser
import textwrap
import json

# We scan output text for these patterns and replace them with the matching
# abbreviations in order to try and shrink the size of the text message
# TODO: this could be alot more exhaustive
# see these http://www.digsafe.com/documents/1-04update/abbrv.pdf
ABBREVIATIONS = [
    (r'(?i)\s+street',' St'),
    (r'(?i)\s+avenue',' Ave'),
    (r'(?i)\s+drive',' Dr'),
    (r'(?i)\s+road',' Rd'),
    # Bicycle is too long - use Bike
    (r'Bicycle\s+','Bike '),
    # nuke stuff in paranthesis - has a tendency to be junk
    (r'\([^)]*\)','')
]


AT_PATTERN = r'(?:\s+(leave|arrive|depart)(?:\s+(?:by|at|in))\s+(.+))?'
MODE_PATTERN = r'bike|bus|walk|walking|streetcar'
FROM_TO_PATTERN = r'(?:from\s+)?(.+?)\s+to\s+(.+?)'

ACTIONS = (
    (r'^help$','help'),
    (r'^stop\s+(\d+)$','stop_info'),
    # MODE directions from FROM to TO at AT
    ('^('+MODE_PATTERN+r')(?:\s+directions\s+)?'+
    FROM_TO_PATTERN+
    AT_PATTERN+
    '$'
    ,'directions1'),
    # from FROM to TO via MODE at AT
    (r'^(?:directions\s+)?'+FROM_TO_PATTERN+
    '(?:\s+(?:by|via)\s+('+MODE_PATTERN+'))?'+
    AT_PATTERN+
    '$'
    ,'directions2')
)

WELCOME_TEXT = '''
Bikebusnola.com - New Orleans transit and bike directions via text msg
TEXT with msg
  START to FINISH
To get bike+bus directions
  HELP
For more options
'''.strip()

HELP_TEXT1 = '''
To get bike+bus directions from A to B text:
  A to B
Use addresses or well known landmarks. 
Results may include steps - 1,2,3... Text step # for more info
'''.strip()

HELP_TEXT2 = '''
To change travel mode:
  A to B by MODE
MODE may be BIKE BUS or WALKING
To get directions for a certain time:
  A to B arrive at TIME
  A to B depart at TIME
'''.strip()

UNKNOWN_COMMAND_TEXT = "Sorry I didn't understand that. Text HELP for some tips on using this service"

def abbreviate(name):
  for pattern,repl in ABBREVIATIONS:
    name = re.sub(pattern,repl,name)
  return name


def format_duration(leg):
  return otp.format_duration(leg['endTime']-leg['startTime'],short=True)

def step_instructions(step,mode):
  name = abbreviate(step['streetName'])
  dist = step['distance']
  direction = step.get('relativeDirection')
  if direction:
    direction = re.sub('_',' ',direction.capitalize())
    return "%s on %s" % (direction,name)
  else:
    direction = step.get('absoluteDirection')
    direction = re.sub('_',' ',direction.capitalize())
    return "%s on %s" % (direction,name)

def busleg_details(leg):
  legtext = []
  start = leg['startTime']
  end = leg['endTime']
  legtext.append("%s-%s" % (leg['routeShortName'],leg['routeLongName']))
  # include a space befer @NN:NN becase this is often a line to wrap 
  legtext.append("Depart stop #%s %s @%s" % (leg['from']['stopCode'],abbreviate(leg['headsign']),otp.format_date(start)))
  legtext.append("Arrive stop #%s %s @%s" % (leg['to']['stopCode'],abbreviate(leg['to']['name']),otp.format_date(end)))
  legtext.append(format_duration(leg))
  return "\n".join(legtext)

def leg_details(leg):
  legtext = []

  mode = leg['mode']
  verb = otp.verb_for_mode(mode).lower()
  dist = leg['distance']
  dur = leg['endTime']-leg['startTime']
  legtext.append("%s %s-%s" % (otp.format_distance(dist),verb,format_duration(leg)))
  for step in leg['steps']:
    legtext.append(step_instructions(step,mode))
  
  return "\n".join(legtext)

def has_transit_leg(itin):
  for leg in itin['legs']:
    mode = leg['mode']
    if mode == 'BUS' or mode == 'TRAM':
      return True
  return False

def plan_instructions(doc):
  if 'error' in doc:
    # abbreviate to kill parantheticals
    # one error is something like:
    # Trip is not possible.  Your start or end point might not be safely accessible .
    return message(abbreviate(doc['error']['msg']))
  elif 'plan' in doc:
    plan = doc['plan']
    modes = doc['requestParameters']['mode'].split(',')
    legtext = []
    details = {}
    # choose a single itinerary
    # if we selected transit directions, prefer a transit itinerary 
    # even if it is slower
    if 'TRANSIT' in modes:
      busitinerary = [itin for itin in plan['itineraries'] if has_transit_leg(itin)]
      if len(busitinerary):
        itinerary = busitinerary[0]
      else:
        legtext.append("No bus route available")
        itinerary = plan['itineraries'][0]
    else:
      itinerary = plan['itineraries'][0]
    legs = itinerary['legs']

    if len(legs) > 1:
      legn = 0
      for leg in legs:
        n = str(legn+1)
        # mode can be BUS,BICYCLE,TRAM,WALK
        mode = leg['mode']
        verb = otp.verb_for_mode(mode)
        # include route number
        if mode == 'BUS':
           verb += " #%s" % leg['route']
        if mode == 'TRAM':
           verb = 'Take %s streetcar' % leg['routeShortName']
        # else if tram - use official route name
        fromname = abbreviate(leg['from']['name'])
        toname = abbreviate(leg['to']['name'])
        suffix = ''
        # include bike/walk distance
        if mode == 'BICYCLE' or mode == 'WALK':
          dist = leg['distance']
          suffix = "-%s" % otp.format_distance(dist)
          # if this the only leg then include the details
          if len(legs) == 1:
            steps = leg['steps']
            if len(steps) > 2:
              suffix += ' via\n'+'\n'.join([step_instructions(step,mode) for step in steps[1:-1]])
          else:
            details[n] = sms_chunk(leg_details(leg))
        # append the bus arrival time
        elif mode == 'BUS' or mode == 'TRAM':
          ts = leg['startTime']
          # include a space befer @NN:NN becase this is often a line to wrap 
          suffix = " @%s %s" % (otp.format_date(ts),format_duration(leg))
          # TODO
          details[n] = sms_chunk(busleg_details(leg))
          # unlikely this is the only leg but if it is then we should provide details

        prefix = ''
        if len(legs) > 1:
          prefix = "%s." % n
        if legn == 0:
          legtext.append("%s%s from %s to %s%s" % (prefix,verb,fromname,toname,suffix))
        else:
          legtext.append("%s%s to %s%s" % (prefix,verb,toname,suffix))
        legn = legn+1

      legtext.append('Text # for more info')
      if itinerary != plan['itineraries'][0]:
        # what if there are multiple legs ?
        altleg = plan['itineraries'][0]['legs'][0]
        if 'BICYCLE' in modes:
          legtext.append('Biking may be faster.Text BIKE for details')
          details['bike'] = sms_chunk(leg_details(altleg))
        else:
          legtext.append('Walking may be faster.Text WALK for details')
          details['walk'] = sms_chunk(leg_details(altleg))
      return ('OK',sms_chunk("\n".join(legtext)),json.dumps(details))
    else: # single leg - WALK or BIKE
      leg = legs[0]
      return ('OK',sms_chunk(leg_details(leg)),json.dumps(details))
  else:
    return message("No results found")

# strip spaces and remove extras
# do whatever other prepocessing is necessar/
def normalize(text):
  return re.sub(r'\s+',' ',text).strip()

def message(text):
  # this is just to limit any messages that might come from unexpected places
  # like say the error message returned by OTP
  if len(text) > 160:
    text = text[0:157]+'...'
  return ("MSG",[text],'')

def stop_info(stopcode):
  # This is tricky - not working yet
  return message("NOT YET IMPLEMENTED - stop %s" % stopcode)

def help():
  return ('OK',[HELP_TEXT1,HELP_TEXT2],'')

def wrap(text,n=160):
  lines = []
  for inputline in text.split('\n'):
    if len(inputline) < n:
      lines.append(inputline)
    else:
      for chunk in textwrap.wrap(text,n):
        lines.append(chunk)
  return lines

def sms_chunk(text):
  if len(text) < 160:
    return [text]
  else:
    lines = wrap(text,160)
    parts = []
    part_length = 0
    for line in lines:
      line_length = len(line)
      if len(parts) > 0 and (line_length + part_length + 1) < 160:
        parts[-1] = parts[-1]+"\n"+line
        part_length = line_length + part_length + 1
      else:
        parts.append(line)
        part_length = line_length
    return parts

def directions1(mode,dirfrom,dirto,atmode,at):
  return directions(dirfrom,dirto,mode,at,atmode)

def directions2(dirfrom,dirto,mode,atmode,at):
  return directions(dirfrom,dirto,mode,at,atmode)

def error_for_geocode(result,query):
  if result == 'APPROXIMATE':
    return message("%s is not specific enough. Please refine" % query)
  else:
    return message("Unable to locate %s" % query)

def directions(dirfrom,dirto,mode,at,atmode):
  if not mode:
    mode = 'ANY'
  from_result,from_place = geocode(dirfrom)
  if from_result != 'OK':
    return error_for_geocode(from_result,dirfrom)
  to_result,to_place = geocode(dirto)
  if to_result != 'OK':
    return error_for_geocode(to_result,dirto)
  date = None
  datemode = None
  if at:
    date = dateparser.parse_time(at)
    if atmode == 'arrive':
      datemode = 'arrive'
    else:
      datemode = 'depart'
    print "date chosen %s,mode=%s" % (date,datemode)
  plan = otp.plan(from_place[0:2],to_place[0:2],mode.upper(),date,datemode)
  return plan_instructions(plan)

def match_action(text):
  for patterntext,funcname in ACTIONS:
    pattern = re.compile(patterntext,re.I)
    match = pattern.match(text)
    if match:
      return funcname,match.groups()
  return None

def handle_text(smsbody,cookies=None):
  # cookie data is JSON with response for special "shortcodes"
  # a response can be an array in which cases it is a series of text messages
  # or a string in which case it is a command which is reevaluated
  if cookies:
    cookie_key = smsbody.lower()
    cookie_data = json.loads(cookies)
    if cookie_key in cookie_data:
      result = cookie_data[cookie_key]
      if isinstance(result,basestring):
        smsbody = result
      else:
        # return none as cookie data so that cookie is not reset 
        # and user can follow up with more details
        return ('OK',result,None)
  text = re.sub(r'\s+',' ',smsbody).strip()
  action = match_action(text)
  if action:
    funcname,match = action
    func = globals().get(funcname)
    return func(*match)
  else:
    return message(UNKNOWN_COMMAND_TEXT)

if __name__ == '__main__':
  import sys
  import os
  cookies = None
  for arg in sys.argv[1:]:
    if arg[-5:] == '.json':
      f = open(arg)
      plan = json.load(f)
      result,messages,cookies = plan_instructions(plan)
    else:
      result,messages,cookies = handle_text(arg,cookies)
    print '*** %s ***\n[%s]' % (arg,result)
    for m in messages:
      print m
      print "-- %d -- " % len(m)
