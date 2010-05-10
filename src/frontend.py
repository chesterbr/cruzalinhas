from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import scraper
import models
import geohash
from django.utils import simplejson

from geohash import Geohash


class MainPage(webapp.RequestHandler):    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

class ListaPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        for linha in models.Linha.all():
            self.response.out.write('<a href="/linha?linha=%s">%s</a><br/>' % (linha.nome, linha.nome))

class LinhaPage(webapp.RequestHandler):        
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        linha = models.Linha.all().filter("nome =", self.request.get("linha")).fetch(1)[0]
        a = None
        for ponto in linha.pontos:
            g = geohash.Geohash((ponto.lng, ponto.lat))
            if a:
                b = a + g
            else:
                b = None
            self.response.out.write(str(ponto.lat) + "," + str(ponto.lng) + "," + 
                                    str(g) + "," + str(b) + "," + str(ponto.nearhash) + "\n")
            a = g
                        
class RebuildPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Populando...')
        max = self.request.get("max")
        max = int(max) if max else None
        models.popula(scraper.getLinhas(), ignoraExistentes=True, max=max)
        self.response.out.write('ok')
        
class LinhasQuePassamPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        hash = str(geohash.Geohash((lng, lat)))[0:6]
        linhas = {}
        for ponto in models.Ponto.all().filter("nearhash =", hash):
            chave = str(ponto.linha.key())
            if not chave in linhas:
                linhas[chave] = ponto.linha
        self.response.out.write(simplejson.dumps(linhas))
        

#class AtualizaNovasPage(webapp.RequestHandler):
#    def get(self):
#        self.response.headers['Content-Type'] = 'text/plain'
#        self.response.out.write('Atualizando...')
#        models.popula(scraper.getLinhas())
#        self.response.out.write('ok')
            

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/lista', ListaPage),
                                      ('/linha', LinhaPage),
                                      ('/linhasquepassam.json', LinhasQuePassamPage),
#                                      ('/atualiza-novas', AtualizaNovasPage),
                                      ('/rebuild', RebuildPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
