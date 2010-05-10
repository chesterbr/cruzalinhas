# -*- coding: utf-8 -*-
from __future__ import division
from google.appengine.ext import db
import math
import geohash

class Linha(db.Model):
    """Uma linha de ônibus. Ex.: 314V-10 Vila Ema - Metrô Liberdade.
    Contém a URL da SPTrans e uma lista de pontos do trajeto, na ordem de desenho"""
    nome = db.StringProperty(required=True)
    url = db.StringProperty(required=True)

class Ponto(db.Model):
    """Um ponto geográfico ordenado de uma linha."""
    linha = db.ReferenceProperty(Linha, collection_name="pontos")
    ordem = db.IntegerProperty(required=True)
    lat = db.FloatProperty(required=True)
    lng = db.FloatProperty(required=True)
    # nearhash é o geohash da caixa que contém este ponto e o anterior, com
    # precisão reduzida para 5 caracteres (~2,5Km)
    nearhash = db.StringProperty(required=False)
    
def popula(linhas, ignoraExistentes=True, max=None):
    """Carrega uma lista de linhas no banco.
    A lista deve conter dicionários com nome, url e uma lista de pontos, i.e., o formato
    retornado pelo scraper (vide scraper.py).
    
    Se ignoraExistentes for False, irá apagar linhas com o mesmo nome e re-inserir. O
    default é ignorar e pular pra próxima."""
    numPopuladas = 0
    for l in linhas:
        if l["pontos"]: # linhas sem pontos não servem
            existentes = Linha.all().filter("nome =", l["nome"]).fetch(999)
            if existentes and ignoraExistentes:
                continue
            for linha in existentes:
                for ponto in Ponto.all().filter("linha =", linha):
                    ponto.delete()
                linha.delete()
            linha = Linha(nome=l["nome"], url=l["url"])
            linha.put()
            n = 1
            geohashAnt = None
            for p in l["pontos"]:
                geohashAtu = geohash.Geohash((p[1], p[0]))
                if geohashAnt:
                    nearhash = str(geohashAnt + geohashAtu)[0:6]
                else:
                    nearhash = None
                Ponto(linha=linha, ordem=n, lat=p[0], lng=p[1], nearhash=nearhash).put()
                n += 1
                geohashAnt = geohashAtu
            numPopuladas += 1
        if max and (numPopuladas == max):
            return
                
def caixa(lat, lng, raio):
    """Recupera as coordenadas da 'caixa' que contém um determinado ponto geográfico,
    permitindo criar queries para pegar apenas pontos dentro da caixa somente com
    filtros de > e < (que são indexáveis pelo GAE)
    
    A conta é aproximada, mas boa o bastante, e tirada de http://phpimpact.codepad.org/HhsJ2mgX
    
    Recebe a latitude, longitude e o raio (em km) da circunferência inscrita na caixa
    (isto é, metade da largura da caixa)
    
    Retorna uma tupla com latitude mínima, latitude máxima, longitude mínima e longitude máxima"""
    lng_min = lng - raio / abs(math.cos(math.radians(lat)) * 111.13)
    lng_max = lng + raio / abs(math.cos(math.radians(lat)) * 111.13)
    lat_min = lat - (raio / 111.13)
    lat_max = lat + (raio / 111.13)
    return (lat_min, lat_max, lng_min, lng_max)

    

    
