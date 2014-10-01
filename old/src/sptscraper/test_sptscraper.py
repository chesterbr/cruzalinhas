#!/usr/bin/python2.5 -O
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

import sptscraper
import os
import unittest
import shutil
import random
import math
import time
from mock import Mock

DIR = "../../tmp/"
DB = "../../tmp/linhas.sqlite"
TEST_FILES_DIR = "../../test_files"
ID_LINHA_1 = 81085
ID_LINHA_2 = 81086

class TestSptScraper(unittest.TestCase):

    scraper = None

    def setUp(self):
        self.scraper = sptscraper.SptScraper()
        self.scraper.html_dir = DIR
        self.scraper.db_name = DB
        self.scraper.silent = True
        if os.path.exists(self.scraper.db_name):
            os.remove(self.scraper.db_name)


    def tearDown(self):
        if os.path.exists(DIR):
            shutil.rmtree(DIR)
        if os.path.exists(self.scraper.db_name):
            os.remove(self.scraper.db_name)

    def test_clean_html(self):
        if not os.path.exists(DIR):
            os.mkdir(DIR)
        html = os.path.join(DIR, "teste" + str(random.randint(1, 1000)) +".html")
        txt = os.path.join(DIR, "teste" + str(random.randint(1, 1000)) +".txt")
        open(html, 'w').close()
        open(txt, 'w').close()
        self.assertTrue(os.path.exists(html))
        self.assertTrue(os.path.exists(txt))
        self.scraper.clean_html()
        self.assertFalse(os.path.exists(html))
        self.assertTrue(os.path.exists(txt))
        self.assertFalse(os.path.exists(os.path.join(self.scraper.html_dir, self.scraper.index_file)))

    def test_download_index(self):
        num_linhas = self.scraper.download_index()
        self.assertTrue(num_linhas > 0)
        self.assertEquals(num_linhas, len(self.scraper.lista_linhas()))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, self.scraper.index_file)))

    def test_download_index_invalido(self):
        self.scraper.base_href = "http://www.google.com/"
        self.scraper.pag_linhas = ""
        num_linhas = self.scraper.download_index()
        self.assertEqual(num_linhas, 0)
        self.assertFalse(os.path.exists(os.path.join(self.scraper.html_dir, self.scraper.index_file)))

    def test_lista_linhas(self):
