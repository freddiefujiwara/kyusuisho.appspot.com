import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Page(db.Model):
  page_id = db.IntegerProperty()
  html = db.TextProperty()

class Map(db.Model):
  map_id = db.StringProperty()
  prefecture = db.StringProperty()
  city = db.StringProperty()
  map_url = db.StringProperty()
  mobile_map_url = db.StringProperty()
  max_lng = db.FloatProperty()
  mid_lng = db.FloatProperty()
  min_lng = db.FloatProperty()
  max_lat = db.FloatProperty()
  mid_lat = db.FloatProperty()
  min_lat = db.FloatProperty()
  order   = db.IntegerProperty()

class MainPage(webapp.RequestHandler):
  def get(self):
    page = Page.gql('WHERE page_id = :1', 1).get()
    template_values = {
      'list': page.html
    }
    path = os.path.join(os.path.dirname(__file__), 'static/index.html')
    self.response.out.write(template.render(path, template_values))

class AreasAPI(webapp.RequestHandler):
  def get(self):
    page = Page.gql('WHERE page_id = :1', 10).get()
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(page.html)

class NearestAPI(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/xml'
    lat = 0.0
    lng = 0.0
    try:
      lat = float(self.request.get('lat'))
      lng = float(self.request.get('lng'))
    except:
      lat = 0.0
      lng = 0.0
    distances_hash = {}
    distances = []
    for gmap in Map.all():
      distance = pow(gmap.mid_lng-lng,2)+pow(gmap.mid_lat-lat,2)
      distances_hash[str(distance)] = gmap.map_id
      distances.append(distance)
    gmap = Map.gql('WHERE map_id = :1',distances_hash[str(min(distances))] ).get()
    xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>"
    xml+= u"<area>"
    xml+= u"<id>"+NearestAPI.xml_escape(gmap.map_id)+u"</id>"
    xml+= u"<prefecture>"+NearestAPI.xml_escape(gmap.prefecture)+u"</prefecture>"
    xml+= u"<city>"+NearestAPI.xml_escape(gmap.city)+u"</city>"
    xml+= u"<map_url>"+NearestAPI.xml_escape(gmap.map_url)+u"</map_url>"
    xml+= u"<mobile_map_url>"+NearestAPI.xml_escape(gmap.mobile_map_url)+u"</mobile_map_url>"
    xml+= u"<mid_lat>"+str(gmap.mid_lat)+u"</mid_lat>"
    xml+= u"<mid_lng>"+str(gmap.mid_lng)+u"</mid_lng>"
    xml+= u"</area>"
    xml+= u"</document>"
    self.response.out.write(xml)

  @classmethod
  def xml_escape(cls,text):
    NearestAPI.xml_escape_table = {
      u"&": u"&amp;",
      u'"': u"&quot;",
      u"'": u"&apos;",
      u">": u"&gt;",
      u"<": u"&lt;",
    }
    return u"".join(NearestAPI.xml_escape_table.get(c,c) for c in text)

class AllDataAPI(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/xml'
    xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>"
    for gmap in Map.all():
      xml+= u"<area>"
      xml+= u"<id>"+AllDataAPI.xml_escape(gmap.map_id)+u"</id>"
      xml+= u"<prefecture>"+AllDataAPI.xml_escape(gmap.prefecture)+u"</prefecture>"
      xml+= u"<city>"+AllDataAPI.xml_escape(gmap.city)+u"</city>"
      xml+= u"<map_url>"+AllDataAPI.xml_escape(gmap.map_url)+u"</map_url>"
      xml+= u"<mobile_map_url>"+AllDataAPI.xml_escape(gmap.mobile_map_url)+u"</mobile_map_url>"
      xml+= u"<max_lat>"+str(gmap.max_lat)+u"</max_lat>"
      xml+= u"<max_lng>"+str(gmap.max_lng)+u"</max_lng>"
      xml+= u"<mid_lat>"+str(gmap.mid_lat)+u"</mid_lat>"
      xml+= u"<mid_lng>"+str(gmap.mid_lng)+u"</mid_lng>"
      xml+= u"<min_lat>"+str(gmap.min_lat)+u"</min_lat>"
      xml+= u"<min_lng>"+str(gmap.min_lng)+u"</min_lng>"
      xml+= u"<order>"+str(gmap.order)+u"</order>"
      xml+= u"</area>"
    xml+= u"</document>"
    self.response.out.write(xml)

  @classmethod
  def xml_escape(cls,text):
    AllDataAPI.xml_escape_table = {
      u"&": u"&amp;",
      u'"': u"&quot;",
      u"'": u"&apos;",
      u">": u"&gt;",
      u"<": u"&lt;",
    }
    return u"".join(AllDataAPI.xml_escape_table.get(c,c) for c in text)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/apis/all.xml', AllDataAPI),
                                      ('/apis/areas.xml', AreasAPI),
                                      ('/apis/nearest.xml', NearestAPI)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
