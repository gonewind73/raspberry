/**
 * 何国锋
 * 2018.9.15
 */

$(document).ready(
	function() {
		init()
    });
    
function init() {

    set_event()
    IOT.bStatus = false;
    IOT.bWeather = "sunny";
    IOT.config.bAutomatic = false;
    IOT.config.out_time = 10;
	IOT.config.in_time = 15;
	setInterval(getStatus,60000);
}
    

var IOT = {
    bWeather:"sunny", // sunny,rain,cloud
    bStatus:false,
    config:{bAutomatic:false,out_time:10,in_time:15}
	
	}

function set_event() {
    var ns = 0.85
    var os = 1
    $('.Action').click(function(e) {
            do_action(e);
    }).hover(function() {
        $(this).stop().animate({
            scale : os + 0.15
        }, 250);
    }, function() {
        $(this).stop().animate({
            scale : ns + 0.15
        }, 125);
	})
	$('#status').click(function(e) {
		getStatus()
	})
    $('.Setup#automatic').click(function(e) {
        config($(this).attr('id'))
        
        })
        
    
}
function config(id){
	checked = $("#automatic").attr("checked")
	$.ajax({url:"/config?auto="+checked,
				type:"get",
				dataType:"json",
				success: updateStatus,
				//error: alert("error!")
				})
}

function do_action(e){
	console.log(e)
	$.ajax({url:"/action?action="+e.currentTarget.id,
				type:"get",
				dataType:"json",
				success: updateStatus,
				//error: alert("error!")
				})
	}
	
function getStatus(){

	htmlobj=$.ajax({url:"/getstatus",
					type:"get",
					dataType:"json",
					success: updateStatus,
						})			

}

function updateStatus(data){
	// $("#status").html("阳光："+ data.sunny + " 下雨："+ data.water );
	if(data==null)return
	console.log(data)
	$(".Status").hide()
	if(data.sunny) $("#sunny").show()
	if(data.water) $("#rainy").show()
	if(data.sunny==0 && data.water==0) $("#cloudy").show()

	$(".Action").show()
	$("#rackstatus").show()
	if(data.innermost){
		$("#rackstatus").attr("status","in")
		$("#pullin").hide()
	} 
	if(data.outtermost){
		$("#rackstatus").attr("status","out")
		$("#pullout").hide()
	} 

	if(data.automatic) $("#automatic").attr("checked",true)
}





function log(s) {
	if (DEBUG) {
		if (typeof (console) != 'undefined') {
			if (console) {
				if (navigator.userAgent.toLowerCase()
						.indexOf("applewebkit") != -1) {
					console.log(s)
				} else {
					console.log.apply(this, arguments)
				}
			}
		}
	}
}


	
window.onunload = window.onbeforeunload = function(e) {

};





