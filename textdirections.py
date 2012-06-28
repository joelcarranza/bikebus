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
    # nuke stuff in paranthesis - has a tendency to be junk
    (r'\([^)]*\)','')
]


AT_PATTERN = r'(\s+(?:at|in)\s+.+)?'
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

HELP_TEXT = 'Try texting: <start> TO <finish> for directions'
WELCOME_TEXT = 'This is an experimental bus/bike trip planner service'
UNKNOWN_COMMAND_TEXT = "Sorry I didn't understand that. Text HELP for some tips on using this service"

def abbreviate(name):
  for pattern,repl in ABBREVIATIONS:
    name = re.sub(pattern,repl,name)
  return name

def step_instructions(step):
  direction = step.get('relativeDirection')
  if direction:
    direction = re.sub('_',' ',direction.lower())
  name = abbreviate(step['streetName'])
  if direction:
    return "%s on %s" % (direction,name)
  else:
    return name

def leg_details(leg):
  mode = leg['mode']
  verb = otp.verb_for_mode(mode)
  fromname = abbreviate(leg['from']['name'])
  toname = abbreviate(leg['to']['name'])
  dist = leg['distance']
  suffix = " (%smi)" % otp.format_distance(dist)
  detail_text = "%s from %s to %s%s\n" % (verb,fromname,toname,suffix)
  steps = leg['steps']
  return detail_text+'\n'.join([step_instructions(step) for step in steps])

def plan_instructions(doc):
  # choose a single itinerary
  itinerary = doc['plan']['itineraries'][0]
  # TODO: what if the itinerary fails?
  if len(itinerary):
    legtext = []
    legn = 0
    legs = itinerary['legs']
    details = {}
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
        if dist > 175: # ~approx 0.1 miles, anything closer don't bother with distance
          suffix = " (%smi)" % otp.format_distance(dist)
        # if this the only leg then include the details
        if len(legs) == 1:
          steps = leg['steps']
          if len(steps) > 2:
            suffix += ' via\n'+'\n'.join([step_instructions(step) for step in steps[1:-1]])
        else:
          details[n] = sms_chunk(leg_details(leg))
      # append the bus arrival time
      elif mode == 'BUS' or mode == 'TRAM':
        ts = leg['startTime']
        suffix = " @%s" % otp.format_date(ts)
        # TODO
        details[n] = "STOP %s" % leg['from']['stopCode']
        # unlikely this is the only leg but if it is then we should provide details

      prefix = ''
      if len(legs) > 1:
        prefix = "%s. " % n
      if legn == 0:
        legtext.append("%s%s from %s to %s%s" % (prefix,verb,fromname,toname,suffix))
      else:
        legtext.append("%s%s to %s%s" % (prefix,verb,toname,suffix))
      legn = legn+1

    if len(legs) > 1:
      legtext.append('Text # for more info')
    return ('OK',sms_chunk("\n".join(legtext)),json.dumps(details))
  else:
    return message("No results found")

# strip spaces and remove extras
# do whatever other prepocessing is necessar/
def normalize(text):
  return re.sub(r'\s+',' ',text).strip()

def message(text):
  return ("MSG",[text],'')

def stop_info(stopcode):
  times = otp.stop_times(stopcode)
  return message("NOT YET IMPLEMENTED - stop %s" % stopcode)

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
      if len(parts) > 0 and (line_length + part_length + 1) < 160:
        parts[-1] = parts[-1]+"\n"+line
        part_length = line_length + part_length + 1
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

