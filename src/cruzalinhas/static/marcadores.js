
//
// marcadores.js
// 
// Contém o código que gerencia os marcadores, carregando as linhas que passam por
// cada um deles e os dados de cada linha, além de lightboxes e outros detalhes de UI.
// 
// IMPORTANTE: Se você MODIFICAR esse arquivo, RODE o build_all_scripts.py, pois
// o html carrega o all_scripts.js e não esse.
// 
// (o Eclipse/Aptana está configurado com um builder apropriado, se tudo correr bem
// ele deve rodar automaticamente - chque se o .py acima está com permissão de
// execução).
// 
// Copyright (c) 2010, 2011 Carlos Duarte do Nascimento (Chester)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of this 
// software and associated documentation files (the "Software"), to deal in the Software 
// without restriction, including without limitation the rights to use, copy, modify, merge, 
// publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons 
// to whom the Software is furnished to do so, subject to the following conditions:
//     
// The above copyright notice and this permission notice shall be included in all copies or 
// substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
// PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
// FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
// DEALINGS IN THE SOFTWARE.
//

// Evitando que alguém entre pelo html antigo
if (location.href.indexOf("/static/") != -1) {
    location.replace("/");
}

// Gerenciamento dos marcadores
var map;
var ICON_URLS = ["", "http://www.google.com/mapfiles/marker_yellow.png", "http://www.google.com/mapfiles/marker_brown.png", "http://www.google.com/mapfiles/marker_green.png", "http://www.google.com/mapfiles/marker_purple.png", "http://www.google.com/mapfiles/marker_grey.png", "http://www.google.com/mapfiles/marker_orange.png", "http://www.google.com/mapfiles/marker_white.png"];
var IMG_LOADER = '<img src="/static/ajax-loader.gif"/>';
var LINHAS_INICIAL = 8;
var LINHAS_INCREMENTO = 30;

