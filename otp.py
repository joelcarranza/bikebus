import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import re
import time

# provides an interface to the OpenTripPlanner web service

URL = 'http://ws.bikebusnola.com:8080/opentripplanner-api-webapp/ws/'

# documentation http://www.opentripplanner.org/apidoc/rest.plan.html

# distance for biking in meters - 1609/mi
# not clear if this is per-leg or total
MAX_BIKE_DISTANCE = 3200

# transfer penalty in seconds
TRANSFER_PENALTY = 600

MODE_PARAMS = {
    # we can hack this to disallow streetcars here or we can do it in the
    # GTFS feed
    'ANY':{'mode':'TRANSIT,BICYCLE',
      'optimize':'TRIANGLE',
      'triangleTimeFactor':'0',
      'triangleSlopeFactor':'0',
      'triangleSafetyFactor':'1',
      'maxWalkDistance':MAX_BIKE_DISTANCE,'transferPenalty':TRANSFER_PENALTY}, 
    'BUS':{'mode':'TRANSIT,WALK','transferPenalty':TRANSFER_PENALTY},
    'STREETCAR':{'mode':'TRANSIT,WALK','transferPenalty':TRANSFER_PENALTY},
    'BIKE':{'mode':'BICYCLE'},
    'WALK':{'mode':'WALK'}
}

def verb_for_mode(mode):
  if mode == 'BICYCLE':
    return 'Bike'
  elif mode == 'BUS':
    return 'Take bus'
  elif mode == 'WALK':
    return 'Walk'
  elif mode == 'TRAM':
    return 'Take streetcar'
  else:
    return mode

def step_instructions(step,mode):
  name = step['streetName']
  direction = step.get('relativeDirection')
  if direction:
    direction = re.sub('_',' ',direction.capitalize())
    return "%s on %s" % (direction,name)
  else:
    direction = step.get('absoluteDirection')
    direction = re.sub('_',' ',direction.lower())
    return "%s %s on %s" % (mode.capitalize(),direction,name)

def format_distance(distance,short=False):
  # TODO: short should squeeze where possible
  # distance in meters
  if distance < 1609:
    feet = distance/ 3.2808399
    return "%dft" % feet
  else:
    miles = distance/ 1609.344
    return "%.1fmi" % miles

# TODO: support short 
def format_duration(delta,short=False):
  minutes = int(delta/60000)
  if short:
    return "%dmin" % minutes
  else:
    return "%d minutes" % minutes

# the leading - on %-I not supported on some platforms/versions?
# TODO: hate that uppercase AM/PM - perhaps would be better to format
# ourselves - would lose ability to format with arbitrary string
def format_date(ts,fmt="%-I:%M%p"):
  # ts is in milliseconds since the epoch
  date = datetime.fromtimestamp(ts/1000)
  # use minus to remove trailing zeroes!
  # does this not work on cygwin windows? python version?
  return date.strftime(fmt)

def all_modes():
  return MODE_PARAMS.keys()

def plan(fromPlace,toPlace,mode,date=None,datemode=None):
  headers = {}
  params = dict(MODE_PARAMS[mode])
  params['fromPlace'] = "%f,%f" % fromPlace
  params['toPlace'] = "%f,%f" % toPlace
  if date:
    params['date'] = date.date().isoformat()
    params['time'] = date.strftime("%I:%M %p").upper()
    if datemode == 'arrive':
      params['arriveBy'] = 'true' 
    if datemode == 'depart':
      params['arriveBy'] = 'false' 
  # TODO: catch errors here and return status code
  r = requests.get(URL+'plan',headers=headers,params=params)
  r.raise_for_status()
  return json.loads(r.text)
