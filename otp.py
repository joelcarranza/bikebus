import requests
import xml.etree.ElementTree as ET

# provides an interface to the OpenTripPlanner web service

URL = 'http://50.116.38.181:8080/opentripplanner-api-webapp/ws/plan'

# documentation http://www.opentripplanner.org/apidoc/rest.plan.html

MODE_PARAMS = {
    # we can hack this to disallow streetcars here or we can do it in the
    # GTFS feed
    'BIKE':{'mode':'TRANSIT,BICYCLE'},
    'WALK':{'mode':'TRANSIT,WALK'}
}

def all_modes():
  return MODE_PARAMS.keys()

def plan(fromPlace,toPlace,mode):
  headers = {'Accept': 'text/xml'}
  params = dict(MODE_PARAMS[mode])
  params['fromPlace'] = "%f,%f" % fromPlace
  params['toPlace'] = "%f,%f" % toPlace
  r = requests.get(URL,headers=headers,params=params)
  r.raise_for_status()
  return ET.fromstring(r.text)

