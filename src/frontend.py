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
        path = os.path.join(os.path.dirname(__file__), 'static','cruzalinhas.html')
        self.response.out.write(template.render(path, {}))
        
class ListaPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        for linha in Linha.all():
            self.response.out.write('<a href="/linha.json?key=%s">%s</a><br/>' % (str(linha.key()), linha.nome))

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
        self.response.out.write(pontos_json) 

class LinhasQuePassamPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        # Recupera as chaves das linhas que passam pelo geohash do ponto
        hash = models.calculaNearhash(lng, lat)
        chave_memcache = "hash_linhas_keys_" + hash;
        client = memcache.Client()
        linhas_keys = client.get(chave_memcache)
        if linhas_keys is None:
            result = Hash.all().filter("hash =", hash).fetch(1)
            linhas_keys = result[0].linhas if result else []
            client.add(chave_memcache, linhas_keys)        
        # Converte elas para objetos no formato da resposta e devolve como JSON
        linhas_obj = [self._linha_obj(key) for key in linhas_keys]
        self.response.out.write(simplejson.dumps(linhas_obj))
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


# Desnormalizando os dados que ja estao la (gambiarra)

class GeraHashPage(webapp.RequestHandler):
    def get(self):
        """Popula os objetos Hash para os pontos de uma linha"""
        self.response.headers['Content-Type'] = 'text/plain'
        key = self.request.get("key")
        linha = Linha.get(db.Key(key))
        self.response.out.write('Linha: %s\n' % linha.nome)
        # Percorre os pontos dessa linha, processando os hashes dos segmentos
        nearhashAnterior = ""
        for ponto in linha.pontos:
            if ponto.nearhash:
                if ponto.nearhash == nearhashAnterior:
                    self.response.out.write('hash repetido, pulando %s\n' % ponto.nearhash)
                    continue       
                nearhashAnterior = ponto.nearhash     
#                if len(ponto.nearhash) != 6:
#                    self.response.out.write('hash curto, pulando %s\n' % ponto.nearhash)
                # Se ja existe objeto para o hash, pega ele, senao cria um novo
                hashLista = Hash.all().filter("hash =", ponto.nearhash).fetch(1)
                if hashLista:
                    self.response.out.write('Hash: %s ja existia \n' % ponto.nearhash)
                    hash = hashLista[0]
                else:
                    self.response.out.write('Hash: %s criado \n' % ponto.nearhash)
                    hash = Hash(hash=ponto.nearhash)
                    
                # Se a linha ainda nao esta associada ao objeto-hash, associa
                if str(linha.key()) not in hash.linhas:
                    self.response.out.write('Linha adicionada a lista\n')
                    hash.linhas.append(str(linha.key()))
                    hash.put()
                    
                
class ListaGeraHashPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        for linha in Linha.all():
            self.response.out.write('<a href="/gerahash?key=%s">%s</a><br/>' % (str(linha.key()), linha.nome))
                            
        
        
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/lista', ListaPage),
                                      ('/gerahash', GeraHashPage),
                                      ('/listagerahash', ListaGeraHashPage),
                                      ('/linha.json', LinhaPage),
                                      ('/linhasquepassam.json', LinhasQuePassamPage),
#                                      ('/zap', ZapPage),
                                      ('/clearcache', ClearCachePage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
