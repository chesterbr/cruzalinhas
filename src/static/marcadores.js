google.load("maps", "2.x", {
    "other_params": "sensor=true"
});

var map;
var marcadores = {

    _marcadores: [],
    
    get: function(id){
        return _marcadores[id];
    },
    
    add: function(latlng){
        // Cria um novo marcador
        var id = new Date().getTime();
        marker = new GMarker(latlng, {
            draggable: true
        });
        GEvent.addListener(marker, "dragend", function(latlng){
            m.remove(id);
            m.add(latlng);
        });
        map.addOverlay(marker);
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
							gpontos.push(new GLatLng(pontos[j][0], pontos[j][1]));
						}
						glinha = new GPolyline(gpontos, "#8A2BE2", 5, 0.5);
						map.addOverlay(glinha);
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
				map.removeOverlay(marcador.polylines[j]);
            }
        }
        map.removeOverlay(marcador["marker"]);
		delete this._marcadores[id];
		this.atualiza();      
    }
    
}

// Cria o mapa e associa o click à criação de pontos de trajeto
function inicializa(){
    map = new google.maps.Map2(document.getElementById("map_canvas"));
    map.setCenter(new google.maps.LatLng(-23.548153, -46.633101), 13);
    map.addControl(new GLargeMapControl());
    GEvent.addListener(map, "click", function(overlay, latlng){
        if (latlng) {
            marcadores.add(latlng);
        }
        else 
            if (overlay instanceof GMarker) {
                alert(overlay);
            }
        
    });
}



google.setOnLoadCallback(inicializa);
