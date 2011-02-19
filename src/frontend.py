# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Carlos Duarte do Nascimento (Chester)
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
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Linha, Hash
import os
from dao import Dao
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'static', 'cruzalinhas.html')
        self.response.out.write(template.render(path, {}))

# API
# TODO compatibilizar com a versão antiga (os novos crio num v2 ou algo assim
# (basta extrair do JSON a parte que interessa, considerar default dia útil e ida)
        
class LinhaPage(webapp.RequestHandler):        
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        key = self.request.get("key")
        dao = Dao()
        pontos_json = dao.get_pontos_linha(key)
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
        linhas_info = dao.get_info_linhas(lat, lng)
        callback = self.request.get("callback");
        if callback:
            linhas_info = callback + "(" + linhas_info + ");"
        self.response.out.write(linhas_info)

# Métodos de upload para o crawler

class UploadLinhaPage(webapp.RequestHandler):
    def get(self):
        if self.request.get("deleted") == "true":
            linha = Linha.all().filter("id =", self.request.get("id")).fetch(1)
            if linha:
                linha.delete()
            print "LINHA DELETE OK " + linha
        else:
            linha = Linha(id = int(self.request.get("id")),
                          info = self.request.get("info"),
                          pontos = self.request.get("pontos"),
                          hashes = self.request.get("hashes"))
            linha.put()
            print "LINHA UPLOAD OK " + linha
                      
class UploadHashPage(webapp.RequestHandler):
    def get(self):
        if self.request.get("deleted") == "true":
            hash = Hash.all().filter("linha =", self.request.get("linha")).fetch(1)
            if hash:
                hash.delete()
            print "HASH DELETE OK " + hash
        else:
            hash = Hash(hash = int(self.request.get("hash")),
                        linhas = self.request.get("linhas"))
            print "HASH UPLOAD OK " + hash

# Não sei se vou ficar com esse cara, ele é perigoso
#class ZapPage(webapp.RequestHandler):
#    def get(self):
#        self.response.headers['Content-Type'] = 'text/plain'
#        self.response.out.write('Apagando hashes...')
#        while Hash.all().fetch(1):
#            db.delete(Hash.all().fetch(100))
#        self.response.out.write('Apagando linhas...')
#        while Linha.all().fetch(1):
#            db.delete(Linha.all().fetch(100))
#        self.response.out.write('Ok')

class RobotsPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('User-agent: *\n')
        self.response.out.write('Disallow: /linhasquepassam.json\n')
        self.response.out.write('Disallow: /linha.json\n')
            
application = webapp.WSGIApplication([
                                      # Site (páginas abertas fora do /static)
                                      ('/', MainPage),
                                      ('/robots.txt', RobotsPage),
                                      ('/linha.json', LinhaPage),
                                      ('/linhasquepassam.json', LinhasQuePassamPage)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
