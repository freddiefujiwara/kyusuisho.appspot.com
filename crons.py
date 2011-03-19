#!/usr/bin/env python
# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from django.utils import simplejson
import urllib
import gdata.spreadsheet.text_db

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

class CrawlMap:

    def crawl(self):
      for gmap in Map.all():
        json = urllib.urlopen(u"http://pipes.yahoo.com/pipes/pipe.run?_id=b7b3030968c2dcaf1560c469a6d57340&_render=json&map_url=%s" % (urllib.quote(gmap.map_url))).read()
        data = simplejson.loads(json)
        lngs = []
        lats = []
        for record in data["value"]["items"]:
          lnglat = record["author"].split(",")
          lngs.append(lnglat[0])
          lats.append(lnglat[1])
        if 0 < len(lngs) and 0 < len(lats):
          gmap.max_lng = float(max(lngs))
          gmap.min_lng = float(min(lngs))
          gmap.mid_lng = gmap.min_lng + (gmap.max_lng-gmap.min_lng)/2
          gmap.max_lat = float(max(lats))
          gmap.min_lat = float(min(lats))
          gmap.mid_lat = gmap.min_lat + (gmap.max_lat-gmap.min_lat)/2
        else:
          gmap.max_lng = 0.0
          gmap.min_lng = 0.0
          gmap.mid_lng = 0.0
          gmap.max_lat = 0.0
          gmap.min_lat = 0.0
          gmap.mid_lat = 0.0
        gmap.put()

class CrawlSpread:

    def crawl(self):
      client = gdata.spreadsheet.text_db.DatabaseClient('kyusuisho.appspot.com@gmail.com', 'ohsiusuyk')
      db = client.GetDatabases(name=u'kyusuisho.appspot.com')[0]
      table = db.GetTables(name=u'root')[0]
      xml=CrawlSpread.make_xml(table)

      page = Page.gql('WHERE page_id = :1', 10).get()
      if page is None:
        page = Page(page_id=10,html=xml)
      else:
        page.html = xml
      page.put()

      html=CrawlSpread.crawl_spread(table)
      page = Page.gql('WHERE page_id = :1', 1).get()
      if page is None:
        page = Page(page_id=1,html=html)
      else:
        page.html = html
      page.put()

      order = 0
      for record in table.GetRecords(1, 999999999):
        gmap = Map.gql('WHERE map_id = :1',record.content[u"マップid英数字"] ).get()
        if gmap is None:
          gmap = Map(map_id        =record.content[u"マップid英数字"],
                     prefecture    =record.content[u"都道府県"],
                     city          =record.content[u"市区町村"],
                     map_url       =record.content[u"マップurl"],
                     mobile_map_url=record.content[u"携帯マップurl"],
                     max_lng = 0.0,
                     min_lng = 0.0,
                     mid_lng = 0.0,
                     max_lat = 0.0,
                     min_lat = 0.0,
                     mid_lat = 0.0,
                     order         = order
                    )
        else:
          gmap.prefecture    =record.content[u"都道府県"]
          gmap.city          =record.content[u"市区町村"]
          gmap.map_url       =record.content[u"マップurl"]
          gmap.mobile_map_url=record.content[u"携帯マップurl"]
          gmap.order         = order
        gmap.put()
        order = order + 1
              

    @classmethod
    def html_escape(cls,text):
      CrawlSpread.html_escape_table = {
        #  u"&": u"&amp;",
        u'"': u"&quot;",
        u"'": u"&apos;",
        u">": u"&gt;",
        u"<": u"&lt;",
      }
      return u"".join(CrawlSpread.html_escape_table.get(c,c) for c in text)

    @classmethod
    def xml_escape(cls,text):
      CrawlSpread.xml_escape_table = {
        u"&": u"&amp;",
        u'"': u"&quot;",
        u"'": u"&apos;",
        u">": u"&gt;",
        u"<": u"&lt;",
      }
      return u"".join(CrawlSpread.xml_escape_table.get(c,c) for c in text)

    @classmethod
    def crawl_spread(cls,table):
      html = u""
      scripts = []
      current_prefecture = u"";
      for record in table.GetRecords(1, 999999999):
        if current_prefecture != record.content[u"都道府県"]:
          html += u"" if u"" == html else u"</ul></li>" 
          current_prefecture =  record.content[u"都道府県"]
          html += u"<li>"+CrawlSpread.html_escape(current_prefecture)+u"<ul>"
        html+= u'<li>'
        html+= u'<a href="'+CrawlSpread.html_escape(record.content[u"携帯マップurl"])+u'"'
        html+= u' id="'+CrawlSpread.html_escape(record.content[u"マップid英数字"])+u'"'
        html+= u' class="link"'
        html+= u' name="'+CrawlSpread.html_escape(record.content[u"マップid英数字"])+u'">'
        html+= CrawlSpread.html_escape(record.content[u"市区町村"])+u'</a></li>'
        scripts.append(u'"'+CrawlSpread.html_escape(record.content[u"マップid英数字"])+u'":"'+CrawlSpread.html_escape(record.content[u"マップurl"])+u'"')
      html += u'</ul></li><script type="text/javascript" id="gmaps">l={'
      html += u",".join(scripts)
      html += u'};</script>'
      return html

    @classmethod
    def make_xml(cls,table):
      xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>"
      scripts = []
      current_prefecture = u"";
      for record in table.GetRecords(1, 999999999):
        if current_prefecture != record.content[u"都道府県"]:
          xml += u"" if u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>" == xml else u"</prefecture>" 
          current_prefecture =  record.content[u"都道府県"]
          xml += u"<prefecture><name>"+CrawlSpread.xml_escape(current_prefecture)+u"</name>"
        xml+= u"<area>"
        xml+= u"<id>"+CrawlSpread.xml_escape(record.content[u"マップid英数字"])+u"</id>"
        xml+= u"<name>"+CrawlSpread.xml_escape(record.content[u"市区町村"])+u"</name>"
        xml+= u"<link>"+CrawlSpread.xml_escape(record.content[u"マップurl"])+u"</link>"
        xml+= u"<mobile_link>"+CrawlSpread.xml_escape(record.content[u"携帯マップurl"])+u"</mobile_link>"
        xml+= u"</area>"
      xml += u"</prefecture></document>"
      return xml

class CrawlMapHandler(webapp.RequestHandler):
    
    def __init__(self):
        self.application = CrawlMap()
    
    def get(self):
        json = self.application.crawl()
        self.response.out.write(json)

class CrawlSpreadHandler(webapp.RequestHandler):
    
    def __init__(self):
        self.application = CrawlSpread()
    
    def get(self):
        self.application.crawl()

def main():
    application = webapp.WSGIApplication([('/crons/crawl_spread', CrawlSpreadHandler),('/crons/crawl_map', CrawlMapHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
