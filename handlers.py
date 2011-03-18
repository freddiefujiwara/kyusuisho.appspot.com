import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Page(db.Model):
  page_id = db.IntegerProperty()
  html = db.TextProperty()

class MainPage(webapp.RequestHandler):
  def get(self):
    page = Page.gql('WHERE page_id = :1', 1).get()
    template_values = {
      'list': page.html
    }
    path = os.path.join(os.path.dirname(__file__), 'static/index.html')
    self.response.out.write(template.render(path, template_values))

class APIPage(webapp.RequestHandler):
  def get(self):
    page = Page.gql('WHERE page_id = :1', 10).get()
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(page.html)

application = webapp.WSGIApplication(
                                     [('/', MainPage),('/api.xml', APIPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
