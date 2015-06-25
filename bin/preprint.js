$('.entry').css('margin-top', '40px');

$('.entry-collogroups')
	.css('background-color', 'white')
	.css('margin','0 0 0 -11px');

$('*').each(function(){
	var x = $(this);
	x.css('font-family', x.css('font-family'));
});
