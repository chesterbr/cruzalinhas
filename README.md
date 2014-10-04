# cruzalinhas

Aplicativo  e API de acesso a rotas de transporte público de São Paulo, disponível em [cruzalinhas.com](http://cruzalinhas.com)

## Ambiente de desenvolvimento

Originalmente desenvolvido em Python/Google App Engine, o cruzalinhas atualmente é um aplicativo Ruby on Rails.

### Baixando e inicializando

A inicialização é a tradicional de qualquer aplicativo Rails:

```bash
git clone git@github.com:chesterbr/cruzalinhas.git
cd cruzalinhas
rbenv install # (ou qualquer coisa que garanta o Ruby 2.1.2 instalado)
bundle install
bundle exec db:create db:migrate
```

### Atualizando com dados da SPTrans

```bash
bundle exec gtfs_engine:update geohashes:rehash
```

TODO: fazer atualizar com arquivo local; juntar as duas tasks; explicar como baixar

### Rodando o servidor

Novamente, o esquema padrão Rails ```bundle exec rails server``` e abra [http://localhost:3000](http://localhost:3000).

   
## Observações   
   
 - O front-end fica em "static" dentro da pasta do site. O javascript fica em
   marcadores.js, que está minificado dentro do all-scripts.js. Feio, eu sei,
   mas foi o que deu para fazer na época (refatoração aqui é bem-vinda).
      
 - Se fizer alguma mudança interessante, pull requests são bem-vindos. Se
   quiser ajudar e não tiver idéias, consulte a lista de issues em aberto:
   
       https://github.com/chesterbr/cruzalinhas/issues
   
    (e avise para que não trabalhemos no mesmo issue ao mesmo tempo)   
        

## Motivação Original (texto pré-2012)        

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

## Motivação Atual

Felizmente as coisas melhoraram no plano federal (com a criação da Lei de Acesso à Informação) e municipal (com uma gestão voltada aos usuários do serviço e não a interesses escusos). Atualmente é possível baixar os dados atualizados(*) no site para desenvolvedores da SPTrans.

Juntando isso com o fato de o "scraper" mencionado acima quebrar o tempo todo (deixando os dados desatualizados), *e* o meu foco atual ter mudado de Python para Ruby, resolvi refazer o *back-end* do aplicativo, importando os dados baixados no formato GTFS e disponibilizando a mesma API.

(*) embora o processo ainda seja manual, portanto irregular perante a lei, mas isso é outro assunnto...
    

## Licença

O código-fonte está disponível sob a licença MIT (vide abaixo). Essencialmente,
o uso é livre, devendo apenas a nota de copyright abaixo ser reproduzida em
cópias/trabalhos derivados.

O serviço é prestado na melhor intenção de ajudar as pessoas a se localizar,
sem qualquer garantia, explícita ou implícita de funcionamento, atualização,
precisão ou veracidade das informações prestadas. A fonte original são os dados disponibilizados pela SPTrans, cujo site deve ser sempre consultado para validação da informação.


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


