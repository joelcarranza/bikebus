import xml.etree.ElementTree as ET
import os
import datetime
import re
from geocoder import geocode
import re
import otp
import dateutil.parser

# see these http://www.digsafe.com/documents/1-04update/abbrv.pdf
abbr = [
    (r'(?i)\s+street',' St'),
    (r'(?i)\s+avenue',' Ave'),
    (r'(?i)\s+drive',' Dr') 
]


actions = (
    r'^help$','help',
    r'^(.+)\s+to\s+(.+)$','directions'
)

HELP_TEXT = 'Try texting: <start> TO <finish> for directions'
WELCOME_TEXT = 'This is an experimental bus/bike trip planner service'
UNKNOWN_COMMAND_TEXT = "Sorry I didn't understand that. Text HELP for some tips on using this service"

def verb_for_mode(mode):
  if mode == 'BICYCLE':
    return 'Bike'
  elif mode == 'BUS':
    return 'Take bus'
  elif mode == 'WALK':
    return 'walk'
  elif mode == 'TRAM':
    return 'Take streetcar'
  else:
    return mode

def format_distance(distance):
  # distance in meters
  miles = distance/ 1609.344
  return "%.1f" % miles

def format_date(datestr):
  # datestr is ISO-8601
  date = dateutil.parser.parse(datestr)
  return date.strftime("%I:%M%p")

def abbreviate(name):
  for pattern,repl in abbr:
    name = re.sub(pattern,repl,name)
  return name

def step_instructions(step):
  direction = step.findtext('relativeDirection')
  name = abbreviate(step.findtext('streetName'))
  if direction:
    return "%s on %s" % (direction,name)
  else:
    return name

def plan_instructions(doc):
  itinerary = doc.find('plan/itineraries/itinerary')
  if len(itinerary):
    legtext = []
    legn = 0
    legs = itinerary.findall('legs/leg')
    for leg in legs:
      # mode can be BUS,BICYCLE,TRAM,WALK
      mode = leg.attrib['mode']
      verb = verb_for_mode(mode)
      # include route number
      if mode == 'BUS':
         verb += " #%s" % leg.attrib['route']
      if mode == 'TRAM':
         verb = 'Take %s streetcar' % leg.attrib['routeShortName']
      # else if tram - use official route name
      fromname = abbreviate(leg.find('from/name').text)
      toname = abbreviate(leg.find('to/name').text)
      suffix = ''
      # include bike/walk distance
      if mode == 'BICYCLE' or mode == 'WALK':
        dist = float(leg.findtext('distance'))
        suffix = " (%smi)" % format_distance(dist)
        # if this the only leg then include the details
        if len(legs) == 1:
          steps = leg.findall('steps/walkSteps')
          if len(steps) > 2:
            suffix += ' via '+',\n\t'.join([step_instructions(step) for step in steps[1:-1]])
      # append the bus arrival time
      elif mode == 'BUS' or mode == 'TRAM':
        datestr = leg.findtext('startTime')
        suffix = " @%s" % format_date(datestr)
        # unlikely this is the only leg but if it is then we should provide details

      if legn == 0:
        legtext.append("%s from %s to %s%s" % (verb,fromname,toname,suffix))
      else:
        legtext.append("%s to %s%s" % (verb,toname,suffix))
      legn = legn+1
    return legtext
  else:
    return ["No results found"]

# strip spaces and remove extras
# do whatever other prepocessing is necessary
def normalize(text):
  return re.sub(r'\s+',' ',text).strip()

def message(text):
  return ("MSG",[text],'')

def help():
  return message(HELP_TEXT)

def directions(dirfrom,dirto):
  fromPlace = geocode(dirfrom)
  if not fromPlace:
    return message("Unable to locate %s" % dirfrom)
  toPlace = geocode(dirto)
  if not toPlace:
    return message("Unable to locate %s" % dirto)
  plan = otp.plan(fromPlace,toPlace,'BIKE')
  inst = plan_instructions(plan)
  return message(" ".join(inst))

def handle_text(smsbody):
  text = re.sub(r'\s+',' ',smsbody).strip()
  for i in xrange(0,len(actions),2):
    pattern = re.compile(actions[i],re.I)
    funcname = actions[i+1]
    match = pattern.match(text)
    if match:
      func = globals().get(funcname)
      return func(*match.groups())

  return message(UNKNOWN_COMMAND_TEXT)

