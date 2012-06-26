import requests
import json

URL = 'http://maps.googleapis.com/maps/api/geocode/json'

# Bounds for new orleans
#  u'northeast': {u'lat': 30.17723999999999, u'lng': -89.626092}, 
#  u'southwest': {u'lat': 29.868772, u'lng': -90.1376406}}
BOUNDS = (
    (29.8687,-90.1376),
    (30.1772,-89.6260)
)

def geocode(search):
  # TODO: support straight up lat/lon search
  params = dict(sensor="true",
      address=search,
      bounds='|'.join(['%f,%f' % b for b in BOUNDS]))
  r = requests.get(URL,params=params)
  r.raise_for_status()
  result = json.loads(r.text)
  status = result['status']
  # status OK ZERO_RESULTS OVER_QUERY_LIMIT
  if status == 'OK':
    for result in result['results']:
      location_type = result['geometry']['location_type']
      # require a decent location - exclude matches that just identify the
      # city center - i.e. New Orleans, LA
      if location_type == 'APPROXIMATE':
        return 'APPROXIMATE',None
      # make sure we are IN new orleans
      (lat_min,lon_min),(lat_max,lon_max) = BOUNDS
      lat = result['geometry']['location']['lat']
      lon = result['geometry']['location']['lng']
      if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
        return status,(lat,lon)
  return 'ZERO_RESULTS',None

