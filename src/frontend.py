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
from django.utils import simplejson
from geohash import Geohash
from google.appengine.api import memcache
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Linha, Ponto, Hash
import scraper
import models
import os
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'static', 'cruzalinhas.html')
        self.response.out.write(template.render(path, {}))
        
class LinhaPage(webapp.RequestHandler):        
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        key = self.request.get("key")
        chave_memcache = "pontos_json_" + key;
        client = memcache.Client()
        pontos_json = client.get(chave_memcache)
        if pontos_json is None:
            linha = Linha.get(db.Key(key))
            pontos = Ponto.all().filter("linha = ", linha).order("ordem")
            pontos_json = simplejson.dumps([(ponto.lat, ponto.lng) for ponto in pontos])
            client.add(chave_memcache, pontos_json)
        callback = self.request.get("callback");
        if callback:
            pontos_json = callback + "(" + pontos_json + ");"            
        self.response.out.write(pontos_json) 

class LinhasQuePassamPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        # Recupera as chaves das linhas que passam pelo geohash do ponto
        hash = str(Geohash((lng, lat)))[0:6]
        chave_memcache = "hash_linhas_keys_" + hash;
        client = memcache.Client()
        linhas_keys = client.get(chave_memcache)
        if linhas_keys is None:
            result = Hash.all().filter("hash =", hash).fetch(1)
            linhas_keys = result[0].linhas if result else []
            client.add(chave_memcache, linhas_keys)        
        # Converte elas para objetos no formato da resposta e devolve como JSON
        linhas_obj = [self._linha_obj(key) for key in linhas_keys]
        linhas_json = simplejson.dumps(linhas_obj)
        callback = self.request.get("callback");
        if callback:
            linhas_json = callback + "(" + linhas_json + ");"
        self.response.out.write(linhas_json)
    def _linha_obj(self, key):
        """Monta info da linha no formato da resposta, usando o cache se possível"""
        client = memcache.Client()
        chave_memcache = "linha_json_" + key
        linha_obj = client.get(chave_memcache)
        if linha_obj is None:
            linha = Linha.get(db.Key(key))
            linha_obj = {
                          "key" : str(linha.key()),
                          "nome" : linha.nome,
                          "url" : linha.url,
                          "hashes" : linha.hashes()}
            client.add(chave_memcache, linha_obj)
        return linha_obj

# sptcrawler

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

class ZapPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Apagando hashes...')
        while Hash.all().fetch(1):
            db.delete(Hash.all().fetch(100))
        self.response.out.write('Apagando linhas...')
        while Linha.all().fetch(1):
            db.delete(Linha.all().fetch(100))
        self.response.out.write('Ok')

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
