from django.utils import simplejson
from geohash import Geohash
from google.appengine.api import memcache
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Linha, Ponto
import scraper
import geohash
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
            pontos = Linha.get(db.Key(key)).pontos
            linha_json = simplejson.dumps([(ponto.lat, ponto.lng) for ponto in pontos])
            client.add(key, linha_json)
        self.response.out.write(linha_json) 

class LinhasQuePassamPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        hash = str(geohash.Geohash((lng, lat)))[0:6]
        linhas = {}
        for ponto in Ponto.all().filter("nearhash =", hash):
            chave = str(ponto.linha.key())
            if not chave in linhas:
                linhas[chave] = {
                                 "key" : str(ponto.linha.key()),
                                 "nome" : ponto.linha.nome,
                                 "url" : ponto.linha.url}
        self.response.out.write(simplejson.dumps(linhas.values()))

# Crawler stuff

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
                        
class RebuildPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Populando...')
        max = self.request.get("max")
        max = int(max) if max else None
        models.popula(scraper.getLinhas(), ignoraExistentes=True, max=max)
        self.response.out.write('ok')
        
        
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/lista', ListaPage),
                                      ('/linha.json', LinhaPage),
                                      ('/linhasquepassam.json', LinhasQuePassamPage),
                                      ('/zap', ZapPage),
                                      ('/rebuild', RebuildPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
