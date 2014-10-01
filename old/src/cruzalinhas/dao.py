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
    
    def get_pontos_linha(self, linha_id):
        """Retorna objeto JSON com os pontos do trajeto para cada dia e sentido"""
        chave_memcache = "pontos_por_linha_id_%s" % linha_id
        pontos = self.cache.get(chave_memcache)
        if pontos is None:
            result = Linha.all().filter("id =", int(linha_id)).fetch(1)
            if result:
                pontos = result[0].pontos
                self.cache.add(chave_memcache, pontos)
        return pontos

    def get_info_hashes_linha(self, linha_id):
        """Retorna objeto JSON com as infos gerais e hashes da linha"""
        chave_memcache = "info_por_linha_id_%s" % linha_id
        linha = self.cache.get(chave_memcache)
        if linha is None:
            result = Linha.all().filter("id =", int(linha_id)).fetch(1)
            if result:
                linha = '{"id":%s,"info":%s,"hashes":%s}' % (linha_id, result[0].info,result[0].hashes)
                self.cache.add(chave_memcache, linha)
        return linha
    
    def get_info_hashes_linhas(self, lat, lng):
        """Retorna array JSON com as infos e hashes das linhas que passam num ponto"""
        hash = str(Geohash((lng, lat)))[0:6]
        chave_memcache = "linhas_por_hash_%s" % hash;
        linhas_ids = self.cache.get(chave_memcache)
        if linhas_ids is None:
            result = Hash.all().filter("hash =", hash).fetch(1)
            linhas_ids = json.loads(result[0].linhas) if result else []
            self.cache.add(chave_memcache, linhas_ids)        
        return json.dumps([json.loads(self.get_info_hashes_linha(linha)) for linha in linhas_ids], separators=(',',':'))
    
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
                linha = Linha.all().filter("id =", id).fetch(1)
                if linha:
                    linha = linha[0]
                    linha.info = info
                    linha.pontos = pontos
                    linha.hashes = hashes
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
            hash_obj = Hash.all().filter("hash =", hash).fetch(1)
            if hash_obj:
                hash_obj = hash_obj[0]
                hash_obj.linhas = linhas
            else:
                hash_obj = Hash(hash = hash, linhas = linhas)
            hash_obj.put()
            return "OK HASH UPLOAD %s " % id
        except:
            return "ERRO HASH: %s" % sys.exc_info()[1]

