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
import urlparse
import re
import sqlite3
import time
try:
    import json
except ImportError:
    import simplejson as json 

class SptScraper:

    base_href = r"http://200.99.150.170/PlanOperWeb/"
    pag_linhas = "linhaselecionada.asp"
    
    index_file = "index.html"
    data_dir = "data"
    db_name = "linhas.sqlite"
    
    DIAS = ["util", "sabado", "domingo"]
    SENTIDOS = ["ida", "volta"]
    PERIODOS = ["manha", "entrepico", "tarde"]
    
    DICT_DIAS = dict(zip("USD", DIAS))
    DICT_SENTIDOS = dict(zip("IV", SENTIDOS))
    
    _conn = None
    _cursor = None
    
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
        (que já deve ter sido baixada via download_index) """
        html = open(os.path.join(self.data_dir, self.index_file)).read()
        soup = BeautifulSoup(html)
        linhas = []
        for elem in soup.findAll("a", attrs={"class":re.compile("linkLinha|linkDetalhes")}):
            if elem["class"] == "linkLinha":
                nome = elem.string.replace("Linha: ", "").strip()
            elif elem["class"] == "linkDetalhes":
                parsed_url = urlparse.urlparse(self.base_href + elem["href"])
                params = dict([part.split('=') for part in parsed_url[4].split('&')])
                linha = {
                    "nome" : nome,
                    "id" : params["CdPjOID"] }
                linhas.append(linha)
        return linhas

    def download_linha(self, id):
        """Baixa os arquivos relacionados a uma linha identificado por "id". Os arquivos são
           salvos no formato id-tipo-dia-sentido.html, onde tipo é M(apa) ou I(nfo), dia é
           U(til), S(abado) ou D(omingo/feriado) e sentido é I(da) ou V(olta)
           
           Por ora, apenas o mapa está implementado """
        
        self._assert_data_dir()
        for sentido in [0,1]:
            for dia in [0,1,2]:
                for tipo in "MI":
                    if tipo == "M":
                        url = self.base_href + "ABInfSvItiGoogleM.asp?DfSenID=%s&CdPjOID=%s&TpDiaID=%s&Tipo=Mapa" % (sentido, id, dia)
                    else:
                        url = self.base_href + "detalheLinha.asp?TpDiaID=%s&CdPjOID=%s&TpDiaIDpar=%s&DfSenID=%s" % (dia, id, dia, sentido + 1)
                    nomearq = "%s-%s-%s-%s.html" % (id, tipo, "USD"[dia], "IV"[sentido])
                    html = urllib2.urlopen(url).read()
                    arq = open(os.path.join(self.data_dir, nomearq), "w")
                    arq.writelines(html)
                    time.sleep(1)
        
        # 
                
    def get_pontos(self, id):
        """Recupera os pontos do HTML-mapa relacinados a uma linha. O retorno é um dict cujas chaves são os
           dias da semana ("util", "sabado" ou "domingo"), e os valores também são dicts, desta vez cujas
           chaves são "ida" ou "volta", e no último nível temos a lista de pontos. Ex.:
           
               >>>pontos = get_pontos(1234)
               >>>pontos["util"]["ida"]   # dia útil, sentido: ida
               [[10.1, -20.2], [30.3, -40.4], ...]
               
        """
        pontos = dict()
        for dia in "USD":
            pontos[self.DICT_DIAS[dia]] = dict()
            for sentido in "IV":
                nomearq = "%s-M-%s-%s.html" % (id, dia, sentido)
                html = open(os.path.join(self.data_dir, nomearq)).read()
                lista_js = re.search(r'var coor = "(.*?)"', html).group(1)
                if not lista_js:
                    pontosDS = []
                else:
                    lista = [float(x) / 1000000 for x in lista_js.split(r"||")]
                    pontosDS = [[a,b] for (a,b) in zip(lista[::2], lista[1::2])]
                pontos[self.DICT_DIAS[dia]][self.DICT_SENTIDOS[sentido]] = pontosDS
        return pontos

    def get_info_linha(self, id):
        """Recupera informações de uma linha (nome, número, horários, tempos, ruas,
           etc.) a partir do HTML dela. Retorna uma hierarquia de dicts, vide teste 
           unitário para ver as infos que retornam neles"""
        # Info básica (tanto faz qual HTML usar, ela repete em todos)
        arq_info = "%s-I-U-I.html" % id
        html = open(os.path.join(self.data_dir, arq_info)).read()
        soup = BeautifulSoup(html)
        info = {}
        nomes = soup.find("dl", id="dadosLinha").dd.ul.findAll("li")
        nomes[1].strong.extract()
        nomes[2].strong.extract()
        info["nome"] = {}
        info["nome"]["ida"] = nomes[1].string.strip()
        info["nome"]["volta"] = nomes[2].string.strip()
        info["numero"] = soup.find("input", id="noLinha")["value"]
        info["area"] = soup.find("input", id="areCod")["value"]
        info["consorcio"] = soup.find("input", id="consorcio")["value"]
        info["empresa"] = soup.find("input", id="empresa")["value"]
        info["horario"] = {"ida": {}, "volta": {}}
        horarios = soup.find("table", id="tabelaHorarios").findAll("tr")
        for sentido in [0,1]:
            for dia in [0,1,2]:
                info["horario"][self.SENTIDOS[sentido]][self.DIAS[dia]] = \
                    horarios[dia+1].findAll("td")[sentido+1].string
        info["tempo"] = {"ida": {"util": {}, "sabado": {}, "domingo": {}},
                         "volta": {"util": {}, "sabado": {}, "domingo": {}}}
        tempos = soup.find("table", id="tabelaTempo").findAll("tr")
        for sentido in [0,1]:
            for dia in [0,1,2]:
                for periodo in [0,1,2]:
                    info["tempo"][self.SENTIDOS[sentido]][self.DIAS[dia]][self.PERIODOS[periodo]] = \
                        tempos[dia+2].findAll("td")[1+periodo+3*sentido].string.strip()

        
        return info
    
    def _init_banco(self):
        self._conn = sqlite3.connect(self.db_name)
        self._cursor = self._conn.cursor()
        self._cursor.execute("create table if not exists linhas(id integer primary key, deleted boolean, last_update integer, last_upload integer, info text, pontos text)")
    
    def _close_banco(self):
        self._cursor.close() 
        self._conn.close()
    
    def lista_banco(self):
        self._init_banco()
        self._cursor.execute("select id from linhas order by id");
        lista_ids = self._cursor.fetchall()
        self._close_banco()
        return [i[0] for i in lista_ids]
    
    def atualiza_banco(self, id, info, pontos):
        """Insert ou update do registro do banco correspondente àquele ID"""
        dados = self.get_banco(id)
        self._init_banco()
        if not dados:
            ti = (id, 1, json.dumps(info), json.dumps(pontos),)
            self._cursor.execute("insert into linhas (id,deleted,last_update,info,pontos) values (?,'false',?,?,?)", ti)
        elif (dados["info"] != info) or (dados["pontos"] != pontos):
            tu = (dados["last_update"] + 1, json.dumps(info), json.dumps(pontos),id,)
            self._cursor.execute("update linhas set deleted='false',last_update=?,info=?,pontos=? where id=?", tu)
        self._conn.commit()
        self._close_banco()
    
    def deleta_banco(self, id):
        """Marca um registro no banco como deletado (não apaga fisicamente)"""
        dados = self.get_banco(id)
        if dados["deleted"] == "true":
            return        
        self._init_banco()
        t = (dados["last_update"] + 1, id,)
        self._cursor.execute("update linhas set deleted='true',last_update=? where id=?", t)
        self._conn.commit()
        self._close_banco()       
    
    def get_banco(self, id):
        self._init_banco()
        t = (id,)
        self._cursor.execute("select * from linhas where id = ?", t);
        r = self._cursor.fetchone()
        self._close_banco()
        if not r:
            return None
        result = dict(zip([x[0] for x in self._cursor.description], r))
        result["info"] = json.loads(result["info"])
        result["pontos"] = json.loads(result["pontos"])
        return result
         
            
#        
#                
#def geraCSV(linhas, stream):
#    writer = csv.writer(stream)    
#    for linha in linhas:
#        _log("Sleeping...")
#        time.sleep(20 + random.uniform(1, 10))
#        _log("Iniciando linha: %s" % linha["nome"])
#        writer.writerow([linha["nome"].encode("utf-8"),
#                         linha["url"],
#                         [p for p in linha["pontos"]]])
#
#
#def _getPontos(url):
#    """Retorna o generator de uma coleção de pontos (latitude e longitude) para uma
#    linha de ônibus, identificada pela URL"""
#    _log("Processando linha: " + url)
#    urlDs = re.sub(r"&TpDiaID=.", "&TpDiaID=0", url, 1) # Garante rota de dia da semana
#    if url != urlDs:
#        url = urlDs
#        _log("Link convertido para segunda-feira:" + url)
#    html = urllib2.urlopen(url).read()
#    # Os pontos estão na string JavaScript coor, que consiste em uma lista de  
#    # latitudes e longitudes, separados por || e convertidos para inteiros
#    # (i.e., multiplicados por 1 milhão). 
#    lista_js = re.search(r'var coor = "(.*?)"', html).group(1)
#    if not lista_js:
#        _log("Aviso: linha sem pontos. URL: " + url)
#        return
#    lista = [float(x) / 1000000 for x in lista_js.split(r"||")]
#    i = iter(lista)
#    for lat in i:
#        yield (lat, i.next())
##    return [(lat, i.next()) for lat in i]
#
#def _log(string):
#    print(string)
#    logging.debug(string)
#
#            
#
#if __name__ == "__main__":
#    print "Gerando linhas.csv..."
#    linhas = getLinhas()
#    nargs = len(sys.argv)    
#    if nargs > 2 or (nargs==2 and not isdigit(sys.argv[1])):
#        print "Uso: scraper.py [no. de linhas a pular no inicio]"
#        sys.exit()
#    if nargs == 2:
#        for i in range(0, int(sys.argv[1])):
#            _log("Pulando: %s" % linhas.next()["nome"])
#    arquivoCsv = open("linhas.csv", "ab")
#    geraCSV(linhas, arquivoCsv)
#    arquivoCsv.close()
