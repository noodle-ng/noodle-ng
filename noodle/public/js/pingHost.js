doc = currentDocument();

// Diese Funktion wird nach dem Ping aufgerufen (Callback)
// und wertet das Ergebnis aus
var gotPing = function (data) {
	img_online  = IMG({src: "/images/ping_online.png"});
	img_offline = IMG({src: "/images/ping_offline.png"});
	for (var i = 0; i < ping_Hosts_pending.length; i++){
		if ( ping_Hosts_pending[i].getAttribute('value') == data["host"]) {
			if (data["time"] == false){
				swapDOM(ping_Hosts_pending[i], img_offline);
			}
			else {
				swapDOM(ping_Hosts_pending[i], img_online);
			};
		};
	};
};

var ping_onload = function(){
	
	// das rotierende gif laden
	ping_Hosts = doc.getElementsByName("ping_Host");
	ping_Hosts_pending = new Array();
	while (ping_Hosts.length > 0){
		ip = ping_Hosts[0].getAttribute('value');
		img_rotation = IMG({src: "/images/ping_rotation.gif"});
		updateNodeAttributes(img_rotation, {'name': 'actually_ping_Host', 'value': ip});
		ping_Hosts_pending.push(img_rotation)
		swapDOM(ping_Hosts[0], img_rotation);
	};
	
	// die callbacks setzen
	callbacks = new Array();
	for (var i = 0; i < ping_Hosts_pending.length; i++){
		ip = ping_Hosts_pending[i].getAttribute('value');
		var d = loadJSONDoc("/ping?ip=" + ip);
		callbacks.push(d);
		callbacks[i].addCallback(gotPing);
	};
	
};

MochiKit.DOM.addLoadEvent(ping_onload)