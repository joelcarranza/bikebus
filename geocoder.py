import requests
import json

URL = 'http://maps.googleapis.com/maps/api/geocode/json'

def parse_components(components):
  results = dict()
  for c in components:
    for ctype in c['types']:
      results[ctype] = c['short_name']
  return results

def geocode(search):
  # TODO: support straight up lat/lon search
  # Bounds for new orleans
  #  u'northeast': {u'lat': 30.17723999999999, u'lng': -89.626092}, 
  #  u'southwest': {u'lat': 29.868772, u'lng': -90.1376406}}
  params = dict(sensor="true",
      address=search,
      bounds='29.8687,-90.1376|30.1772,-89.6260')
  r = requests.get(URL,params=params)
  r.raise_for_status()
  result = json.loads(r.text)
  status = result['status']
  # status OK ZERO_RESULTS OVER_QUERY_LIMIT
  if status == 'OK':
    for result in result['results']:
      # TODO: validate that it is in roughly the correct neighborhood
      # Address is not just the city center
      components = parse_components(result['address_components'])
      # TODO: this may be too strict !
      # country or locality may not even be there!
      if components.get('country') == 'US' and components.get('locality') == 'New Orleans':
        lat = result['geometry']['location']['lat']
        lon = result['geometry']['location']['lng']
        return (lat,lon)
  return None

