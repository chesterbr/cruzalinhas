# -*- coding: utf-8 -*-
"""Classe que permite ao bulkload_client.py importar o csv gerado pelo scraper

Exemplo de chamada na linha de comando (trocar o valor de "cookie" por um pego
após um login, e a URL para a do servidor conforme o caso):

python2.5 /usr/local/bin/bulkload_client.py --filename=linhas.csv 
  --url=http://localhost:8080/load --kind=Ponto 
  --cookie "dev_appserver_login=\"test@example.com:True:185804764220139124118\""

"""
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
        ponto = Ponto(ordem=entity["ordem"], lat=entity["lat"], lng=entity["lng"])
        
        # Se nao tem a linha, cria
        linhas = Linha.all().filter("nome =", entity["linha_nome"]).fetch(1)
        if linhas:
            linha = linhas[0]
        else:
            linha = Linha(nome=entity["linha_nome"], url=entity["linha_url"])
            linha.put()
        ponto.linha = linha
            
        # Calcula o geohash da menor região que contém os dois pontos e corta
        # pra abranger uma área razoável (<2km, cf. http://en.wikipedia.org/wiki/Geohash)
        #pontoAnt = linha.pontos[-1]
        pontosAnt = Ponto.all().filter("linha =", linha).filter(
            "ordem =", ponto.ordem - 1).fetch(1)
        if pontosAnt:
            pontoAnt = pontosAnt[0]
            ponto.nearhash = str(geohash.Geohash((pontoAnt.lng, pontoAnt.lat)) + 
                                 geohash.Geohash((ponto.lng, ponto.lat)))[0:6]
        
        # Cria o ponto e fala pro bulk_uploader desencanar
        ponto.put()
        return None

if __name__ == '__main__':
    bulkload.main(PontoLoader())

