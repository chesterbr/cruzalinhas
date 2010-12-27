import sptscraper
import os
import unittest
import shutil
import random

DIR = "../tmp/"
    
class TestSptScraper(unittest.TestCase):
    
    scraper = None
    
    def setUp(self):
        self.scraper = sptscraper.SptScraper()
        self.scraper.data_dir = DIR
        
    def tearDown(self):
        if os.path.exists(DIR):
            shutil.rmtree(DIR)
        
#    def test_clean_html(self):
#        if not os.path.exists(DIR):
#            os.mkdir(DIR)        
#        html = os.path.join(DIR, "teste" + str(random.randint(1, 1000)) +".html")
#        txt = os.path.join(DIR, "teste" + str(random.randint(1, 1000)) +".txt")
#        open(html, 'w').close()
#        open(txt, 'w').close()
#        self.assertTrue(os.path.exists(html)) 
#        self.assertTrue(os.path.exists(txt)) 
#        self.scraper.clean_html()
#        self.assertFalse(os.path.exists(html)) 
#        self.assertTrue(os.path.exists(txt)) 
#        self.assertFalse(os.path.exists(os.path.join(self.scraper.data_dir, self.scraper.index_file)))
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
#        self.assertEquals(num_linhas, 0)
#        self.assertFalse(os.path.exists(os.path.join(self.scraper.data_dir, self.scraper.index_file)))
        
    def test_lista_linhas(self):
#        self.scraper.download_index()
        shutil.copytree("../test_files", DIR)
        lista_linhas = self.scraper.lista_linhas()
        self.assertTrue(lista_linhas)
        self.assertTrue(lista_linhas[0]["nome"])
        self.assertTrue(lista_linhas[0]["url"])
        
    def test_get_html_linha(self):
        shutil.copytree("../test_files", DIR)
        
        
        