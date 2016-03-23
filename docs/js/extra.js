$( document ).ready(function() {
	
	// add link to demo
	$('ul.navbar-nav').
		not(".navbar-right").
		append( '<li>' +
		    '<a href="/messaging/js/django-rest-messaging-demo-production/">Demo</a>' +
        '</li>' );
	
	// do not deactivate next button
	var nextLi = $('ul.navbar-right').
		children('li').
		eq(1);
	
	if(nextLi.hasClass( "disabled" )){
		// we enable it
		nextLi.attr('class', '');
		// we set the link to the example
		nextLi.html('<a href="/messaging/js/django-rest-messaging-demo-production/">'+
	            'Next <i class="fa fa-arrow-right"></i>'+
	            '</a>');
	}
	
});