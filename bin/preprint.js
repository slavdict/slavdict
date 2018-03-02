$('#main, #main > div')
    .css('witdht', '32em')
    .css('padding', 0)
    .css('margin', 0);

$('.Entry').css('line-height', '1.8em');
$('.FirstParagraph').css('text-indent', 0);

$('*').each(function(){
	var x = $(this);
	x.css('font-family', x.css('font-family'));
});

$('.author').remove();
