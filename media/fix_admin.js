(function($) {
    $(document).ready(function() {

        $('label').each(function(){
            var x = $(this);
            var t = x.html();
            t = t.replace(/:/, '');
            x.html(t);
        });

        $('.vCheckboxLabel')
            .removeClass('vCheckboxLabel')
            .each(function(){
                var x = $(this);
                var y = x.prev();
                x = x.detach();
                x.insertBefore(y);
        });


        var x = $('#orthographic_variants-group').detach();
        var y = $('.civil_equivalent').parent('fieldset');
        x.insertBefore(y);

        x = $('#meaningcontext_set-group').detach();
        y = $('#id_meaning').closest('fieldset');
        x.insertAfter(y);

        function updateAddAnother(){

            $('div.add-row').each(function(){
                var x = $(this).children('a');
                var t = x.html();
                t = t.replace(/Добавить еще один/, 'Добавить');
                x.html(t);
            });

            var c = $('#id_orthographic_variants-TOTAL_FORMS');
            if (c.val()==0){
                $('#orthographic_variants-group').find('div.add-row a').click();
            }

        }
        setTimeout(updateAddAnother, 1000);
    });
})(django.jQuery);

