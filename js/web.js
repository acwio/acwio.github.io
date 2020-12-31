$(document).ready(init());

function init() {
	if(window.location.hash) {
		// Fragment exists
		var hash = window.location.hash.substring(1);
		showTab(hash);
	} else {
		showTab('home');
	}
}

function showTab(tabName){
	$('.tab-pane').hide();
	$('#'+tabName).show();
}