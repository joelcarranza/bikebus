import csv
from itertools import izip

# This script aments GTFS feed with trip_bikes_allowed field
# as per: 
# https://groups.google.com/forum/?fromgroups#!topic/gtfs-changes/rEiSeKNc4cs

def csv_read(filename):
  results = []
  header = None
  with open(filename, 'rb') as f:
      reader = csv.reader(f)
      for row in reader:
        if not header:
          header = row
        else:
          results.append(dict(izip(header,row)))
  return results

def csv_write(filename,data,header=None):
  if not header:
    header = data[0].keys()
  with open(filename, 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in data:
      rowdata = [row.get(key,'') for key in header]
      writer.writerow(rowdata)

if __name__ == '__main__':
  routes = csv_read('routes.txt')
  route_type_by_id = {}
  for r in routes:
    route_type_by_id[r['route_id']] = int(r['route_type'])
  trips = csv_read('trips.txt')
  for trip in trips:
    route_id = trip['route_id']
    # 0 - Tram/Streetcar  3-bus
    route_type = route_type_by_id[route_id]
    # 2: bikes allowed on this trip 
    # 1: no bikes allowed on this trip 
    # 0: no information (same as field omitted) 
    if route_type == 3:
      trip['trip_bikes_allowed'] = 2
    elif route_type == 0:
      trip['trip_bikes_allowed'] = 1
    else:
      trip['trip_bikes_allowed'] = 0
  csv_write('trips-modified.txt',trips)
