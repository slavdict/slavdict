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

        x = $('#etymology_set-group').detach();
        y = $('.derivation_entry').parent('fieldset');
        x.insertAfter(y);

        x = $('#meaningcontext_set-group').detach();
        y = $('#id_meaning').closest('fieldset');
        x.insertAfter(y);

        lang2cssclass = {
            '10': 'grec',
            '11': 'hebrew',
            '16': 'akkadian',
            '17': 'aramaic',
            '18': 'armenian',
            '19': 'georgian',
            '20': 'coptic',
            '21': 'latin',
            '22': 'syriac'
        }
        langclsss1 = 'grec hebrew akkadian aramaic armenian georgian coptic latin syriac'
        langclsss2 = 'grec-translit hebrew-translit akkadian-translit aramaic-translit armenian-translit georgian-translit coptic-translit latin-translit syriac-translit'

        function changeLangCSSClass(x, v){
            if (v){
                var c1 = lang2cssclass[v];
                var c2 = c1 + '-translit';
                x.nextAll('.text').find('input')
                    .removeClass( langclsss1 )
                    .addClass( c1 );
                x.nextAll('.translit').find('input')
                    .removeClass( langclsss2 )
                    .addClass( c2 );
            }
        }

        $('#etymology_set-group .form-row.language').each(function(){
            var x = $(this);
            var v = x.find('select').val();
            changeLangCSSClass(x, v);
        });
        $('#etymology_set-group .form-row.language select').change(function(){
            var i = $(this);
            var x = i.closest('.form-row.language');
            var v = i.val();
            changeLangCSSClass(x, v);
        });

        $('#greekequivalentforexample_set-group .inline-related .inline_label').addClass('grec');
        $('#greekequivalentforexample_set-group .inline-related .text input').addClass('grec');

        $('textarea#id_example').addClass('antconsol');
        $('#example_set-group .example textarea').addClass('antconsol');

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

