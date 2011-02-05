# -*- coding: utf-8 -*-

import sptscraper
import os
import unittest
import shutil
import random
import math
import time

DIR = "../tmp/"
ID_LINHA_1 = 53106   
ID_LINHA_2 = 58520 
    
class TestSptScraper(unittest.TestCase):
    
    scraper = None
    
    def setUp(self):
        self.scraper = sptscraper.SptScraper()
        self.scraper.data_dir = DIR
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
        self.assertFalse(os.path.exists(os.path.join(self.scraper.data_dir, self.scraper.index_file)))
#
#    def test_download_index(self):
#        num_linhas = self.scraper.download_index()
#        self.assertTrue(num_linhas > 0)
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, self.scraper.index_file)))
#
#    def test_download_index_invalido(self):
#        self.scraper.base_href = "http://www.google.com/"
#        self.scraper.pag_linhas = ""
#        num_linhas = self.scraper.download_index()
#        self.assertEqual(num_linhas, 0)
#        self.assertFalse(os.path.exists(os.path.join(self.scraper.data_dir, self.scraper.index_file)))
#        
#    def test_lista_linhas(self):
##        self.scraper.download_index()
#        shutil.copytree("../test_files", DIR)
#        lista_linhas = self.scraper.lista_linhas()
#        self.assertTrue(lista_linhas)
#        self.assertTrue(lista_linhas[0]["id"].isdigit())
#        self.assertTrue(lista_linhas[0]["id"]>0)
#        self.assertTrue(lista_linhas[0]["nome"])
         
#    def testa_download_linha(self):
#        os.mkdir(DIR)
#        shutil.copyfile("../test_files/index.html", os.path.join(DIR, "index.html"))
#        lista_linhas = self.scraper.lista_linhas()
#        id = lista_linhas[0]["id"]
#        self.scraper.download_linha(id)
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-M-U-I.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-M-S-I.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-M-D-I.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-M-U-V.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-M-S-V.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-M-D-V.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-I-U-I.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-I-S-I.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-I-D-I.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-I-U-V.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-I-S-V.html")))
#        self.assertTrue(os.path.exists(os.path.join(self.scraper.data_dir, id+"-I-D-V.html")))
        
    def test_get_pontos_linha(self):
        shutil.copytree("../test_files", DIR)
        id = ID_LINHA_1
        pontos = self.scraper.get_pontos(id)
        #todo nomes por extenso?
        self.assertEqual(pontos["util"]["ida"], pontos["sabado"]["ida"])
        self.assertEqual(pontos["util"]["volta"], pontos["domingo"]["volta"])
        self.assertNotEquals(pontos["util"]["ida"], pontos["domingo"]["volta"])
        self.assertTrue(math.fabs(float(pontos["util"]["ida"][0][0])) < 90)
        self.assertTrue(math.fabs(float(pontos["util"]["ida"][0][1])) < 90)
        self.assertTrue(math.fabs(float(pontos["sabado"]["volta"][1][0])) < 90)
        self.assertTrue(math.fabs(float(pontos["sabado"]["volta"][1][1])) < 90)
        self.assertTrue(math.fabs(float(pontos["domingo"]["ida"][2][0])) < 90)
        self.assertTrue(math.fabs(float(pontos["domingo"]["ida"][2][1])) < 90)
        
    def test_get_info_linha(self):
        shutil.copytree("../test_files", DIR)
        id = ID_LINHA_1
        info = self.scraper.get_info_linha(id)
        self.assertEqual(info["nome"]["ida"], "CENTER NORTE")
        self.assertEqual(info["nome"]["volta"], "CEMITERIO DO HORTO")
        self.assertEqual(info["numero"], "1016-10")
        self.assertEqual(info["area"], "2")
        self.assertEqual(info["consorcio"], u"CONSÓRCIO TRANSCOOPER FÊNIX")
        self.assertEqual(info["empresa"], u"TRANSCOOPER - COOPERATIVA DE TRANSPORTE DE PESSOAS E CARGAS DA REGIÃO SUDESTE")        
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
        shutil.copytree("../test_files", DIR)
        id1 = ID_LINHA_1
        info1 = self.scraper.get_info_linha(id1)
        pontos1 = self.scraper.get_pontos(id1)
        id2 = ID_LINHA_2
        info2 = self.scraper.get_info_linha(id2)
        pontos2 = self.scraper.get_pontos(id2)
        # insert / list
        ids_banco = self.scraper.lista_banco()
        self.assertEqual(0, len(ids_banco))
        self.scraper.atualiza_banco(id1, info1, pontos1)
        ids_banco = self.scraper.lista_banco()
        self.assertEqual(1, len(ids_banco))
        self.scraper.atualiza_banco(id2, info2, pontos2)
        ids_banco = self.scraper.lista_banco()
        self.assertEqual(2, len(ids_banco))
        # get
        dados = self.scraper.get_banco(ids_banco[0])
        self.assertEqual(info1, dados["info"])
        dados = self.scraper.get_banco(ids_banco[1])
        self.assertEqual(pontos2, dados["pontos"])
        self.assertNotEqual(pontos1, dados["pontos"])
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
        self.assertNotEqual(last_update, dados["last_update"])       
        last_update = dados["last_update"]
        ids_banco = self.scraper.lista_banco()
        self.assertEqual(2, len(ids_banco))
        self.scraper.deleta_banco(id2)
        dados = self.scraper.get_banco(ids_banco[1])
        self.assertEqual(last_update, dados["last_update"])       
        

if __name__ == '__main__':
    unittest.main()
        
        
        