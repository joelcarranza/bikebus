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
from textdirections import handle_text
import xml.etree.ElementTree as ET
import geocoder
import StringIO
import json

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
  # TODO: flip root and mobile at some point when testing is done
  '/mobile', 'app',
  '/', 'sms_debug',
  '/sms','sms'
)

class app:
  def POST(self):
    fromplace = web.input().fromplace
    toplace = web.input().toplace
    from_result,from_ll = geocoder.geocode(fromplace)
    to_result,to_ll = geocoder.geocode(toplace)
    result = otp.plan(from_ll[0:2],to_ll[0:2],web.input().mode)
    #result = json.load(open('plan.json'))
    return render.app(mode=web.input().mode,fromplace=fromplace,toplace=toplace,result=result,error=None)
  def GET(self):
    return render.app()
    #result = json.load(open('plan.json'))
    #return render.app(fromplace='From',toplace='To',result=result,error=None)

class sms:
  def POST(self):
    # https://www.twilio.com/docs/api/twiml/sms/twilio_request
    body = web.input().Body 
    result,message,cookies = handle_text(body,web.cookies().get('bikebus'))
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
    result,message,cookies = handle_text(q,web.cookies().get('bikebus'))
    if cookies is not None:
      web.setcookie('bikebus',cookies)
    else:
      web.setcookie('bikebus',web.cookies().get('bikebus'))
    return render.sms(question=q,message=message)
  def GET(self):
    return render.sms(qestion='',message=[])

if __name__ == '__main__':
  web.application(urls,globals()).run()
else:
  application = web.application(urls, globals()).wsgifunc()


