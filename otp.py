import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# provides an interface to the OpenTripPlanner web service

URL = 'http://50.116.38.181:8080/opentripplanner-api-webapp/ws/'

# documentation http://www.opentripplanner.org/apidoc/rest.plan.html

MODE_PARAMS = {
    # we can hack this to disallow streetcars here or we can do it in the
    # GTFS feed
    'ANY':{'mode':'TRANSIT,BICYCLE,WALK'},
    'BUS':{'mode':'TRANSIT,WALK'},
    'STREETCAR':{'mode':'TRANSIT,WALK'},
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

def format_distance(distance):
  # distance in meters
  miles = distance/ 1609.344
  return "%.1f" % miles

def format_date(ts):
  # ts is in milliseconds since the epoch
  date = datetime.fromtimestamp(ts/1000)
  # use minus to remove trailing zeroes!
  # does this not work on cygwin windows? python version?
  return date.strftime("%-I:%M%p")

def all_modes():
  return MODE_PARAMS.keys()

def stop_times(stopcode):
  headers = {}
  params = dict(agency='NORTA',id=stopcode)
  r = requests.get(URL+'transit/stopTimesForStop',headers=headers,params=params)
  r.raise_for_status()
  return json.loads(r.text)


def plan(fromPlace,toPlace,mode,date=None):
  headers = {}
  params = dict(MODE_PARAMS[mode])
  params['fromPlace'] = "%f,%f" % fromPlace
  params['toPlace'] = "%f,%f" % toPlace
  if date:
    params['date'] = date.isoformat()
  r = requests.get(URL+'plan',headers=headers,params=params)
  r.raise_for_status()
  return json.loads(r.text)
