"""Modulo que captura os dados do site da SPTrans"""
# -*- coding: utf-8 -*-
import logging
from contextlib import closing
import re
import time
import urllib2
from BeautifulSoup import BeautifulSoup
import csv
import random

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
        ordem = 0
        _log("Sleeping...")
        time.sleep(5 + random.uniform(1, 5))
        for ponto in linha["pontos"]:
            ordem += 1
            writer.writerow([linha["nome"].encode("utf-8"),
                             linha["url"],
                             ordem,
                             ponto[0],
                             ponto[1]])


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
    arquivoCsv = open("linhas.csv", "wb")
    geraCSV(getLinhas(), arquivoCsv)
    arquivoCsv.close()
