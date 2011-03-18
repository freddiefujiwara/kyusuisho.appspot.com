#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gdata.spreadsheet.text_db

class MakeXML:

    def post(self):
      client = gdata.spreadsheet.text_db.DatabaseClient("kyusuisho.appspot.com@gmail.com", "ohsiusuyk")
      db = client.GetDatabases(name=u"kyusuisho.appspot.com")[0]
      return MakeXML.make_xml(db.GetTables(name=u"root")[0]).encode("utf-8")

    @classmethod
    def xml_escape(cls,text):
      MakeXML.xml_escape_table = {
        u"&": u"&amp;",
        u'"': u"&quot;",
        u"'": u"&apos;",
        u">": u"&gt;",
        u"<": u"&lt;",
      }
      return u"".join(MakeXML.xml_escape_table.get(c,c) for c in text)

    @classmethod
    def make_xml(cls,table):
      xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>"
      scripts = []
      current_prefecture = u"";
      for record in table.GetRecords(1, 999999999):
        if current_prefecture != record.content[u"都道府県"]:
          xml += u"" if u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>" == xml else u"</prefecture>" 
          current_prefecture =  record.content[u"都道府県"]
          xml += u"<prefecture><name>"+MakeXML.xml_escape(current_prefecture)+u"</name>"
        xml+= u"<area>"
        xml+= u"<id>"+MakeXML.xml_escape(record.content[u"マップid英数字"])+u"</id>"
        xml+= u"<name>"+MakeXML.xml_escape(record.content[u"市区町村"])+u"</name>"
        xml+= u"<link>"+MakeXML.xml_escape(record.content[u"マップurl"])+u"</link>"
        xml+= u"<mobile_link>"+MakeXML.xml_escape(record.content[u"携帯マップurl"])+u"</mobile_link>"
        xml+= u"</area>"
      xml += u"</prefecture></document>"
      return xml

def main():
    make_xml = MakeXML()
    print make_xml.post()


if __name__ == "__main__":
    main()
