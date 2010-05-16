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
"""Modulo que captura os dados do site da SPTrans

Pode ser chamado de forma indepentente (o parâmetro opcional indica a quantidade de
linhas a 'pular', útil para retomar capturas interrompidas), ou a partir de outros
códigos (o método getLinhas() é a chave para isso) - neste caso, tome o cuidado de
não sobrecarregar o site)"""
import logging
from contextlib import closing
import re
import time
import urllib2
from BeautifulSoup import BeautifulSoup
import csv
import random
import sys
from sre_parse import isdigit

BASE_HREF = r"http://200.99.150.170/PlanOperWeb/"
PAG_LINHAS = "linhaselecionada.asp"
    
def getLinhas():
    """Recupera as linhas (cada linha tem nome, uma coleção iterável de pontos e uma url)
    
    A leitura do 1o. item gera uma chamada HTTP. As outras não fazem isso, mas a leitura
    da propriedade "pontos" o fará. Dessa forma é possível "pular" linhas e só ir nos
    pontos das que interessam, sem gerar tráfego HTTP desnecessário."""
    _log("Lendo lista de linhas")
    html = urllib2.urlopen(BASE_HREF + PAG_LINHAS).read()
    _log("Processando HTML")
    soup = BeautifulSoup(html)
    _log("Navegando links")
    for elem in soup.findAll("a", attrs={"class":re.compile("linkLinha|linkDetalhes")}):
            if elem["class"] == "linkLinha":
                nome = elem.string.replace("Linha: ", "").strip()
                pontos = _getPontos(BASE_HREF + 
                                    re.match(r"javascript:CarregarMapa\('(.*)'\)",
                                             elem["onclick"]).group(1))
            elif elem["class"] == "linkDetalhes":
                url = BASE_HREF + elem["href"]
                linha = {
                    "nome" : nome,
                    "pontos" : pontos,
                    "url" : url }
                yield linha

def geraCSV(linhas, stream):
    writer = csv.writer(stream)    
    for linha in linhas:
        _log("Sleeping...")
        time.sleep(20 + random.uniform(1, 10))
        _log("Iniciando linha: %s" % linha["nome"])
        writer.writerow([linha["nome"].encode("utf-8"),
                         linha["url"],
                         [p for p in linha["pontos"]]])


def _getPontos(url):
    """Retorna o generator de uma coleção de pontos (latitude e longitude) para uma
    linha de ônibus, identificada pela URL"""
    _log("Processando linha: " + url)
    urlDs = re.sub(r"&TpDiaID=.", "&TpDiaID=0", url, 1) # Garante rota de dia da semana
    if url != urlDs:
        url = urlDs
        _log("Link convertido para segunda-feira:" + url)
    html = urllib2.urlopen(url).read()
    # Os pontos estão na string JavaScript coor, que consiste em uma lista de  
    # latitudes e longitudes, separados por || e convertidos para inteiros
    # (i.e., multiplicados por 1 milhão). 
    lista_js = re.search(r'var coor = "(.*?)"', html).group(1)
    if not lista_js:
        _log("Aviso: linha sem pontos. URL: " + url)
        return
    lista = [float(x) / 1000000 for x in lista_js.split(r"||")]
    i = iter(lista)
    for lat in i:
        yield (lat, i.next())
#    return [(lat, i.next()) for lat in i]

def _log(string):
    print(string)
    logging.debug(string)

            

if __name__ == "__main__":
    print "Gerando linhas.csv..."
    linhas = getLinhas()
    nargs = len(sys.argv)    
    if nargs > 2 or (nargs==2 and not isdigit(sys.argv[1])):
        print "Uso: scraper.py [no. de linhas a pular no inicio]"
        sys.exit()
    if nargs == 2:
        for i in range(0, int(sys.argv[1])):
            _log("Pulando: %s" % linhas.next()["nome"])
    arquivoCsv = open("linhas.csv", "ab")
    geraCSV(linhas, arquivoCsv)
    arquivoCsv.close()
