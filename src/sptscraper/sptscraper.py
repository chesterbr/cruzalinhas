#!/usr/bin/python2.7 -O
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010-2011 Carlos Duarte do Nascimento (Chester)
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
""" Utilitário que baixa e interpreta os dados de itinerários de ônibus
    do site da SPTrans, opcionalmente atualizando o cruzalinhas

    Uso: python sptscraper.py COMANDO [id]   (use o comando help para info) """
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import base64
import sys
import os
import urllib
import urllib2
import urlparse
import re
import sqlite3
import time
import argparse
import textwrap
import random
import geohash
try:
    import json
except ImportError:
    import simplejson as json

class SptScraper:

    base_href = r"http://200.99.150.170/PlanOperWeb/"
    pag_linhas = "linhaselecionada.asp"

    index_file = "index.html"
    html_dir = "html"
    db_name = "linhas.sqlite"
    silent = False

    DIAS = ["util", "sabado", "domingo"]
    SENTIDOS = ["ida", "volta"]
    PERIODOS = ["manha", "entrepico", "tarde"]

    DICT_DIAS = dict(zip("USD", DIAS))
    DICT_SENTIDOS = dict(zip("IV", SENTIDOS))

    _conn = None
    _cursor = None

    def main(self):
        def write(string):
            """Imprime sem enter no final e desliga os logs (conveniência)"""
            self.silent = True
            sys.stdout.write(string)
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=textwrap.dedent('''\
Baixa e interpreta os dados de linhas de transporte público do site da SPTrans.

Os arquivos HTML são interpretados e o resultado é armazenado no arquivo
linhas.sqlite, que pode ser levado para outros aplicativos, transformado em
JSON ou ser usado para atualizar o cruzalinhas.

Comandos:
  info          Mostra a quantidade de atualizações pendentes para upload.
  download [id] Baixa os HTMLs da SPTrans (do início ou a partir do id).
  resume        Baixa os HTMLs a partir do último salvo
  parse         Lê os HTMLs e executa inclusões/alterações/exclusões no banco.
  list          Imprime uma lista JSON dos IDs das linhas no banco.
  dump [id]     Imprime o JSON das linhas no banco (ou apenas de uma).
  hashes        Imprime o JSON dos hashes no banco (com as linhas de cada um)
  upload        Sobe as atualizações pendentes do banco para o cruzalinhas.
            '''))
        parser.usage = "%(prog)s COMANDO [id]  (para ajuda: %(prog)s help)"
        parser.add_argument("comando", nargs = 1,
                            choices = ["help", "info","download", "resume", "parse", "list", "dump", "hashes", "upload"],
                            help = "Comandos (vide acima)")
        parser.add_argument("id",
                            metavar = "id",
                            type = int,
                            nargs = "?",
                            help = "id da linha (opcional para alguns comandos)")
        parser.add_argument("--url",
                            dest = "url",
                            nargs = "?",
                            help = "URL da instalação do cruzalinhas (para fazer upload), sem barra no final. Ex.: --url http://localhost:8080")
        parser.add_argument("--token",
                            dest = "token",
                            nargs = "?",
                            help = "Token de autenticação do admin (para fazer upload). Obtenha chamando o /token do cruzalinhas no browser")
        arguments = parser.parse_args()
        cmd = arguments.comando[0];
        if cmd == "help":
            parser.print_help()
        if cmd == 'info':
            print "Info para banco (%s) e HTMLs (%s):" % (self.db_name, self.html_dir)
            linhas = len(self.lista_linhas())
            conta = self.conta_pendencias_banco()
            print "  Linhas no index.html local: %s" % (linhas)
            print "  Atualizações de linhas pendentes no banco: %s" % conta["linhas"]
            print "  Atualizações de hashes pendentes no banco: %s" % conta["hashes"]
        if cmd == "resume":
            max_id = 0
            for arq in os.listdir(self.html_dir):
                match = re.search("(\d*)\-[IM]-[USD]-[IV]\.html", arq)
                if match and int(match.group(1)) > max_id:
                    max_id = int(match.group(1))
            if max_id == 0:
                print 'Não há download para continuar, tente "download"'
            else:
                cmd = "download"
                arguments.id = max_id
        if cmd == 'download':
            if not arguments.id:
                print "Preparando para apagar HTMLs baixados (Ctrl+C para cancelar)..."
                time.sleep(5)
                print "Apagando HTMLs antigos..."
                self.clean_html()
                print "Baixando página-índice..."
                numlinhas = self.download_index()
                print "Existem %s linhas no índice. Interpretando..." % numlinhas
                id_inicial = None
            else:
                print "Retomando download a partir do id %s..." % arguments.id
                id_inicial = str(arguments.id)
            linhas = self.lista_linhas()
            for id in sorted(linhas.keys()):
                if id_inicial and id != id_inicial:
                    continue
                id_inicial = None
                print "[%s] Baixando linha id=%s (%s)..." % (datetime.now(), id, linhas[id])
                self.download_linha(id)
            print "Download concluído"
        if cmd == "parse":
            self.html_to_banco(self.lista_linhas().keys())
            self.repopula_tabela_hashes()
            print "Parse concluído."
        if cmd == "list":
            print json.dumps(self.lista_ids_banco(inclui_deletadas=False), separators=(',',':'))
        if cmd == "dump":
            if arguments.id:
                linhas = [arguments.id]
            else:
                linhas = sorted(self.lista_ids_banco(inclui_deletadas=False))
            write("{")
            primeira = True
            for id in linhas:
                if not primeira:
                    write(",")
                primeira = False
                linha = self.get_banco(id)
                del(linha["id"])
                del(linha["last_update"])
                del(linha["last_upload"])
                del(linha["hashes"])
                del(linha["deleted"])
                write(str(id) + ":" + json.dumps(linha, separators=(',',':')))
            write("}")
        if cmd == "hashes":
            write("{")
            primeira = True
            for hash in self.list_tabela_hashes():
                if not primeira:
                    write(",")
                primeira = False
                write('"' + str(hash) + '":' + json.dumps(self.get_linhas_tabela_hashes(hash), separators=(',',':')))
            write("}")
        if cmd == "upload":
            if not arguments.url:
                print "Por favor, informe a URL da instalação do cruzalinhas (--url) sem barra no final"
            elif not arguments.token:
                print "Por favor, informe o token de autenticação do admin (--token). Para obter, chame /token na instalação do cruzalinhas"
            else:
                self.upload_linhas_banco(lambda dados: self._upload(arguments.url+"/uploadlinha",arguments.token,dados))
                self.upload_hashes_banco(lambda dados: self._upload(arguments.url+"/uploadhash",arguments.token,dados))


    def _upload(self, url, token, dados):
        dados_json = {}
        for param in dados.keys():
            if param == "hash":
                dados_json[param] = dados[param] # evita "6xyabc" no lugar de 6xyabc
            else:
                dados_json[param] = json.dumps(dados[param], separators=(',',':'))
        request = urllib2.Request(url, None, {"Cookie":base64.b64decode(token)})
        result = urllib2.urlopen(request,urllib.urlencode(dados_json)).read()
        is_ok = result.startswith("OK")
        if not is_ok:
            print result
        return is_ok

    def _assert_html_dir(self):
        if not os.path.exists(self.html_dir):
            os.mkdir(self.html_dir)

    def clean_html(self):
        """Apaga os downloads já realizados"""
        self._assert_html_dir()
        for file in os.listdir(self.html_dir):
            if file.endswith(".html"):
                os.unlink(os.path.join(self.html_dir,file))

    def download_index(self):
        """Baixa a página-índice (que contém a lista das linhas), verifica sua integridade
        e retorna a quantidade de linhas encontradas."""
        html = urllib2.urlopen(self.base_href + self.pag_linhas).read()
        soup = BeautifulSoup(html)
        numLinhas = 0
        for elem in soup.findAll("a", attrs={"class":re.compile("linkLinha|linkDetalhes")}):
            if elem["class"] == "linkLinha" and elem.string:
                numLinhas += 1
        if numLinhas > 0:
            self._assert_html_dir()
            arq = open(os.path.join(self.html_dir, self.index_file), "w")
            arq.writelines(html)
        return numLinhas

    def lista_linhas(self):
        """Retorna um dicionário cujas chaves são os IDs das linhas e os valores
           são os nomes, a partir da última página-índice baixada) """
        html_file = os.path.join(self.html_dir, self.index_file)
        if not os.path.exists(html_file):
            return {}
        html = open(html_file).read()
        soup = BeautifulSoup(html)
        linhas = {}
        for elem in soup.findAll("a", attrs={"class":re.compile("linkLinha|linkDetalhes")}):
            if elem["class"] == "linkLinha" and elem.string:
                nome = elem.string.replace("Linha: ", "").replace("&nbsp"," ").strip()
            elif elem["class"] == "linkDetalhes":
                parsed_url = urlparse.urlparse(self.base_href + elem["href"])
                # TODO Este trecho ignora links do OlhoVivo, que são no formato
                #      /PlanOperWeb/http://olhovivo.sptrans.com.br/linha/1016-10
                #      Talvez dê pra adicionar direto na interface os links
                if "detalheLinha.asp" in parsed_url[2]:
                    params = dict([part.split('=') for part in parsed_url[4].split('&')])
                    id = params["CdPjOID"]
                    linhas[id] = nome
        return linhas

    def download_linha(self, id):
        """Baixa os arquivos relacionados a uma linha identificado por "id". Os arquivos são
           salvos no formato id-tipo-dia-sentido.html, onde tipo é M(apa) ou I(nfo), dia é
           U(til), S(abado) ou D(omingo/feriado) e sentido é I(da) ou V(olta)"""

        self._assert_html_dir()
        for sentido in [0,1]:
            for dia in [0,1,2]:
                for tipo in "MI":
                    if tipo == "M":
                        url = self.base_href + "ABInfSvItiGoogleM.asp?DfSenID=%s&CdPjOID=%s&TpDiaID=%s&Tipo=Mapa" % (sentido, id, dia)
                    else:
                        url = self.base_href + "detalheLinha.asp?TpDiaID=%s&CdPjOID=%s&TpDiaIDpar=%s&DfSenID=%s" % (dia, id, dia, sentido + 1)
                    nomearq = "%s-%s-%s-%s.html" % (id, tipo, "USD"[dia], "IV"[sentido])
                    try:
                        html = urllib2.urlopen(url).read()
                    # FIXME
                    # urllib2.HTTPError: HTTP Error 500: Internal Server Error
                    # urllib2.HTTPError: HTTP Error 503: Service Unavailable
                    # urllib2.URLError: <urlopen error (54, 'Connection reset by peer')>
                    # urllib2.URLError: <urlopen error (60, 'Operation timed out')>
                    except:
                        print "Erro ao baixar: " + url
                        raise
                    arq = open(os.path.join(self.html_dir, nomearq), "w")
                    arq.writelines(html)
                    time.sleep(random.uniform(0,1.5))


    def get_pontos_linha(self, id):
        """Recupera os pontos do HTML-mapa relacinados a uma linha. O retorno é um dict cujas chaves são os
           dias da semana ("util", "sabado" ou "domingo"), e os valores também são dicts, desta vez cujas
           chaves são "ida" ou "volta", e no último nível temos a lista de pontos. Ex.:

               >>>pontos = get_pontos_linha(1234)
               >>>pontos["util"]["ida"]   # dia útil, sentido: ida
               [[10.1, -20.2], [30.3, -40.4], ...]

        """
        pontos = dict()
        for dia in "USD":
            pontos[self.DICT_DIAS[dia]] = dict()
            for sentido in "IV":
                nomearq = "%s-M-%s-%s.html" % (id, dia, sentido)
                html = open(os.path.join(self.html_dir, nomearq)).read()
                lista_js = re.search(r'var coor = "(.*?)"', html).group(1)
                if not lista_js:
                    pontosDS = []
                else:
                    lista = [int(x) for x in lista_js.split(r"||")]
                    pontosDS = [[a,b] for (a,b) in zip(lista[::2], lista[1::2])]
                pontos[self.DICT_DIAS[dia]][self.DICT_SENTIDOS[sentido]] = pontosDS
        return pontos

    def get_info_linha(self, id):
        """Recupera informações de uma linha (nome, número, horários, tempos, ruas,
           etc.) a partir do HTML dela. Retorna uma hierarquia de dicts, vide teste
           unitário para ver as infos que retornam neles"""
        # Info básica (tanto faz qual HTML usar, ela repete em todos)
        arq_info = "%s-I-U-I.html" % id
        html = open(os.path.join(self.html_dir, arq_info)).read()
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
        try:
            for sentido in [0,1]:
                for dia in [0,1,2]:
                    for periodo in [0,1,2]:
                        info["tempo"][self.SENTIDOS[sentido]][self.DIAS[dia]][self.PERIODOS[periodo]] = \
                            tempos[dia+2].findAll("td")[1+periodo+3*sentido].string.strip()
        except AttributeError:
            del(info["tempo"])
            self._log(u"Aviso: linha id=%s (%s) não tem tempos de viagem" % (id, info["numero"]))


        return info

    def get_hashes(self, trajeto):
        """Dada a lista de pontos (i.e., de pares de coordenadas) que compõe o desenho de
           um trajeto, calcula os geohashes das "caixas" que contém esse trajeto com exatos
           6 caracteres (o que, segundo http://en.wikipedia.org/wiki/Geohash, faz com uqe
           o "erro" seja de ~0.6km, bem razoável para uma busca por proximidade a pé).
           O retorno é um conjunto sem repetições destes geohashes"""
        hashes = set()
        pontoAnt = None
        for ponto in trajeto:
            if pontoAnt:
                hash = str(geohash.Geohash((pontoAnt[1] / 1000000.0, pontoAnt[0] / 1000000.0)) +
                           geohash.Geohash((ponto[1] / 1000000.0, ponto[0] / 1000000.0)))[0:6]
                if len(hash) == 6:
                    hashes.add(hash)
            pontoAnt = ponto

        return hashes

    def _init_banco(self):
        self._conn = sqlite3.connect(self.db_name)
        self._cursor = self._conn.cursor()
        self._cursor.execute("create table if not exists linhas(id integer primary key, deleted boolean, last_update integer, last_upload integer, info text, pontos text, hashes text)")
        self._cursor.execute("create table if not exists hashes(hash char(6) primary key, last_update integer, last_upload integer, linhas text)")

    def _close_banco(self):
        self._cursor.close()
        self._conn.close()

    def lista_ids_banco(self, inclui_deletadas=True):
        """Recupera os IDs cadastrados no banco, como uma lista de integers. Por default
           inclui linhas deletadas, mas pode ser chamado com inclui_deletadas=False"""
        self._init_banco()
        if inclui_deletadas:
            self._cursor.execute("select id from linhas order by id");
        else:
            self._cursor.execute("select id from linhas where deleted='false' order by id");
        lista_ids = self._cursor.fetchall()
        self._close_banco()
        return [i[0] for i in lista_ids]

    def atualiza_banco(self, id, info, pontos):
        """Insert ou update do registro do banco correspondente àquele ID"""
        dados = self.get_banco(id)
        self._init_banco()
        if not dados:
            hashes = self.get_hashes_pontos(pontos)
            ti = (id, json.dumps(info), json.dumps(pontos), json.dumps(hashes), )
            self._cursor.execute("insert into linhas (id,deleted,last_update,last_upload,info,pontos,hashes) values (?,'false',1,0,?,?,?)", ti)
        elif (dados["info"] != info) or (dados["pontos"] != pontos):
            hashes = self.get_hashes_pontos(pontos)
            tu = (dados["last_update"] + 1, json.dumps(info), json.dumps(pontos), json.dumps(hashes), id,)
            self._cursor.execute("update linhas set deleted='false',last_update=?,info=?,pontos=?,hashes=? where id=?", tu)
        self._conn.commit()
        self._close_banco()

    def get_hashes_pontos(self, pontos):
        """Idem a get_hashes, mas atua em todos os trajetos possíveis para uma linha, isto
           é, num array no formato pontos[dia][sentido] = [[x1,y1], [x2,y2]...].
           O retorno é a lista dos hashes que abrigam todos os trajetos, independente de
           sentido ou linha. É uma lista e não um conjunto para permitir serialização JSON. """
        hashes = set()
        for dia in self.DIAS:
            for sentido in self.SENTIDOS:
                hashes.update(self.get_hashes(pontos[dia][sentido]))
        return list(hashes)


    def deleta_banco(self, id):
        """Marca um registro no banco como deletado (não apaga fisicamente)"""
        dados = self.get_banco(id)
        if dados["deleted"] == "true":
            return
        self._init_banco()
        t = (dados["last_update"] + 1, id,)
        self._cursor.execute("update linhas set deleted='true',last_update=?,info='{}',pontos='{}'  where id=?", t)
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
        result["hashes"] = json.loads(result["hashes"])
        return result

    def list_tabela_hashes(self, inclui_atualizadas=True):
        if inclui_atualizadas:
            q = "select hash from hashes order by hash"
        else:
            q = "select hash from hashes where last_update != last_upload order by hash"
        self._init_banco()
        lista_hashes = self._cursor.execute(q).fetchall()
        self._close_banco()
        return [i[0] for i in lista_hashes]

    def get_linhas_tabela_hashes(self, hash):
        self._init_banco()
        self._cursor.execute("select linhas from hashes where hash = ?", (hash,));
        r = self._cursor.fetchone()
        self._close_banco()
        if not r:
            return []
        else:
            return json.loads(r[0])

    def repopula_tabela_hashes(self):
        """Repopula a tabela de hashes com as linhas ativas no banco"""
        ids = self.lista_ids_banco(inclui_deletadas=False)
        self._init_banco()
        self._cursor.execute("select max(last_update) from hashes")
        last_update = self._cursor.fetchone()[0]
        if last_update:
            last_update += 1
        else:
            last_update = 1
        self._cursor.execute("update hashes set last_update=?,linhas='[]'", (last_update, ))
        self._conn.commit()
        for linha in self._cursor.execute("select id, hashes from linhas where deleted='false'").fetchall():
            id_linha = linha[0]
            self._log("Atualizando tabela de hashes para linha id=%s" % id_linha)
            for hash in json.loads(linha[1]):
                self._cursor.execute("select linhas from hashes where hash=?", (hash, ))
                r = self._cursor.fetchone()
                if not r:
                    self._cursor.execute("insert into hashes (hash,linhas,last_update,last_upload) values (?,?,?,0)",
                                         (hash, "[%s]" % id_linha, last_update, ))
                else:
                    linhas = json.loads(r[0])
                    linhas.append(id_linha)
                    self._cursor.execute("update hashes set linhas=?,last_update=? where hash=?",
                                         (json.dumps(linhas, separators=(',',':')), last_update, hash, ))
            self._conn.commit()
        self._close_banco()


    def html_to_banco(self, lista_ids):
        """Atualiza o banco, inserindo/alterando os HTMLs que constem na
           lista e excluindo dele os que não estiverem nela"""
        lista_ordenada = sorted(lista_ids)
        for id in lista_ordenada:
            self._log("Parseando HTMLs da linha id=%s" % id)
            info = self.get_info_linha(id)
            pontos = self.get_pontos_linha(id)
            self.atualiza_banco(id, info, pontos)
        for id in self.lista_ids_banco():
            if int(id) not in lista_ordenada and str(id) not in lista_ordenada:
                self._log("Marcando para remoção linha id=%s" % id)
                self.deleta_banco(id)

    def upload_linhas_banco(self, fn_upload):
        for id in self.lista_ids_banco():
            dados = self.get_banco(id)
            if dados["last_update"] != dados["last_upload"]:
                if dados["deleted"] == "true":
                    msg = "Linha id=%s (DELETED)" % id
                else:
                    msg = "Linha id=%s, codigo=%s" % (id, dados["info"]["numero"])
                self._log("Iniciando upload de linha - %s" % msg)
                if fn_upload(dados):
                    t = (id,)
                    self._init_banco()
                    self._cursor.execute("update linhas set last_upload=last_update where id=?", t)
                    self._conn.commit()
                    self._close_banco()
                    self._log("Upload OK - %s" % msg)
                else:
                    self._log("Erro no upload - %s" % msg)

    def upload_hashes_banco(self, fn_upload):
        for hash in self.list_tabela_hashes(inclui_atualizadas=False):
            self._log("Iniciando upload - hash %s " % hash)
            dados = {"hash":hash, "linhas": self.get_linhas_tabela_hashes(hash)}
            if fn_upload(dados):
                self._init_banco()
                self._cursor.execute("update hashes set last_upload=last_update where hash=?", (hash, ))
                self._conn.commit()
                self._close_banco()
                self._log("Upload OK - hash %s" % hash)
            else:
                self._log("Erro no upload - hash %s" % hash)

    def conta_pendencias_banco(self):
        """Diz quantas linhas/hashes temos que subir (porque mudaram)"""
        self._init_banco()
        self._cursor.execute("select count(*) from linhas where last_update != last_upload");
        r1 = self._cursor.fetchone()
        self._cursor.execute("select count(*) from hashes where last_update != last_upload");
        r2 = self._cursor.fetchone()
        self._close_banco()
        return {"linhas": r1[0], "hashes": r2[0]}


    def _log(self, string):
        if not self.silent:
            print(string)
            #logging.debug(string)


if __name__ == '__main__':
    SptScraper().main()
