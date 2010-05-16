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

#### CONFIG
# Apontar para development ou production
#SERVIDOR = "localhost:8080"
SERVIDOR = "cruzalinhas.appspot.com"

# Colocar um cookie de autenticação válido
#COOKIE = 'dev_appserver_login="test@example.com:True:185804764220139124118"'
#### FIM CONFIG

linhas = open("linhas.csv", "r")
print "Começou"
num_linhas_pular = int(sys.argv[1]) if len(sys.argv) > 1 else 0
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
                           '--url=http://%s/load-linha' % SERVIDOR,
                           '--kind=Linha',
                           '--batch_size=1',
                           '--cookie', COOKIE])
    temp = open("temp.csv", "w")
    ordem = 1
    for ponto in eval(linha[2]):
        temp.write("%s,%s,%s,%s\n" % (nome, ordem, ponto[0], ponto[1]))
        ordem += 1
    temp.close()
    subprocess.check_call(['python2.5',
                           '/usr/local/bin/bulkload_client.py',
                           '--filename=temp.csv',
                           '--url=http://%s/load-ponto' % SERVIDOR,
                           '--kind=Ponto',
                           '--batch_size=50',
                           '--cookie', COOKIE])
     
linhas.close()
os.remove("temp.csv")
print "Concluído"
        