var marcadores = {

    _marcadores: [],
    _cache_linhas: [],
    
    get: function(id){
        return _marcadores[id];
    },
    
    // Adiciona um marcador no mapa (e na lista).
    //
    // Se for um marcador pré-existente que está em drag-and-drop, assume que o
    // marcador anterior foi removido (soft) e recebe a posição que ele ocupava.
    // Para drag and drop (que remove e recria), recebe a ordem na lista do que foi removido.
    // Para preencher o "buraco" durante uma remoção, recebe a lista de linhas
    //   do marcador original (vide remove())
    add: function(latlng, preset_ordem, linhas){
        // Cria o marker
        var ordem = preset_ordem;
        if (!preset_ordem) {
            ordem = this.count() + 1;
        }
        var id = new Date().getTime();
        marker = new google.maps.Marker({
            position: latlng,
            map: map,
            draggable: true,
            icon: ICON_URLS[ordem]
        });
        m = this;
        google.maps.event.addListener(marker, "dragend", function(event){
            var ordem_orig = marcadores._marcadores[id].ordem;
            m.soft_remove(id);
            m.add(event.latLng, ordem_orig);
        });
        // Guarda ele na lista
        this._marcadores[id] = {
            id: id,
            marker: marker,
            linhas: null,
            max_linhas: LINHAS_INICIAL,
            ordem: ordem,
            polylines: [],
            oculta_linha: []
        }
        if (linhas) {
            m._marcadores[id].linhas = linhas;
        }
        else {
            // Recupera as linhas que passam por ele (em background)
            $.ajax({
                url: "/linhasquepassam.json",
                dataType: 'json',
                data: {
                    lat: latlng.lat(),
                    lng: latlng.lng()
                },
                success: function(data){
                    if (m._marcadores[id]) {
                        m._marcadores[id].linhas = data;
                        m.atualiza();
                    }
                },
                retry_ms: 1000,
                error: function(request, status, error){
                    if (m._marcadores[id]) {
                        a = this;
                        setTimeout(function(){
                            $.ajax(a)
                        }, this.retry_ms);
                        this.retry_ms *= 2;
                    }
                }
            });
            this.atualiza();
        }
        return id;
    },
    
    mostrou_instrucoes: false,
    atualiza: function(){
        var html = "";
        var count = this.count();
        for (key in this._cache_linhas) {
            this.apagaLinha(key);
        }
        if (count == 0) {
            if (!this.mostrou_instrucoes) {
                $("#div_lista").animate({
                    width: '-=50'
                }, 0);
                $("#div_lista").html($("#div_instrucoes").clone());
                $("#div_lista").animate({
                    width: '+=50'
                }, 1000);
            }
            this.mostrou_instrucoes = true;
            return;
        }
        this.mostrou_instrucoes = false;
        for (ordem = 1; ordem <= count; ordem++) {
            var marcador = this.getMarcadorPelaOrdem(ordem);
            if (!marcador) {
                // estamos no meio de uma remoção, relaxa
                return;
            }
            html += '<div style="margin-bottom:4px;clear:both;">';
            html += ' <p style="margin:0px; text-align:center;">';
            html += '  <img style="max-height:17px" src="' + ICON_URLS[marcador.ordem] + '"/><br/>';
            html += '  <span class="link_remover"><a class="link_remover" title="remove o pino do mapa" href="javascript:void(0)" onClick="javascript:marcadores.remove(' + marcador.id + '); return false">REMOVER</a></span>';
            html += ' </p>';
            if (marcador.linhas) {
                var vazio = true;
                var linhas_no_marcador = 0;
                for (j in marcador.linhas) {
                    var mostra = false;
                    var linha = marcador.linhas[j];
                    if (count == 1) {
                        // Só tem um marcador, mostra todas as linhas
                        mostra = true;
                    }
                    else {
                        // Se não for o último marcador, mostra só as que também passam no próximo
                        if (marcador.ordem < count) {
                            proximoMarcador = this.getMarcadorPelaOrdem(ordem + 1);
                            if (!proximoMarcador || (!proximoMarcador.linhas)) {
                                html += IMG_LOADER;
                                vazio = false;
                                break;
                            }
                            else {
                                for (k in proximoMarcador.linhas) {
                                    if (linha.nome == proximoMarcador.linhas[k].nome) {
                                        mostra = true;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    if (mostra) {
                        linhas_no_marcador++;
                        if (linhas_no_marcador > marcador.max_linhas) {
                            html += '<div style="clear:both"><p style="text-align:center;"><a href="javascript:void(0)" onClick="marcadores.mais(' + marcador.id + ');return false;">mais...</a></p></div>';
                            break;
                        }
                        var conteudo_legenda = IMG_LOADER;
                        if (marcador.oculta_linha[linha.key] || this.desenhaLinha(linha)) {
                            conteudo_legenda = '<input type="checkbox" title="oculta/exibe no mapa"' +
                            (marcador.oculta_linha[linha.key] ? '' : 'checked="checked"') +
                            ' onClick="marcadores.alterna_linha(' +
                            marcador.id +
                            ',\'' +
                            linha.key +
                            '\')">';
                        }
                        html += '<div class="legenda_linha" style="background-color:' +
                        this.corDaLinha(linha) +
                        '">' +
                        conteudo_legenda +
                        '</div>' +
                        '<p class="p_linha p_linha_' +
                        linha.key +
                        '" style="float:left;margin:1px"><a href="' +
                        linha.url +
                        '" target="_blank">' +
                        marcadores.ajustaNome(linha.nome) +
                        '</a>' +
                        '</p>';
                        vazio = false;
                    }
                }
                if (vazio) {
                    if (count == 1) {
                        html += this.pmsg("nenhuma linha passa aqui");
                    }
                    else 
                        if (ordem < count) {
                            html += this.pmsg("nenhuma linha passa entre eles");
                        }
                }
            }
            else {
                html += IMG_LOADER;
            }
            html += "</div>";
        }
        html += '<p class="p_dicas">Arraste o pino no mapa para ajustar o local, ou clique em REMOVER para jogar ele fora.<br/><br/>';
        html += 'Com dois ou mais pinos, só aparecem as linhas que passam entre eles.<br/><br/>';
        html += 'Definidos os pinos, use <input type="checkbox" disabled="true" checked="chekced"/> para esconder linhas indesejadas.<br/><br/>';
        html += 'A busca não leva em conta os pontos de ônibus e estações, apenas a proximidade do trajeto.</p>';
        
        $("#div_lista").html(html);
    },
    
    getMarcadorPelaOrdem: function(ordem){
        var ms = this._marcadores;
        for (j in ms) {
            if (ms[j].ordem == ordem) {
                return ms[j];
            }
        }
        return null;
    },
    
    count: function(){
        var j = 0;
        for (marcador in this._marcadores) {
            j++;
        }
        return j;
    },
    
    // Aumenta a quantidade de linhas mostrada num marcador e atualiza a listagem
    mais: function(id){
        var marcador = this._marcadores[id];
        if (marcador) {
            marcador.max_linhas += LINHAS_INCREMENTO;
        }
        this.atualiza();
    },
    
    // Tira um marcador da lista (mas não preenche o buraco dele)
    soft_remove: function(id){
        var marcador = this._marcadores[id];
        if (marcador.linhas) {
            for (j in marcador.polylines) {
                marcador.polylines[j].setMap(null);
            }
        }
        marcador.marker.setMap(null);
        delete this._marcadores[id];
    },
    
    // Remove um marcador pra valer (movendo os outros acima na lista)
    remove: function(id){
        var ordem = this._marcadores[id].ordem;
        var ultima_ordem = this.count();
        this.soft_remove(id);
        for (i = ordem + 1; i <= ultima_ordem; i++) {
            var m = this.getMarcadorPelaOrdem(i);
            var linhas = m.linhas;
            this.soft_remove(m.id);
            this.add(m.marker.position, i - 1, linhas);
        }
        this.atualiza();
    },
    
    // Se a linha já está no cache desenha e retorna true
    // Caso não esteja (ou esteja mas ainda não tenha carregado), retorna false
    //   (e pede pra carregar se ainda não o fez)
    desenhaLinha: function(linha){
        var cache = this._cache_linhas;
        var c = cache[linha.key];
        if (!c) {
            cache[linha.key] = {};
            $.getJSON("/linha.json", {
                key: linha.key
            }, function(pontos){
                gpontos = []
                for (j in pontos) {
                    gpontos.push(new google.maps.LatLng(pontos[j][0], pontos[j][1]));
                }
                cache[linha.key].pontos = gpontos;
                cache[linha.key].cor = marcadores.proximacor();
                marcadores.atualiza();
            });
        }
        if (c && c.pontos) {
            if (!c.polyline) {
                c.polyline = new google.maps.Polyline({
                    map: map,
                    path: c.pontos,
                    strokeColor: c.cor,
                    strokeWeight: 5,
                    strokeOpacity: 0.5
                });
                google.maps.event.addListener(c.polyline, "mouseover", function(latlng){
                    $(".p_linha_" + linha.key).addClass("destaca_linha");
                });
                google.maps.event.addListener(c.polyline, "mouseout", function(latlng){
                    $(".p_linha_" + linha.key).removeClass("destaca_linha");
                });
            }
            return true;
        }
        return false;
    },
    
    // Remove uma linha do mapa, se já estiver desenhada (mas não apaga do cache)
    apagaLinha: function(key){
        c = this._cache_linhas[key];
        if (c && c.polyline) {
            c.polyline.setMap(null);
            delete c.polyline;
        }
    },
    
    // mostra/esconde a linha n do ordem-ésima marcador
    alterna_linha: function(id, key){
        var marcador = this._marcadores[id];
        if (marcador) {
            marcador.oculta_linha[key] = !marcador.oculta_linha[key];
        }
        this.atualiza();
    },
    
    pmsg: function(texto){
        return '<p style="color:red;margin:0px;font-style:italic;text-align:center;">' + texto + "</p>";
    },
    
    _semente_cor: 1,
    proximacor: function(){
        this._semente_cor += 3;
        if (this._semente_cor > 62) {
            this._semente_cor -= 62;
        }
        var h = this._semente_cor.toString(4);
        while (h.length < 3) 
            h = "0" + h;
        var c = h[0] * 256 * 4 + h[1] * 16 * 4 + h[2] * 4;
        cor = c.toString(16)
        while (cor.length < 3) 
            cor = "0" + cor;
        return "#" + cor;
    },
    
    corDaLinha: function(linha){
        var c = this._cache_linhas[linha.key];
        if (c && c.cor) {
            return c.cor;
        }
        else {
            return "#FFF";
        }
        
    },
    
    // Deixa o nome da linha menos feio
    ajustaNome: function(nome){
        // Converte 1a. letra pra upper, outras pra lower
        var baixar = false;
        var result = "";
        for (i = 0; i < nome.length; i++) {
            var c = nome[i];
            if (baixar) {
                result += c.toLowerCase();
            }
            else {
                result += c;
            }
            baixar = (c.toLowerCase() != c);
        }
        // Separa ida e volta
        return result.replace("/", " / ");
    }
    
    
    
    
    
}

// Cria o mapa e associa o click à criação de pontos de trajeto
function inicializa(){
    centro_sp = new google.maps.LatLng(-23.548153, -46.633101);
    map = new google.maps.Map(document.getElementById("map_canvas"), {
        zoom: 13,
        scaleControl: true,
        center: centro_sp,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    google.maps.event.addListener(map, "click", function(event){
        if (marcadores.count() <= 5) {
            marcadores.add(event.latLng);
        }
        else {
            alert("Desculpe, não consigo colocar mais marcadores");
        }
    });
    $("#text_busca").focus(function(){
        if ($(this).hasClass("input_instrucoes")) {
            $(this).removeClass("input_instrucoes");
            $(this).attr("value", "");
        }
    });
    
    marcadores.atualiza();
}




$(document).ready(function(){
    // Prepara lightboxes
    $("#link_oque").fancybox({
        'width': 630,
        'height': 350,
        'autoDimensions': false,
        'autoScale': false
    });
    $("#link_porque").fancybox({
        'width': 610,
        'height': 350,
        'autoDimensions': false,
        'autoScale': false
    });
    $("#link_como").fancybox({
        'width': 630,
        'height': 400,
        'autoDimensions': false,
        'autoScale': false
    });
    $("#link_api").fancybox({
        'width': 750,
        'height': 525,
        'autoDimensions': false,
        'autoScale': false
    });
    $("#link_sobre").fancybox({
        'width': 500,
        'height': 240,
        'autoDimensions': false,
        'autoScale': false,
    });
    
    inicializa();
    $('#form_busca').submit(function(){
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({
            'address': $('#text_busca').val() + ", São Paulo, SP"
        }, function(results, status){
            if (status == google.maps.GeocoderStatus.OK) {
                latlng = results[0].geometry.location;
                map.panTo(latlng);
                marcadores.add(latlng);
            }
            else {
                alert("Não foi possível localizar o endereço (" + status + ")");
            }
        })
        return false;
    });
    
    // Pré-abre lightboxes oriundos de links em hash
    if (location.hash) {
        window.setTimeout(function(){
            $("#link_" + location.hash.substring(1)).trigger("click");
        }, 1000);
    }
    
    
});

