#!/usr/bin/python
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
"""Carrega o CSV de pouquinho em pouquinho no appengine (evitando timeouts)"""
import sys
import subprocess
import os
import csv

linhas = open("linhas.csv", "r")
if len(sys.argv)!=4:
    print "Uso: slow_gae_uploader.py <num_pular> <host> <cookie-param>"
    print "  <num_pular> quantidade de linhas a pular do linhas.csv (0 para ler ele todo)"
    print "  <host> localhost:8080 ou cruzalinhas.appspot.com"
    print "  <cookie-param> chame http://<host>/load-linha acima que ele te dá o valor"
    print "                 (é preciso logar como admin)"
    print "Ex.: slow_gae_uploader.py 100 localhost:8080 --cookie='ACSID=blablebli'"
    sys.exit()
num_linhas_pular = int(sys.argv[1])
host = sys.argv[2]
cookie_param = sys.argv[3]
print "Começou"
n = 0
for linha in csv.reader(linhas):
    nome = linha[0]
    url = linha[1]
    n += 1
    if n <= num_linhas_pular:
        print "Pulando %s" % nome
        continue
    print "Processando %s" % nome
    temp = open("temp.csv", "w")
    temp.write("%s,%s" % (nome, url))
    temp.close()
    subprocess.check_call(['python2.5',
                           '/usr/local/bin/bulkload_client.py',
                           '--filename=temp.csv',
                           '--url=http://%s/load-linha' % host,
                           '--kind=Linha',
                           '--batch_size=1',
                           cookie_param])
    temp = open("temp.csv", "w")
    ordem = 1
    for ponto in eval(linha[2]):
        temp.write("%s,%s,%s,%s\n" % (nome, ordem, ponto[0], ponto[1]))
        ordem += 1
    temp.close()
    subprocess.check_call(['python2.5',
                           '/usr/local/bin/bulkload_client.py',
                           '--filename=temp.csv',
                           '--url=http://%s/load-ponto' % host,
                           '--kind=Ponto',
                           '--batch_size=50',
                           cookie_param])
     
linhas.close()
os.remove("temp.csv")
print "Concluído"
        
