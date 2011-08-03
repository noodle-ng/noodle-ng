doc = currentDocument();

var browse_onload = function(){

	jQuery("#async_json_1").tree({
			data : { 
				type : "json",
				opts : {
					url : "async_json_data.json"
				}
			}
		});
	
};

MochiKit.DOM.addLoadEvent(browse_onload)