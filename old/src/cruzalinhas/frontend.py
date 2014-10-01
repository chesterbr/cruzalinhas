# -*- coding: utf-8 -*-
#
# Copyright (c) 2010,2011 Carlos Duarte do Nascimento (Chester)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software 
# without restriction, including without limitation the rights to use, copy, modify, merge, 
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons 
# to whom the Software is furnished to do so, subject to the following conditions:
#     
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
#
import os
import base64
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Linha, Hash
from dao import Dao
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

# Páginas do site

class MainPage(webapp.RequestHandler):    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'static', 'cruzalinhas.html')
        self.response.out.write(template.render(path, {}))

        
class RobotsPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('User-agent: *\n')
        self.response.out.write('Disallow: /linhasquepassam.json\n')
        self.response.out.write('Disallow: /linha.json\n')

# API v1
        
class LinhaPage(webapp.RequestHandler):        
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        key = self.request.get("key")
        dao = Dao()
        pontos = json.loads(dao.get_pontos_linha(key))["util"]["ida"]
        pontos_json = json.dumps([[float(ponto[0]) / 1000000, float(ponto[1]) / 1000000]
                                  for ponto in pontos], separators=(',',':'))
        callback = self.request.get("callback");
        if callback:
            pontos_json = callback + "(" + pontos_json + ");"            
        self.response.out.write(pontos_json) 

class LinhasQuePassamPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        dao = Dao()
        linhas_info = []
        for linha in json.loads(dao.get_info_hashes_linhas(lat, lng)):
            linhas_info.append({"url": "http://200.99.150.170/PlanOperWeb/detalheLinha.asp?TpDiaID=0&CdPjOID=%s" % linha["id"],
                                "hashes": linha["hashes"],
                                "nome": linha["info"]["numero"] + " " + 
                                        linha["info"]["nome"]["ida"] + "/" + 
                                        linha["info"]["nome"]["volta"],
                                "key": linha["id"]})
        linhas_info = json.dumps(linhas_info)
        callback = self.request.get("callback")
        if callback:
            linhas_info = callback + "(" + linhas_info + ");"
        self.response.out.write(linhas_info)

# Métodos de upload para o crawler (apenas o admin pode entrar neles)

class TokenPage(webapp.RequestHandler):
    def get(self):
        cookies = ";".join(["%s=%s" % (k, self.request.cookies[k]) for k in self.request.cookies])        
        self.response.out.write(base64.b64encode(cookies))
        
class UploadLinhaPage(webapp.RequestHandler):
    def post(self):
        dao = Dao()
        self.response.out.write(dao.put_linha(id = self.request.get("id"),
                                              deleted = self.request.get("deleted"),
                                              info = self.request.get("info"),
                                              pontos = self.request.get("pontos"),
                                              hashes = self.request.get("hashes")))
                      
class UploadHashPage(webapp.RequestHandler):
    def post(self):
        dao = Dao()
        self.response.out.write(dao.put_hash(hash = self.request.get("hash"),                                             
                                             linhas = self.request.get("linhas")))

            
application = webapp.WSGIApplication([
                                      # Site (páginas abertas fora do /static)
                                      ('/', MainPage),
                                      ('/robots.txt', RobotsPage),
                                      ('/linha.json', LinhaPage),
                                      ('/linhasquepassam.json', LinhasQuePassamPage),
                                      # Páginas de atualização do sptscraper
                                      ('/token', TokenPage),
                                      ('/uploadlinha', UploadLinhaPage),
                                      ('/uploadhash', UploadHashPage)])

                            

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