#        self.scraper.download_index()
#        TODO quebrar esse teste em dois: um que lida com arquivos locais, outro com
#        downloads
        lista_linhas = self.scraper.lista_linhas()
        self.assertEquals({}, lista_linhas)
        shutil.copytree(TEST_FILES_DIR, DIR)
        lista_linhas = self.scraper.lista_linhas()
        self.assertTrue(lista_linhas)
        self.assertTrue(lista_linhas.keys()[0].isdigit())
        self.assertTrue(lista_linhas.keys()[0]>0)
        self.assertTrue(lista_linhas.values()[0])

    def test_download_linha(self):
        os.mkdir(DIR)
        id = str(ID_LINHA_1)
        self.scraper.download_linha(id)
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-M-U-I.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-M-S-I.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-M-D-I.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-M-U-V.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-M-S-V.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-M-D-V.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-I-U-I.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-I-S-I.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-I-D-I.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-I-U-V.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-I-S-V.html")))
        self.assertTrue(os.path.exists(os.path.join(self.scraper.html_dir, id+"-I-D-V.html")))

    def test_get_pontos_linha(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id = ID_LINHA_1
        pontos = self.scraper.get_pontos_linha(id)
        #todo nomes por extenso?
        self.assertEqual(pontos["util"]["ida"], pontos["sabado"]["ida"])
        self.assertEqual(pontos["util"]["volta"], pontos["domingo"]["volta"])
        self.assertNotEquals(pontos["util"]["ida"], pontos["domingo"]["volta"])
        for dia in self.scraper.DIAS:
            for sentido in self.scraper.SENTIDOS:
                for ponto in pontos[dia][sentido]:
                    self.assertTrue(ponto[0])
                    self.assertTrue(ponto[1])
                    self.assertTrue(ponto[0] > -24000000, ponto)
                    self.assertTrue(ponto[0] < -22000000, ponto)
                    self.assertTrue(ponto[1] > -47000000, ponto)
                    self.assertTrue(ponto[1] < -45000000, ponto)

    def test_get_hashes(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id = ID_LINHA_1
        pontos = self.scraper.get_pontos_linha(id)
        hashes = self.scraper.get_hashes(pontos["util"]["ida"])
        self.assertTrue(len(hashes)>0)
        [self.assertTrue(hash.startswith("6g"), hash) for hash in hashes]
        [self.assertTrue(len(hash)==6, hash) for hash in hashes]

    def test_get_info_linha(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id = ID_LINHA_1
        info = self.scraper.get_info_linha(id)
        self.assertEqual(info["nome"]["ida"], "CENTER NORTE")
        self.assertEqual(info["nome"]["volta"], "CEMITERIO DO HORTO")
        self.assertEqual(info["numero"], "1016-10")
        self.assertEqual(info["area"], "2")
        self.assertEqual(info["consorcio"], u"CONSÓRCIO TRANSCOOPER FÊNIX")
        self.assertEqual(info["empresa"], u"TRANSCOOPER - COOP. TRANS. PESSOAS E CARGAS DA REG.SUDESTE")
        self.assertEqual(info["horario"]["ida"]["sabado"], "05:00-00:20")
        self.assertEqual(info["horario"]["volta"]["domingo"], "06:30-00:50")
        self.assertEqual(info["tempo"]["ida"]["util"]["manha"], "35")
        self.assertEqual(info["tempo"]["volta"]["sabado"]["entrepico"], "30")
        self.assertEqual(info["tempo"]["volta"]["domingo"]["tarde"], "25")
        #TODO esses aí embaixo
        #self.assertEqual(info["ruas"]["ida"]["domingo"][1]["logradouro"], "AV. SEN. JOSE ERMIRIO DE MORAES")
        #self.assertEqual(info["ruas"]["ida"]["domingo"][2]["faixa"], "1-249")
        #self.assertTrue(info["ruas"]["ida"]["domingo"][2]["evento"]) # feira livre
        #self.assertFalse(info["ruas"]["ida"]["domingo"][3]["evento"])
        # TODO partidas (olhar no site e ver como deve ser
        # mas é algo na linha partidas[sentido][dia][n] contendo faixa, # de partidas e horários dos veículos adaptados
        # TODO pensar se vamos ter flag para veículos adaptados

    def test_crud_banco(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id1 = ID_LINHA_1
        info1 = self.scraper.get_info_linha(id1)
        pontos1 = self.scraper.get_pontos_linha(id1)
        id2 = ID_LINHA_2
        info2 = self.scraper.get_info_linha(id2)
        pontos2 = self.scraper.get_pontos_linha(id2)
        # insert / list
        ids_banco = self.scraper.lista_ids_banco()
        self.assertEqual(0, len(ids_banco))
        self.scraper.atualiza_banco(id1, info1, pontos1)
        ids_banco = self.scraper.lista_ids_banco()
        self.assertEqual(1, len(ids_banco))
        self.scraper.atualiza_banco(id2, info2, pontos2)
        ids_banco = self.scraper.lista_ids_banco()
        self.assertEqual(2, len(ids_banco))
        # get
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertEqual(info1, dados["info"])
        dados = self.scraper.get_banco(ids_banco[1])
        self.assertEqual(pontos2, dados["pontos"])
        self.assertNotEqual(pontos1, dados["pontos"])
        hashes = dados["hashes"]
        self.assertTrue(len(hashes)>0)
        [self.assertTrue(hash.startswith("6g"), hash) for hash in hashes]
        [self.assertTrue(len(hash)==6, hash) for hash in hashes]
        # update (só atualiza o last_update se mudarem os dados)
        dados = self.scraper.get_banco(ids_banco[0])
        last_update = dados["last_update"]
        self.scraper.atualiza_banco(id1, info1, pontos1) # nao mudou
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertEqual(last_update, dados["last_update"])
        self.scraper.atualiza_banco(id1, info1, pontos2) # mudou
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertNotEqual(last_update, dados["last_update"])
        last_update = dados["last_update"]
        self.scraper.atualiza_banco(id1, info2, pontos2) # mudou
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertNotEqual(last_update, dados["last_update"])
        last_update = dados["last_update"]
        self.scraper.atualiza_banco(id1, info1, pontos1) # mudou
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertNotEqual(last_update, dados["last_update"])
        last_update = dados["last_update"]
        self.scraper.atualiza_banco(id1, info1, pontos1) # nao mudou
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertEqual(last_update, dados["last_update"])
        # delete (só atualiza o last_update se mudarem os dados)
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertNotEqual("true", dados["deleted"])
        dados = self.scraper.get_banco(ids_banco[1])
        self.assertNotEqual("true", dados["deleted"])
        last_update = dados["last_update"]
        self.scraper.deleta_banco(id2)
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertNotEqual("true", dados["deleted"])
        dados = self.scraper.get_banco(ids_banco[1])
        self.assertEqual("true", dados["deleted"])
        self.assertEqual(dict(), dados["info"])
        self.assertEqual(dict(), dados["pontos"])
        self.assertNotEqual(last_update, dados["last_update"])
        last_update = dados["last_update"]
        ids_banco = self.scraper.lista_ids_banco()
        self.assertEqual(2, len(ids_banco))
        self.scraper.deleta_banco(id2)
        dados = self.scraper.get_banco(ids_banco[1])
        self.assertEqual(last_update, dados["last_update"])
        ids_banco = self.scraper.lista_ids_banco()
        self.assertEqual(2, len(ids_banco))
        ids_banco = self.scraper.lista_ids_banco(inclui_deletadas=False)
        self.assertEqual(1, len(ids_banco))

    def test_html_to_banco(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id1 = ID_LINHA_1
        info1 = self.scraper.get_info_linha(id1)
        pontos1 = self.scraper.get_pontos_linha(id1)
        id2 = ID_LINHA_2
        info2 = self.scraper.get_info_linha(id2)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.html_to_banco([id1,id2])
        self.assertEqual(2, self.scraper.conta_pendencias_banco()["linhas"])
        mock_fn_upload = Mock()
        mock_fn_upload.return_value = True
        self.scraper.upload_linhas_banco(mock_fn_upload)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.html_to_banco([id1,id2])
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.html_to_banco([id1])
        self.assertEqual(1, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.upload_linhas_banco(mock_fn_upload)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])

    def test_tabela_hashes(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id1 = ID_LINHA_1
        id2 = ID_LINHA_2
        info1 = self.scraper.get_info_linha(id1)
        info2 = self.scraper.get_info_linha(id2)
        pontos1 = self.scraper.get_pontos_linha(id1)
        pontos2 = self.scraper.get_pontos_linha(id2)
        # Adiciona um segmento comum nas linhas (para ficar com o geohash ele em ambas)
        pontos1["util"]["ida"].extend([[-23674434, -46632641], [-23674618, -46632817]])
        pontos2["domingo"]["volta"].extend([[-23674434, -46632641], [-23674618, -46632817]])
        self.scraper.atualiza_banco(id1, info1, pontos1)
        self.scraper.atualiza_banco(id2, info2, pontos2)
        linha1 = self.scraper.get_banco(id1)
        linha2 = self.scraper.get_banco(id2)
        for hash in linha1["hashes"]:
            linhas = self.scraper.get_linhas_tabela_hashes(hash)
            self.assertFalse(id1 in linhas, str(id1) + "," + str(linhas))
        for hash in linha2["hashes"]:
            linhas = self.scraper.get_linhas_tabela_hashes(hash)
            self.assertFalse(id2 in linhas, str(id2) + "," + str(linhas))
        self.scraper.repopula_tabela_hashes()
        for hash in linha1["hashes"]:
            linhas = self.scraper.get_linhas_tabela_hashes(hash)
            self.assertTrue(id1 in linhas, str(id1) + "," + str(linhas))
        for hash in linha2["hashes"]:
            linhas = self.scraper.get_linhas_tabela_hashes(hash)
            self.assertTrue(id2 in linhas, str(id2) + "," + str(linhas))
        self.scraper.deleta_banco(id1)
        self.scraper.repopula_tabela_hashes()
        for hash in linha1["hashes"]:
            linhas = self.scraper.get_linhas_tabela_hashes(hash)
            self.assertFalse(id1 in linhas, str(id1) + "," + str(linhas))
        for hash in linha2["hashes"]:
            linhas = self.scraper.get_linhas_tabela_hashes(hash)
            self.assertTrue(id2 in linhas, str(id2) + "," + str(linhas))

    def test_upload_linhas(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id1 = ID_LINHA_1
        info1 = self.scraper.get_info_linha(id1)
        pontos1 = self.scraper.get_pontos_linha(id1)
        id2 = ID_LINHA_2
        info2 = self.scraper.get_info_linha(id2)
        pontos2 = self.scraper.get_pontos_linha(id2)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.atualiza_banco(id1, info1, pontos1)
        self.assertEqual(1, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.atualiza_banco(id2, info1, pontos1)
        self.assertEqual(2, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.atualiza_banco(id2, info2, pontos2)
        self.assertEqual(2, self.scraper.conta_pendencias_banco()["linhas"])
        mock_fn_upload = Mock()
        mock_fn_upload.return_value = True
        self.scraper.upload_linhas_banco(mock_fn_upload)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.atualiza_banco(id1, info1, pontos1)
        self.scraper.upload_linhas_banco(mock_fn_upload)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.atualiza_banco(id1, info1, pontos2)
        self.scraper.deleta_banco(id2)
        self.assertEqual(2, self.scraper.conta_pendencias_banco()["linhas"])
        self.scraper.upload_linhas_banco(mock_fn_upload)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["linhas"])

    def test_upload_hashes(self):
        shutil.copytree(TEST_FILES_DIR, DIR)
        id1 = ID_LINHA_1
        id2 = ID_LINHA_2
        info1 = self.scraper.get_info_linha(id1)
        info2 = self.scraper.get_info_linha(id2)
        pontos1 = self.scraper.get_pontos_linha(id1)
        pontos2 = self.scraper.get_pontos_linha(id2)
        # Adiciona um segmento comum nas linhas (para ficar com o geohash ele em ambas)
        pontos1["util"]["ida"].extend([[-23674434, -46632641], [-23674618, -46632817]])
        pontos2["domingo"]["volta"].extend([[-23674434, -46632641], [-23674618, -46632817]])
        self.scraper.repopula_tabela_hashes()
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["hashes"])
        self.scraper.atualiza_banco(id1, info1, pontos1)
        self.scraper.repopula_tabela_hashes()
        self.assertEqual(18, self.scraper.conta_pendencias_banco()["hashes"])
        self.scraper.atualiza_banco(id2, info2, pontos2)
        self.scraper.repopula_tabela_hashes()
        self.assertEqual(40, self.scraper.conta_pendencias_banco()["hashes"])
        mock_fn_upload_fail = Mock(side_effect = lambda dados: dados["hash"] != "6gyf7m")
        self.scraper.upload_hashes_banco(mock_fn_upload_fail)
        self.assertEqual(1, self.scraper.conta_pendencias_banco()["hashes"])
        mock_fn_upload = Mock()
        mock_fn_upload.return_value = True
        self.scraper.upload_hashes_banco(mock_fn_upload)
        self.assertEqual(0, self.scraper.conta_pendencias_banco()["hashes"])
        self.scraper.deleta_banco(id2)
        self.scraper.repopula_tabela_hashes()
        self.assertEqual(40, self.scraper.conta_pendencias_banco()["hashes"])




if __name__ == '__main__':
    unittest.main()



