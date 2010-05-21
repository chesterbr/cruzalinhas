var map;
var marcadores = {

    _marcadores: [],
    
    get: function(id){
        return _marcadores[id];
    },
    
    add: function(latlng){
        // Cria um novo marcador
        var id = new Date().getTime();
        marker = new google.maps.Marker({
            position: latlng,
            map: map,
            draggable: true
        });
        google.maps.event.addListener(marker, "dragend", function(event){
            m.remove(id);
            m.add(event.latLng);
        });
        // Guarda ele na lista		
        this._marcadores[id] = {
            "marker": marker,
            "linhas": null,
            "polylines": []
        }
        // Recupera as linhas que passam por ele (em background)
        m = this;
        $.getJSON("/linhasquepassam.json", {
            lat: latlng.lat(),
            lng: latlng.lng()
        }, function(linhas){
            m._marcadores[id].linhas = linhas;
            m.atualiza();
            for (i in linhas) {
                $.getJSON("/linha.json", {
                    key: linhas[i].key
                }, function(pontos){
                    if (m._marcadores[id]) {
                        gpontos = []
                        for (j in pontos) {
                            gpontos.push(new google.maps.LatLng(pontos[j][0], pontos[j][1]));
                        }
                        glinha = new google.maps.Polyline({
                            map: map,
                            path: gpontos,
                            strokeColor: "#8A2BE2",
                            strokeWeight: 5,
                            strokeOpacity: 0.5
                        });
                        m._marcadores[id].polylines.push(glinha);
                    }
                });
            }
        });
        this.atualiza();
        return id;
    },
    
    atualiza: function(){
        html = "";
        for (i in this._marcadores) {
            marcador = this._marcadores[i];
            if (marcador.linhas) {
                html += "Linhas:<br/>";
                for (j in marcador.linhas) {
                    html += "- " + marcador.linhas[j].nome + "<br/>";
                }
            }
            else {
                html += "Carregando..." + i + "<br/>";
            }
        }
        $("#div_lista").html(html);
    },
    
    remove: function(id){
        marcador = this._marcadores[id];
        if (marcador.linhas) {
            for (j in marcador.polylines) {
                marcador.polylines[j].setMap(null);
            }
        }
        marcador["marker"].setMap(null);
        delete this._marcadores[id];
        this.atualiza();
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
        var geocoder = new GClientGeocoder();
        geocoder.getLatLng($('#text_busca').val(), function(latlng){
            map.panTo(latlng);
            marcadores.add(latlng);
        })
        return false;
    });
});

