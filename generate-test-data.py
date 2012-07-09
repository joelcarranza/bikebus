import otp
import json

n = 1

def dump(result):
  global n
  f = open("test/data/plan-%d.json" % n,'w')
  json.dump(result,f,sort_keys=True,indent=2)
  f.close()
  n = n+1

if __name__ == '__main__':
  # Freret St
  loc1 = (29.934984,-90.109348)
  # French Quarter
  loc2 = (29.950138,-90.061519)
  # Fairgrounds
  loc3 = (29.991776,-90.083256)
  
  dump(otp.plan(loc1,loc2,'ANY'))
  dump(otp.plan(loc1,loc3,'ANY'))
  dump(otp.plan(loc2,loc2,'ANY'))
  dump(otp.plan(loc3,loc2,'BIKE'))
  dump(otp.plan(loc2,loc1,'BUS'))
  dump(otp.plan(loc2,loc3,'WALK'))


