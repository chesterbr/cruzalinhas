// Evitando que alguém entre pelo html antigo
if (location.href.indexOf("/static/")!=-1) {
	location.replace("/");
}

var map;
var ICON_URLS = ["", "http://www.google.com/mapfiles/marker_black.png", "http://www.google.com/mapfiles/marker_brown.png", "http://www.google.com/mapfiles/marker_green.png", "http://www.google.com/mapfiles/marker_purple.png", "http://www.google.com/mapfiles/marker_yellow.png", "http://www.google.com/mapfiles/marker_grey.png", "http://www.google.com/mapfiles/marker_orange.png", "http://www.google.com/mapfiles/marker_white.png"];
var IMG_LOADER= '<img src="/static/ajax-loader.gif"/>';

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
            m.soft_remove(id);
            m.add(event.latLng, ordem);
        });
        // Guarda ele na lista		
        this._marcadores[id] = {
			id: id,
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
		if (count==0) {
			$("#div_lista").animate({width:'-=50'},0);
			$("#div_lista").html($("#div_instrucoes").clone());
			$("#div_lista").animate({width:'+=50'},1000);
			return;			
		}
        for (ordem = 1; ordem <= count; ordem++) {
            var marcador = this.getMarcadorPelaOrdem(ordem);
			if (!marcador) {
				// estamos no meio de uma remoção, relaxa
				return;
			}
            html += '<div style="margin-bottom:4px;clear:both;"><p style="margin:0px; text-align:center;"><img style="max-height:17px" src="' + ICON_URLS[marcador.ordem] + '"/><br/><span class="link_remover">(arraste no mapa ou <a class="link_remover" href="javascript:void(0)" onClick="javascript:marcadores.remove('+marcador.id+'); return false">remova</a>)</span></p>';
            if (marcador.linhas) {
                var vazio = true;
                for (j in marcador.linhas) {
                    var mostra = false;
                    var linha = marcador.linhas[j];
//                    if (!this.passaMesmo(marcador, linha)) {
//                        continue;
//                    }
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
						var gif_loading = (this.desenhaLinha(linha) ? "&nbsp;" : IMG_LOADER);
                        html +=  '<div class="legenda_linha" style="background-color:' +
								 this.corDaLinha(linha) +
								 '">' + gif_loading + '</div>' +
								 '<p class="p_linha p_linha_' + 
								 linha.key +
								 '" style="float:left;margin:1px"><a href="' + 
								 linha.url + 
								 '" target="_blank">' + 
								 linha.nome + '</a>' + 
								 '</p>';
                        vazio = false;
                    }
                }
                if (vazio) {
					if (count == 1) {
                        html += this.pmsg("nenhuma linha passa aqui");
                    } else if (ordem < count) {
                        html += this.pmsg("nenhuma linha liga com o ponto abaixo");						
					}
                }
            }
            else {
                html += IMG_LOADER;
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
        //this.atualiza();
    },

    remove: function(id) {
		var ordem = this._marcadores[id].ordem;
		for(i=this.count(); i>ordem;i--) {
			var m = this.getMarcadorPelaOrdem(i);
			this.soft_remove(m.id);
			this.add(m.marker.position, i-1);
		}
		this.soft_remove(id);
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
				google.maps.event.addListener(c.polyline, "mouseover", function(latlng) {
					$(".p_linha_"+linha.key).addClass("destaca_linha");
				});
				google.maps.event.addListener(c.polyline, "mouseout", function(latlng) {
					$(".p_linha_"+linha.key).removeClass("destaca_linha");
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
	
	pmsg: function(texto) {
		return '<p style="color:red;margin:0px;font-style:italic;text-align:center;">'+texto+"</p>";
	},
	
	_semente_cor: 1,
	proximacor: function() {
		this._semente_cor+=3;
		if (this._semente_cor > 62) {
			this._semente_cor -= 62;
		}
		var h = this._semente_cor.toString(4);
   		while (h.length<3) h="0"+h;
   		var c = h[0]*256*4+h[1]*16*4+h[2]*4;
   		cor = c.toString(16)
   		while (cor.length<3) cor="0"+cor;
		return "#"+cor;
	},
	
	corDaLinha: function(linha) {
        var c = this._cache_linhas[linha.key];
		if (c && c.cor) {
			return c.cor;
		} else {
			return "#FFF";
		}
   		
	}


	
	/*,

    
    // Verifica se o marcador passa pelo linha com precisão decente
    passaMesmo: function(marcador, linha){
        var linha_cache = this._cache_linhas[linha.key];
        if (linha_cache) {
            for (i in linha_cache.pontos) {
                if (this.dist(linha_cache.pontos[i], 
							  ponto, marcador.marker.position) < this.DIST_MIN) {
                    return true;
                }
            }
        }
        return false;
    },
    
	DIST_MIN: 10, // distancia minima em metros p/ considerar match
	
    dist: function(a, b){
        var R = 6371; // km
        return Math.acos(Math.sin(lat1) * Math.sin(lat2) +
        Math.cos(lat1) * Math.cos(lat2) *
        Math.cos(lon2 - lon1)) *
        R;
    }*/
    
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
		if (marcadores.count()<=5) {
        	marcadores.add(event.latLng);
		} else {
			alert("Desculpe, não consigo colocar mais marcadores");
		}
    });
	$("#text_busca").focus(function () {
		if ($(this).hasClass("input_instrucoes")) {
			$(this).removeClass("input_instrucoes");
			$(this).attr("value", "");
		}
	});

	marcadores.atualiza();
}

$(document).ready(function(){
	$("#link_oque").fancybox({
		'width'				: 620,
		'height'			: 280,
		'autoDimensions'	: false,
		'autoScale'			: false
	});
	$("#link_porque").fancybox({
		'width'				: 620,
		'height'			: 250,
		'autoDimensions'	: false,
		'autoScale'			: false
	});
	$("#link_como").fancybox({
		'width'				: 620,
		'height'			: 335,
		'autoDimensions'	: false,
		'autoScale'			: false
	});

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

