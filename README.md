bikebus
=======

A web application demonstrating "multi-modal" trip planning for the city of New Orleans, allowing a user to get directions through the city using any combination of walking, bicycling, and public transit. It is specifically designed to address the need of bicyclists who might like to incorporate public transit into their daily travels. 

In order to provide access to the largest group of people, the app provides an interface through which a citizen can ask for directions via text message. 

This code was written for the [Good Idea For New Orleans][good] project, with the aim of making "making bike transportation easier and safer". It leans heavily on open source software and open data.

[good]:http://handbook.neighborland.com/good-ideas-for-new-orleans/

# SMS 

A user can ask for directions via text message by texting XXX-XXXX (TODO). An example of possible text message commands are

	Audubon Park to Superdome
	directions from Audobon Park to Superdome by bike 
	bus directions  from Audubon  Park to Superdome
	Audubon Park to Superdome by bike bus at 3:40

Texting HELP to the service provides some brief instructions

# Mobile Webapp

TODO

# Technical Bits

bikebus is written in Python and uses the [web.py][webpy] framework. The webapp acts as a front-end to a server running the [OpenTripPlanner][otp] software, which provides routing and direction services. The app queries OpenTripPlanner through the [REST API][otp-rest] and formats the response in a web or text friendly format. 

Place names must be geocoded to geographic coordinates in latitude,longitude form before being passed into OpenTripPlanner. Currently, the project uses the [Google geocoder][google-geocoder], but any other geocoder can easily be swapped in. See geocoder.py for more details

Text messaging is provided via [Twilio][twilio]

[webpy]:http://webpy.org/
[otp]:https://github.com/openplans/OpenTripPlanner/wiki/
[twilio]:https://www.twilio.com/
[otp-rest]:http://www.opentripplanner.org/apidoc/
[google-geocoder]:https://developers.google.com/maps/documentation/geocoding/

## Data

[OpenTripPlanner][otp] software uses street data from [OpenStreetMap][osm]. Transit data is supplied in  [GTFS][gtfs] format by the [New Orleans RTA][norta]

[norta]:http://www.norta.com/
[gtfs]:https://developers.google.com/transit/gtfs/
[osm]:http://www.openstreetmap.org/

# Installation

A `requirements.txt` file lists all of the required dependencies for running the webapp. Virtualenv is recommended. 

TODO: wsgi/apache conf instructions here

[virtualenv]:http://www.clemesha.org/blog/modern-python-hacker-tools-virtualenv-fabric-pip/
[wsgi-apache]:http://eleclerc.ca/2009/03/26/django-virtualenv-and-mod_wsgi/

# License

This code is in the public domain. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission. 

# Contact

Contributions of any form are welcome.

Joel Carranza  - joel.carranza@gmail.com