#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gdata.spreadsheet.text_db

class MakeHTML:

    def post(self):
      client = gdata.spreadsheet.text_db.DatabaseClient('kyusuisho.appspot.com@gmail.com', 'ohsiusuyk')
      db = client.GetDatabases(name=u'kyusuisho.appspot.com')[0]
      return MakeHTML.make_html(db.GetTables(name=u'root')[0]).encode("utf-8")

    @classmethod
    def html_escape(cls,text):
      MakeHTML.html_escape_table = {
        #  u"&": u"&amp;",
        u'"': u"&quot;",
        u"'": u"&apos;",
        u">": u"&gt;",
        u"<": u"&lt;",
      }
      return u"".join(MakeHTML.html_escape_table.get(c,c) for c in text)

    @classmethod
    def make_html(cls,table):
      html = u""
      scripts = []
      current_prefecture = u"";
      for record in table.GetRecords(1, 999999999):
        if current_prefecture != record.content[u"都道府県"]:
          html += u"" if u"" == html else u"</ul></li>" 
          current_prefecture =  record.content[u"都道府県"]
          html += u"<li>"+MakeHTML.html_escape(current_prefecture)+u"<ul>"
        html+= u'<li>'
        html+= u'<a href="'+MakeHTML.html_escape(record.content[u"携帯マップurl"])+u'"'
        html+= u' id="'+MakeHTML.html_escape(record.content[u"マップid英数字"])+u'"'
        html+= u' class="link"'
        html+= u' name="'+MakeHTML.html_escape(record.content[u"マップid英数字"])+u'">'
        html+= MakeHTML.html_escape(record.content[u"市区町村"])+u'</a></li>'
        scripts.append(u'"'+MakeHTML.html_escape(record.content[u"マップid英数字"])+u'":"'+MakeHTML.html_escape(record.content[u"マップurl"])+u'"')
      html += u'</ul></li><script type="text/javascript" id="gmaps">l={'
      html += u",".join(scripts)
      html += u'};</script>'
      return html

def main():
    make_html = MakeHTML()
    print make_html.post()


if __name__ == '__main__':
    main()
