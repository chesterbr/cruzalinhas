from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from google.appengine.ext import search
from models import Ponto, Linha
import geohash

class PontoLoader(bulkload.Loader):
    def __init__(self):
        bulkload.Loader.__init__(self, 'Ponto',
                         [('linha_nome', str),
                          ('linha_url', str),
                          ('ordem', int),
                          ('lat', float),
                          ('lng', float),
                          ])

    def HandleEntity(self, entity):
        ponto = Ponto(ordem=entity.ordem, lat=entity.lat, lng=entity.lng)
        
        # Se nao tem a linha, cria
        linha = Linha.all().filter("nome =", entity.linha_nome).fetch(1)
        if not linha:
            linha = Linha(nome=entity.linha_nome, url=entity.linha_url)
            linha.put()
            
        # Calcula o geohash da menor região que contém os dois pontos e corta
        # pra abranger uma área razoável (<2km, cf. http://en.wikipedia.org/wiki/Geohash)
        pontoAnt = Ponto.all().filter("linha =", linha).filter(
            "ordem =", ponto.ordem - 1).fetch(1)
        if pontoAnt:
            ponto.nearhash = str(geohash.Geohash(pontoAnt.lng, pontoAnt.lat) + 
                                 geohash.Geohash(ponto.lng, ponto.lat))[0:6]
        
        return ponto

    if __name__ == '__main__':
        bulkload.main(PontoLoader())
