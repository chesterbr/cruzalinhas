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
from google.appengine.ext import db

class Linha(db.Model):
    """Uma linha de ônibus. Ex.: 314V-10 Vila Ema - Metrô Liberdade.
    As infos e pontos são guardadas como JSON"""
    id = db.IntegerProperty(required=True)
    info = db.StringProperty(required=True)
    pontos = db.StringProperty(required=True)
    hashes = db.StringListProperty(required=True)
    #nome = db.StringProperty(required=True)
    #url = db.StringProperty(required=True)
#    _hashes_list = db.StringListProperty()
#    def hashes(self):
#        """Recupera todos os nearhashes (vide abaixo) dos pontos dessa linha, sem repetir.
#           Se a propriedade não existir, calcula (foi feito assim pq é um late thought)"""
#        if not self._hashes_list:
#            set_hashes = set([ponto.nearhash for ponto in self.pontos])
#            set_hashes.remove(None) # O 1o. ponto tem nearhash nulo
#            self._hashes_list = [hash for hash in set_hashes]
#            self.put()
#        return self._hashes_list

#class Ponto(db.Model):
#    """Um ponto geográfico ordenado de uma linha."""
#    linha = db.ReferenceProperty(Linha, collection_name="pontos")
#    ordem = db.IntegerProperty(required=True)
#    lat = db.FloatProperty(required=True)
#    lng = db.FloatProperty(required=True)
#    # nearhash é o geohash da caixa que contém este ponto e o anterior, com
#    # precisão reduzida para 5 caracteres (~2,5Km)
#    nearhash = db.StringProperty(required=False)
#    def setNearhash(self, pontoAnt):
#        self.nearhash = str(geohash.Geohash((pontoAnt.lng, pontoAnt.lat)) + 
#                            geohash.Geohash((self.lng, self.lat)))[0:6]
                            
class Hash(db.Model):
    hash = db.StringProperty(required=True)
    linhas = db.StringProperty(required=True)                             
                            
#def calculaNearhash(lng, lat):
#    """Calcula um geohash para uma coordenada compatível com a propriedade nearhash,
#    isto é, algo que, se igual a um nearhash da linha, indica que o ponto passa pela
#    mesma"""
#    return str(geohash.Geohash((lng, lat)))[0:6]       
#    
#
#                

    

    
