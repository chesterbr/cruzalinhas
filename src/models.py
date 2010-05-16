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
    def setNearhash(self, pontoAnt):
        self.nearhash = str(geohash.Geohash((pontoAnt.lng, pontoAnt.lat)) + 
                            geohash.Geohash((self.lng, self.lat)))[0:6]        
    

                


    

    
