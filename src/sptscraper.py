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

import os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

class SptScraper:

    base_href = r"http://200.99.150.170/PlanOperWeb/"
    pag_linhas = "linhaselecionada.asp"
    
    index_file = "index.html"
    data_dir = "data"
    
    def _assert_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
    
    def clean_html(self):
        """Apaga os downloads já realizados"""
        self._assert_data_dir()
        for file in os.listdir(self.data_dir):
            if file.endswith(".html"):
                os.unlink(os.path.join(self.data_dir,file))
        
    def download_index(self):
        """Baixa a página-índice (que contém a lista das linhas), verifica sua integridade
        e retorna a quantidade de linhas encontradas."""
        html = urllib2.urlopen(self.base_href + self.pag_linhas).read()
        soup = BeautifulSoup(html)
        numLinhas = 0
        for elem in soup.findAll("a", attrs={"class":re.compile("linkLinha|linkDetalhes")}):
            if elem["class"] == "linkLinha":
                numLinhas += 1
        if numLinhas > 0:
            self._assert_data_dir()
            arq = open(os.path.join(self.data_dir, self.index_file), "w")
            arq.writelines(html)
        return numLinhas
    
    def lista_linhas(self):
        """Retorna uma lista com o nome e a URL de cada linha, a partir da página-índice
        (que já deve ter sido baixada via download_index) 
        html = open(os.path.join(self.data_dir, self.index_file)).read()
        soup = BeautifulSoup(html)
        linhas = []
        for elem in soup.findAll("a", attrs={"class":re.compile("linkLinha|linkDetalhes")}):
            if elem["class"] == "linkLinha":
                nome = elem.string.replace("Linha: ", "").strip()
            elif elem["class"] == "linkDetalhes":
                url = self.base_href + elem["href"]
                linha = {
                    "nome" : nome,
                    "url" : url }
                linhas.append(linha)
        return linhas

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
