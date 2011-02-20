# -*- coding: utf-8 -*-
#
# Copyright (c) 2010, 2011 Carlos Duarte do Nascimento (Chester)
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

from django.utils import simplejson as json
from geohash import Geohash
from models import Linha, Hash
from google.appengine.api import memcache
import sys

class Dao:
    """Classe de acesso aos dados das linhas (com uso do memcache e retornando JSON)"""
    
    cache = memcache.Client()
    
    def get_info_linha(self, linha_id):
        """Retorna objeto JSON com as infos gerais da linha"""
        chave_memcache = "info_por_linha_id_" + linha_id
        linha = self.cache.get(chave_memcache)
        if linha is None:
            linha = Linha.all().filter("id =", linha_id).fetch(1).info
            self.cache.add(chave_memcache, linha)
        return linha
    
    def get_info_linhas(self, lat, lng):
        """Retorna array JSON com a info das linhas que passam num ponto"""
        hash = str(Geohash((lng, lat)))[0:6]
        chave_memcache = "linhas_por_hash_" + hash;
        linhas_ids = self.cache.get(chave_memcache)
        if linhas_ids is None:
            result = Hash.all().filter("hash =", hash).fetch(1)
            linhas_ids = json.loads(result[0].linhas) if result else []
            self.cache.add(chave_memcache, linhas_ids)        
        #TODO converter para array json (esse array é python)
        return [self.get_info_linha(linha) for linha in linhas_ids]
    
    def put_linha(self, id, deleted, info, pontos, hashes):        
        """Atualiza uma linha no banco (incluindo delete) e anula seu cache.
           O cache dos hashes não é atualizado (supõe-se que eles também serão
           atualizados no final). Retorna mensagem consumível pelo sptscraper"""
        try:
            id = int(id)
            self.cache.delete("info_por_linha_id_%s" % id)
            if deleted == "true":
                linha = Linha.all().filter("id =", id).fetch(1)
                if linha:
                    linha.delete()
                    return "OK LINHA DELETE %s " % id
                else:
                    return "OK LINHA DELETE %s (NAO EXISTIA)" % id
            else:
                linha = Linha(id = id, info = info, pontos = pontos, hashes = hashes)
                linha.put()
                return "OK LINHA UPLOAD %s " % id
        except:
            return "ERRO LINHA: %s" % sys.exc_info()[1]

    def put_hash(self, hash, linhas):        
        """Atualiza um hash no banco (mesmo vazio) e anula seu cache.
           Retorna mensagem consumível pelo sptscraper"""
        try:
            self.cache.delete("linhas_por_hash_" + hash)
            hash = Hash(hash = hash, linhas = linhas)
            hash.put()
            return "OK HASH UPLOAD %s " % id
        except:
            return "ERRO HASH: %s" % sys.exc_info()[1]

    def get_pontos_linha(self, linha_id):
        """Retorna objeto JSON com os pontos do trajeto para cada dia e sentido"""
        pass
#        chave_memcache = "pontos_por_linha_id_" + linha_id;
#        pontos_json = self.cache.get(chave_memcache)
#        if pontos_json is None:
#            linha = Linha.get(db.Key(key))
#            pontos = Ponto.all().filter("linha = ", linha).order("ordem")
#            pontos_json = simplejson.dumps([(ponto.lat, ponto.lng) for ponto in pontos])
#            self.cache.add(chave_memcache, pontos_json)

