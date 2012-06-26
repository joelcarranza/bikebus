import xml.etree.ElementTree as ET
import os
import datetime
import re
from geocoder import geocode
import re
import otp
import dateutil.parser
import textwrap
import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc

# We scan output text for these patterns and replace them with the matching
# abbreviations in order to try and shrink the size of the text message
# TODO: this could be alot more exhaustive
# see these http://www.digsafe.com/documents/1-04update/abbrv.pdf
ABBREVIATIONS = [
    (r'(?i)\s+street',' St'),
    (r'(?i)\s+avenue',' Ave'),
    (r'(?i)\s+drive',' Dr') 
]


AT_PATTERN = r'(\s+(?:at|in)\s+.+)?'
MODE_PATTERN = r'bike|bus|walk|walking|streetcar'
FROM_TO_PATTERN = r'(?:from\s+)?(.+?)\s+to\s+(.+?)'

ACTIONS = (
    (r'^help$','help'),
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
  for pattern,repl in ABBREVIATIONS:
    name = re.sub(pattern,repl,name)
  return name

def step_instructions(step):
  direction = re.sub('_',' ',step.findtext('relativeDirection').lower())
  name = abbreviate(step.findtext('streetName'))
  if direction:
    return "%s on %s" % (direction,name)
  else:
    return name

def plan_instructions(doc):
  itinerary = doc.find('plan/itineraries/itinerary')
  # TODO: what if the itinerary fails?
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
            suffix += ' via\n'+'\n'.join([step_instructions(step) for step in steps[1:-1]])
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
    return "\n".join(legtext)
  else:
    return "No results found"

# strip spaces and remove extras
# do whatever other prepocessing is necessary
def normalize(text):
  return re.sub(r'\s+',' ',text).strip()

def message(text):
  return ("MSG",[text],'')

def help():
  return message(HELP_TEXT)

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
      if len(parts) > 0 and line_length + part_length < 160:
        parts[-1] = parts[-1]+"\n"+line
        part_length = line_length + part_length
      else:
        parts.append(line)
        part_length = line_length
    return parts

def directions1(mode,dirfrom,dirto,at):
  return directions(dirfrom,dirto,mode,at)

def directions2(dirfrom,dirto,mode,at):
  return directions(dirfrom,dirto,mode,at)

def parse_natural_date(text):
  # create an instance of Constants class so we can override some of the defaults
  dc = pdc.Constants()
  # create an instance of the Calendar class and pass in our Constants # object instead of letting it create a default
  dp = pdt.Calendar(dc)    
  # http://stackoverflow.com/questions/1810432/handling-the-different-results-from-parsedatetime
  result,what = dp.parse(text)
  # what was returned (see http://code-bear.com/code/parsedatetime/docs/)
  # 0 = failed to parse
  # 1 = date (with current time, as a struct_time)
  # 2 = time (with current date, as a struct_time)
  # 3 = datetime
  if what in (1,2):
      # result is struct_time
      dt = datetime.datetime( *result[:6] )
  elif what == 3:
      # result is a datetime
      dt = result

  if dt is None:
      # Failed to parse
      raise ValueError, ("Don't understand date '"+s+"'")
  return dt
  
def error_for_geocode(result,query):
  if result == 'APPROXIMATE':
    return message("%s is not specific enough. Please refine" % query)
  else:
    return message("Unable to locate %s" % query)

def directions(dirfrom,dirto,mode,at):
  if not mode:
    mode = 'ANY'
  from_result,from_place = geocode(dirfrom)
  if from_result != 'OK':
    return error_for_geocode(from_result,dirfrom)
  to_result,to_place = geocode(dirto)
  if to_result != 'OK':
    return error_for_geocode(to_result,dirto)
  date = None
  if at:
    date = parse_natural_date(at)
  plan = otp.plan(from_place,to_place,mode.upper(),date)
  inst = plan_instructions(plan)
  return ('OK',sms_chunk(inst),'')

def match_action(text):
  for patterntext,funcname in ACTIONS:
    pattern = re.compile(patterntext,re.I)
    match = pattern.match(text)
    if match:
      return funcname,match.groups()
  return None

def handle_text(smsbody,cookies=None):
  text = re.sub(r'\s+',' ',smsbody).strip()
  action = match_action(text)
  if action:
    funcname,match = action
    func = globals().get(funcname)
    return func(*match)
  else:
    return message(UNKNOWN_COMMAND_TEXT)

