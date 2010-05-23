var map;
var ICON_URLS = ["", "http://www.google.com/mapfiles/marker_black.png", "http://www.google.com/mapfiles/marker_brown.png", "http://www.google.com/mapfiles/marker_green.png", "http://www.google.com/mapfiles/marker_purple.png", "http://www.google.com/mapfiles/marker_yellow.png", "http://www.google.com/mapfiles/marker_grey.png", "http://www.google.com/mapfiles/marker_orange.png", "http://www.google.com/mapfiles/marker_white.png"];

var marcadores = {

    _marcadores: [],
    _cache_linhas: [],
    
    get: function(id){
        return _marcadores[id];
    },
    
    add: function(latlng, ordem){
        // Cria um novo marcador
        if (!ordem) {
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
            m.remove(id);
            m.add(event.latLng, ordem);
        });
        // Guarda ele na lista		
        this._marcadores[id] = {
            marker: marker,
            linhas: null,
            ordem: ordem,
            polylines: [],
        }
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
        return id;
    },
    
    atualiza: function(){
        var html = "";
        var count = this.count();
        for (key in this._cache_linhas) {
            this.apagaLinha(key);
        }
        for (ordem = 1; ordem <= count; ordem++) {
            var marcador = this.getMarcadorPelaOrdem(ordem);
            html += '<div style="clear:both;margin:4px;"><img src="' + ICON_URLS[marcador.ordem] + '" style="float:left;margin:2px;"/>';
            if (marcador.linhas) {
                var vazio = true;
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
                                html += "<br/>Aguardando carregar próximo...";
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
                        html += "- " + linha.nome + (this.desenhaLinha(linha) ? "" : "@") + "<br/>";
                        vazio = false;
                    }
                }
                if (vazio) {
                    if ((ordem == count) && (count > 1)) {
                        html += "Destino";
                    }
                    else {
                        html += "<br/>Nenhuma linha aqui";
                    }
                }
            }
            else {
                html += "<br/>Carregando...";
            }
            html += "</div>";
        }
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
    
    remove: function(id){
        var marcador = this._marcadores[id];
        if (marcador.linhas) {
            for (j in marcador.polylines) {
                marcador.polylines[j].setMap(null);
            }
        }
        marcador.marker.setMap(null);
        delete this._marcadores[id];
        //this.atualiza();
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
                marcadores.atualiza();
            });
        }
        if (c && c.pontos) {
            if (!c.polyline) {
                c.polyline = new google.maps.Polyline({
                    map: map,
                    path: c.pontos,
                    strokeColor: "#8A2BE2",
                    strokeWeight: 5,
                    strokeOpacity: 0.5
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
    }
    
}

// Cria o mapa e associa o click à criação de pontos de trajeto
function inicializa(){
    centro_sp = new google.maps.LatLng(-23.548153, -46.633101);
    map = new google.maps.Map(document.getElementById("map_canvas"), {
        zoom: 13,
        center: centro_sp,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    google.maps.event.addListener(map, "click", function(event){
        marcadores.add(event.latLng);
    });
}

$(document).ready(function(){
    inicializa();
    $('#form_busca').submit(function(){
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({
            'address': $('#text_busca').val()
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
});

