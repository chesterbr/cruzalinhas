# cruzalinhas

Aplicativo  e API de acesso a rotas de transporte público de São Paulo, disponível em [cruzalinhas.chester.me](http://cruzalinhas.chester.me)

## Motivação

Os itinerários das linhas de transporte público administradas pela SPTrans são
referentes a um serviço PÚBLICO, e sempre defendi
que estes deveriam estar disponíveis de uma forma mais acessível do que o site (ainda mais sabendo que algumas empresas privadas tinham acesso), permitindo a criação de ferramentas que facilitem a vida do usuário.

Foi criado um programa que capturava os dados diretamente do site da SPTrans (*scraper*) e para demonstrar seu uso,
o site cruzalinhas.

O cruzalinhas permite buscar um endereço ou clicar no mapa e rapidamente ver o traçado de linhas (rotas) que passem perto dele. Ao
marcar pontos sucessivos, o sistema "cruza" as linhas que passam entre eles - daí o nome.

Com a [Lei de Acesso à Informação](https://pt.wikipedia.org/wiki/Lei_de_acesso_%C3%A0_informa%C3%A7%C3%A3o) e uma mudança de postura da SPTrans (que criou um [site para desenvolvedores](http://www.sptrans.com.br/desenvolvedores) no qual é possível baixar os itinerários(\*) no [formato GTFS](https://developers.google.com/transit/gtfs/reference)), o *scraper* se tornou obsoleto, e o cruzalinhas foi atualizado para importar os dados diretamente no formato acima.

<sub>(\*) embora ainda irregular perante a [lei](http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm) por não "possibilitar o acesso **automatizado** por sistemas externos" (Art. 8º, §3º, III). Mas isso é outro assunto.</sub>

## Funcionamento

O sistema de importação e a API (originalmente baseados em [Python](http://www.python.org)/[Google App Engine](https://cloud.google.com/appengine/)) foram refeitos com [Ruby on Rails](http://rubyonrails.org), preservando a compatibilidade com o site (um [aplicativo web de página única](https://en.wikipedia.org/wiki/Single-page_application) feito com HTML e JavaScript) e com aplicativos de terceiros.

## Serviços Utilizados

Os mapas são gerados pela comunidade <a href="https://www.openstreetmap.org">OpenStreetMap</a>, e os _tiles_ são servidos pela <a href="https://www.mapbox.com/">Mapbox</a> através da biblioteca <a href="https://leafletjs.com">Leaflet</a>, com busca de endereços via <a href="http://www.nominatim.org/">Nominatim</a>, nos termos de uso de cada um destes serviços.

## Informações para Desenvolvedores

### Preparando o ambiente de desenvolvimento

Assumindo que você já tenha o [rbenv com ruby-build](https://github.com/rbenv/ruby-build) e `wget` instalados (é o caso do GitHub Codespaces):

```bash
rbenv install -s && bundle && bin/rake db:create db:migrate && bin/rake sptrans:import
```

(alternativamente, troque o `rbenv install -s` por seu método predileto para instalar a versão do Ruby em `.ruby-version`)

### Rodando o servidor

Novamente, o esquema padrão Rails: ```bin/rails server``` e abra [http://localhost:3000](http://localhost:3000).

### Atualizando com dados da SPTrans

Embora a SPTrans tenha disponibilizado os dados GTFS, eles exigem o cadastro para baixar o arquivo, tornando a automação de projetos como este difícil. Felizmente, o OpenMobilityData mantém a última versão dos dados, e a inicialização acima já baixa eles e popula o banco de dados local. Se preciso, rode `bin/rake sptrans:import` para atualizar novamente.

Para abrir a página da linha na SPTrans, é preciso saber o código interno ("CdPjOID") atribuído à versão atual dela , o que não consta na base GTFS. Como o site da SPTrans carrega uma lista com todas as linhas ("letreiros") e códigos atuais, o importador baixa essa lista e gera as URLs no banco de dados.

### API

A referência da API está no próprio site (são apenas duas chamadas), basta clicar no link "API".

### Contribuindo

Existe uma lista de [issues](https://github.com/chesterbr/cruzalinhas/issues), e você pode acrescentar suas sugestões a ela. Caso resolva trabalhar em algum deles (ou em um novo que você criar), deixe um comentário no issue (para evitar que duas pessoas trabalhem na mesma coisa ao mesmo tempo), faça um *fork* e no final submeta um *pull request*.

## Licença

O código-fonte está disponível sob a [licença MIT](LICENSE.md). Essencialmente,
o uso é livre, devendo apenas a nota de copyright ser reproduzida em
cópias/trabalhos derivados.

O serviço é prestado na melhor intenção de ajudar as pessoas a se localizar,
sem qualquer garantia, explícita ou implícita de funcionamento, atualização,
precisão ou veracidade das informações prestadas. A fonte original são os dados disponibilizados pela SPTrans, cujo site deve ser sempre consultado para validação da informação.
