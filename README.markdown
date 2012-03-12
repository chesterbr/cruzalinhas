cruzalinhas - README
====================

Introdução
----------

O cruzalinhas é um experimento que tenta complementar a experiência de
localização de rotas de transporte público em São Paulo, mostrando todas as
linhas que passam por um determinado local e/ou as linhas que passam entre
dois ou mais locais.

Ele pode ser acessado em http://cruzalinhas.com . O código-fonte é livre e pode ser baixado
em http://github.com/chesterbr/cruzalinhas (vide licença abaixo).


Preparando o ambiente e rodando o cruzalinhas na sua máquina
------------------------------------------------------------

1. Certifique-se de que sua máquina tem Python 2.5 ou superior instalado, com o comando:

        python --version

2. Baixe e instale o App Engine SDK Python para a sua plataforma (Windows, Mac ou Linux) de:

        http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python

3. Baixe o código do Github, com o comando abaixo (se fez um fork - o que é uma boa - troque "chesterbr" pelo seu id no github):

        git clone git@github.com:chesterbr/cruzalinhas.git

    O comando vai criar uma pasta "cruzalinhas". Dentro dela há uma pasta "src" com os dois projetos relevantes que vamos mencionar nos passos seguintes:

    - cruzalinhas/src/sptscraper: baixa, processa e envia ao site os dados
    - cruzalinhas/src/cruzalinhas: o site em si

4. Rode o site no servidor local. Para isso, abra o Google App Engine Launcher (que veio com o SDK), clique em File, Add Existing Application. Aponte a caixa de diretório para cruzalinhas/src/cruzalinhas e clique no botão "Run".

    Se estiver usando Linux ou preferir a linha de comando, entre em cruzalinhas/src/cruzalinhas e use o comando abaixo:

        dev_appserver.py .

    Em qualquer caso, você pode testar o servidor com http://localhost:8080 (se não mudou a porta), mas vai ver que não tem nenhuma linha em lugar nenhum.

5. Alimente o seu servidor local com os dados da SPTrans. Vamos usar dados já baixados e processados, pois um download e parse completos do site deles demoram bastante. Siga os passos abaixo:

    5.1. Com o servidor local rodando (vide passo 4), entre em http://localhost:8080/token

    5.2. MARQUE "Sign in as Administrator", coloque qualquer e-mail e clique em "Login"

    5.3. Vai aparecer o token de acesso (uma string gigante). Deixe ele quietinho ali.

    5.4. Entre em http://min.us/mWRB4SYJ8, baixe e descompacte o .zip, e mova o arquivo linhas.sqlite para dentro do cruzalinhas/src/sptscraper

    5.5. No prompt de comando, navegue até o cruzalinhas/src/sptscraper e digite:

        ./sptscraper.py upload --url http://localhost:8080 --token TOKEN

     IMPORTANTE: no comando acima, substitua TOKEN pela string que você obteve no passo 5.3 (copie e cole)
     
     Se ele reclamar do interpretador, acrescente "python" na frente, i.e.:

        python ./sptscraper.py upload --url http://localhost:8080 --token TOKEN

Pronto! Reinicie o servidor local e você deve começar a ver linhas capturadas ao clicar no mapa!
   
   
Dicas para desenvolvedores
--------------------------

 - Os arquivos .py do site são bem auto-explicativos: tem um front-end que
   responde requisições AJAX, uma camada de dados e os modelos. O resto são
   bibliotecas (é fundamental entender http://en.wikipedia.org/wiki/Geohash).
 
 - O front-end fica em "static" dentro da pasta do site. O javascript fica em
   marcadores.js, que é minificado dentro do all-scripts.js automaticamente
   caso se use Eclipse (importe o projeto na "raiz" /cruzalinhas/, que contém
   o código do site e do sptscraper).

 - O Eclipse não é obrigatório: se usar outro ambiente,
   gere o all-scripts rodando o arquivo build_all_scripts.py que está em
   cruzalinhas/aux (dica: configure sua IDE para rodar ele automaticamente sempre
   que alterar o marcadores.js ou qualquer js).

 - Qualquer edição do Eclipse vai funcionar bem (o principal objetivo é o auto-
   minify descrito acima, que já está configurado), mas é uma boa plugar um
   editor decente de Python, como o PyDev (http://pydev.org). O mesmo vale
   para HTML e JavaScript - o Aptana Studio (http://aptana.com) é legal se
   a sua máquina aguentar, caso contrário uma opção é o Amateras 
   (http://amateras.sourceforge.jp/cgi-bin/fswiki_en/wiki.cgi?page=EclipseHTMLEditor)
   
 - O sptscraper.py pode ser usado para baixar os HTMLs, atualizar o banco
   local e subir só as diferenças. Chame "./sptscraper.py help" para detalhes.
   
 - Uma introdução a Google App Engine com Python:
   http://www.slideshare.net/chesterbr/google-appenginecpbr5

 - Se fizer alguma mudança interessante, pull requests são bem-vindos. Se
   quiser ajudar e não tiver idéias, consulte a lista de issues em aberto:
   
       https://github.com/chesterbr/cruzalinhas/issues
   
    (e avise para que não trabalhemos no mesmo issue ao mesmo tempo)   
        
        
Motivação e extração de dados dos trajetos (sptscraper)
-------------------------------------------------------

Os itinerários das linhas de transporte público administradas pela SPTrans são
referentes a um serviço PÚBLICO, pago com o SEU e o MEU dinheiro e deveriam
estar disponíveis de uma forma mais acessível que o site deles. Aparentemente
eles existem em algum lugar, pois bons serviços como o Google Maps têm essa
informação, mas o cidadão comum não tem onde baixar.

Esse tipo de falta de transparência no serviço público é inadmissível (vide
http://slidesha.re/acVn37), fato que me levou a desenvolver o sptscraper.py,
módulo independente deste sistema que captura os dados das linhas do site da
SPTrans, armazena os HTMLs, faz o parse para extrair os dados para um banco
SQLite e salva os resultados no cruzalinhas ou exporta em JSON para você usar
como quiser.

Para quem quiser usar os dados já processados, eles devem ser disponibilizados
de tempos em tempos em http://cruzalinhas.minus.com
    

Licença
-------

O código-fonte está disponível sob a licença MIT (vide abaixo). Essencialmente,
o uso é livre, devendo apenas a nota de copyright abaixo ser reproduzida em
cópias/trabalhos derivados.

Ele inclui cópias inalteradas das seguintes bibliotecas, em conformidade com
suas licenças:

* BeautifulSoup - Copyright (c) 2004-2010, Leonard Richardson
* geohash - Escrito por Schuyler Erle, em domínio público
* jquery - Copyright (c) 2010 John Resig, http://jquery.com/
* fancybox - Copyright (c) 2008 - 2010 Janis Skarnelis
* Python JsMin Compress - Copyright (c) 2009 Baruch Even
* argparse - Copyright (c) 2006-2009 Steven J. Bethard

O serviço é prestado na melhor intenção de ajudar as pessoas a se localizar,
sem qualquer garantia, explícita ou implícita de funcionamento, atualização,
precisão ou veracidade das informações prestadas. A fonte original é o site
da SPTrans, que deve ser sempre consultado para validação da informação.


Copyright notice and MIT-style license
--------------------------------------

 cruzalinhas - Copyright (c) 2010-2012 Carlos Duarte do Nascimento (Chester)

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
     
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
 DEALINGS IN THE SOFTWARE.


