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
from models import Linha, Ponto
import scraper
import models

class MainPage(webapp.RequestHandler):    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

class ListaPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        for linha in Linha.all():
            self.response.out.write('<a href="/linha.json?key=%s">%s</a><br/>' % (str(linha.key()), linha.nome))

class LinhaPage(webapp.RequestHandler):        
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        key = self.request.get("key")
        client = memcache.Client()
        linha_json = client.get(key)
        if linha_json is None:
            linha = Linha.get(db.Key(key))
            pontos = Ponto.all().filter("linha = ", linha).order("ordem")
            linha_json = simplejson.dumps([(ponto.lat, ponto.lng) for ponto in pontos])
            client.add(key, linha_json)
        self.response.out.write(linha_json) 

class LinhasQuePassamPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        hash = models.calculaNearhash(lng,lat)
        linhas = {}
        for ponto in Ponto.all().filter("nearhash =", hash):
            chave = str(ponto.linha.key())
            if not chave in linhas:
                linhas[chave] = {
                                 "key" : str(ponto.linha.key()),
                                 "nome" : ponto.linha.nome,
                                 "url" : ponto.linha.url,
                                 "hashes" : self._hashes(ponto.linha)}
        self.response.out.write(simplejson.dumps(linhas.values()))
    def _hashes(self, linha):
        """Recupera todos os nearhashes de uma linha, usando o cache se possível"""
        client = memcache.Client()
        chave = "hashes_"+str(linha.key)
        hashes = client.get(chave)
        if hashes is None:
            hashes = linha.hashes()
            client.add(chave, hashes)
        return hashes


# Crawler stuff

class ClearCachePage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Limpando cache...')
        memcache.Client().flush_all()
        self.response.out.write('Ok')

class ZapPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Apagando pontos...')
        while Ponto.all().fetch(1):
            db.delete(Ponto.all().fetch(100))
        self.response.out.write('Apagando linhas...')
        while Linha.all().fetch(1):
            db.delete(Linha.all().fetch(100))
        self.response.out.write('Ok')
                        
        
        
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/lista', ListaPage),
                                      ('/linha.json', LinhaPage),
                                      ('/linhasquepassam.json', LinhasQuePassamPage),
                                      ('/zap', ZapPage),
                                      ('/clearcache', ClearCachePage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
