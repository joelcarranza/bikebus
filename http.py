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

render = web.template.render(root_dir+'/templates', base='layout')

urls = (
    '/', 'index',
    '/sms','sms'
)

class sms:
    def POST(self):
       result,message,cookies = handle_text(web.input().q)
       return render.answer('\n'.join(message))

class index:
    def POST(self):
       result,message,cookies = handle_text(web.input().q)
       return render.answer('\n'.join(message))
    def GET(self):
        return render.question()

application = web.application(urls, globals()).wsgifunc()


