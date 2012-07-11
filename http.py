import os
import sys
import site

root_dir = os.path.dirname(__file__)

# with mod_wsgi >= 2.4, this line will add this path in front of the python path
site.addsitedir(os.path.join(root_dir, 'lib/python2.7/site-packages'))

# add this django project
sys.path.append(root_dir)

import web
from web.contrib.template import render_jinja
from geocoder import geocode
import re
import otp
import xml.etree.ElementTree as ET
import geocoder
from datetime import datetime
import StringIO
import json
import textdirections
import dateparser

render = render_jinja(
        os.path.join(root_dir,'templates'),   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
        globals=dict(otp=otp)
    )

# Add/override some global functions.
#render._lookup.globals.update(
#    otp=otp
#)


urls = (
  '/', 'app',
  '/sms-test', 'sms_debug',
  '/sms','sms'
)

class app:
  def GET(self):
    if 'mode' not in web.input():
      return render.app(timemode='now',time=datetime.today().strftime("%H:%M"))

    tvars = dict(web.input())
    tvars['error'] = None

    fromplace = getattr(web.input(),'from')
    toplace = web.input().to
    if not fromplace or not toplace:
      tvars['error'] = 'Please enter an address or landmark for From and To'
      return render.app(**tvars)

    from_result,fromgeo = geocoder.geocode(fromplace)
    if from_result != 'OK':
      tvars['error'] = 'Unable to find address for %s' % fromplace
      return render.app(**tvars)
    tvars['fromgeo'] = fromgeo

    to_result,togeo = geocoder.geocode(toplace)
    if to_result != 'OK':
      tvars['error'] = 'Unable to find address for %s' % toplace
      return render.app(**tvars)
    tvars['togeo'] = togeo

    timemode = web.input().get('timemode')
    if timemode == 'now':
      result = otp.plan(fromgeo[0:2],togeo[0:2],web.input().mode)
    else:
      try:
        time = dateparser.parse_time(web.input().time)
      except ValueError:
        tvars['error'] = "Invalid time format"
        return render.app(**tvars)

      result = otp.plan(fromgeo[0:2],togeo[0:2],web.input().mode,time,timemode)
    if 'plan' in result:
      tvars['result'] = result
    else:
      # no itinerary found - rare but possible
      tvars['error'] = result['error']['msg']
    return render.app(**tvars)

class sms:
  def POST(self):
    # https://www.twilio.com/docs/api/twiml/sms/twilio_request
    body = web.input().Body 
    result,message,cookies = textdirections.handle_text(body,web.cookies().get('bikebus'))
    if cookies is not None:
      web.setcookie('bikebus',cookies)
    else:
      web.setcookie('bikebus',web.cookies().get('bikebus'))
    # https://www.twilio.com/docs/api/twiml/sms/your_response
    root = ET.Element("Response")
    for msg in message:
      el = ET.SubElement(root,'Sms')
      el.text = msg
    tree = ET.ElementTree(root)
    web.header('Content-Type', 'text/xml')
    output = StringIO.StringIO()
    tree.write(output,encoding="UTF-8",xml_declaration=True)
    return output.getvalue()

class sms_debug:
  def POST(self):
    q = web.input().q
    result,message,cookies = textdirections.handle_text(q,web.cookies().get('bikebus'))
    if cookies is not None:
      web.setcookie('bikebus',cookies)
    else:
      web.setcookie('bikebus',web.cookies().get('bikebus'))
    return render.sms(question=q,message=message,help=[textdirections.WELCOME_TEXT,textdirections.HELP_TEXT1,textdirections.HELP_TEXT2])
  def GET(self):
    return render.sms(qestion='',message=[],help=[textdirections.WELCOME_TEXT,textdirections.HELP_TEXT1,textdirections.HELP_TEXT2])

if __name__ == '__main__':
  web.application(urls,globals()).run()
else:
  application = web.application(urls, globals()).wsgifunc()


