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
"""Carrega uma ou mais linhas a partir de um csv no appengine

Exemplo de chamada na linha de comando (trocar o valor de "cookie" por um pego
após um login, e a URL para a do servidor se for o caso):

python2.5 /usr/local/bin/bulkload_client.py --filename=linhas.csv 
  --url=http://localhost:8080/load-linha --kind=Linha 
  --cookie "dev_appserver_login=\"test@example.com:True:185804764220139124118\""

"""
from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from google.appengine.ext import search
from models import Hash, Linha
import geohash
from google.appengine.api.datastore_types import Text

class LinhaLoader(bulkload.Loader):
    def __init__(self):
        bulkload.Loader.__init__(self, 'Linha',
                         [('nome', lambda x: x.decode('utf-8')),
                          ('url', str)])

    def HandleEntity(self, entity):
        for linha in Linha.all().filter("nome =", entity["nome"]).fetch(999):
            for ponto in linha.pontos:
                ponto.delete()
            linha.delete()
        return entity

if __name__ == '__main__':
    bulkload.main(LinhaLoader())

