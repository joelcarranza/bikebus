import os
import sys
import site

root_dir = os.path.dirname(__file__)

# with mod_wsgi >= 2.4, this line will add this path in front of the python path
site.addsitedir(os.path.join(root_dir, 'lib/python2.7/site-packages'))

# add this django project
sys.path.append(root_dir)

import web
import web.template
from geocoder import geocode
import re
import otp
from textdirections import handle_text
import xml.etree.ElementTree as ET
import StringIO

render = web.template.render(root_dir+'/templates', base='layout')

urls = (
  '/', 'sms_test',
  '/sms','sms'
)

class sms:
  def POST(self):
    # https://www.twilio.com/docs/api/twiml/sms/twilio_request
    body = web.input().Body 
    result,message,cookies = handle_text(body,web.cookies().get('bikebus'))
    if cookies:
      web.setcookie('bikebus',cookies)
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

class sms_test:
  def POST(self):
    q = web.input().q
    result,message,cookies = handle_text(q,web.cookies().get('bikebus'))
    if cookies:
      web.setcookie('bikebus',cookies)
    return render.question(q,message)
  def GET(self):
    return render.question('',[])

if __name__ == '__main__':
  web.application(urls,globals()).run()
else:
  application = web.application(urls, globals()).wsgifunc()


