(function($) {
    $(document).ready(function() {

        var qs = location.search;
        if (qs) {
            qs = qs.substring(1, qs.length);
            var qamp = qs.split("&");
            for (var i=0; i<qamp.length; i++){
                var qskv = qamp[i].split("=");
                var qkey = qskv[0];
                var qvalue = qskv[1];
                switch (qkey) {
                    case 'entry':
                        $('#id_entry_container').val(qvalue);
                        $('#id_base_entry').val(qvalue);
                        break;
                    case 'collogroup':
                        $('#id_collogroup_container').val(qvalue);
                        break;
                    case 'meaning':
                        $('#id_meaning').val(qvalue);
                        $('#id_base_meaning').val(qvalue);
                        break;
                    case 'parent_meaning':
                        $('#id_parent_meaning').val(qvalue);
                        break;
                };
            };
        }

        /* Убираем у всех label двоеточия */
        $('label').each(function(){
            var x = $(this);
            var t = x.html();
            t = t.replace(/:/, '');
            x.html(t);
        });

        /* Убираем кнопки "сохранить и продолжить редактирование"
         * и "сохранить и добавить другой объект". */
        $(':submit[name="_continue"], :submit[name="_addanother"]').hide();

        /* Для всех полей с галочками переносим ярлыки из расположения после
         * галочки в расположение перед галочкой. */
        $('.vCheckboxLabel')
            .removeClass('vCheckboxLabel')
            .each(function(){
                var x = $(this);
                var y = x.prev();
                x = x.detach();
                x.insertBefore(y);
        });

        /* Переносим всю группу полей орфографических вариантов в расположение
         * перед полем гражданского написания. */
        var x = $('#orthographic_variants-group').detach();
        var y = $('.civil_equivalent').parent('fieldset');
        x.insertBefore(y);

        /* Переносим группу полей словоформ (пока в списке типов только
         * причастия) в расположение после полей форм глагола. */
        x = $('#wordform_set-group').detach();
        x.addClass('hidden verb');
        y = $('#id_sg1').closest('fieldset');
        x.insertAfter(y);

        /* Переносим группу полей с этимологиями в расположение после поля
         * "образовано от" (морфолгическая деривация). */
        x = $('#etymology_set-group').detach();
        y = $('.derivation_entry').parent('fieldset');
        x.insertAfter(y);

        /* Переносим группу полей контекстов значения в расположение
         * непосредственно перед полем значения. */
        x = $('#meaningcontext_set-group').detach();
        y = $('#id_meaning').closest('fieldset');
        x.insertAfter(y);

        /* Переносим группу полей греческих эквивалентов для значения
         * в расположение после группы полей контекста значения. */
        x = $('#greekequivalentformeaning_set-group').detach();
        y = $('#meaningcontext_set-group');
        x.insertAfter(y);


        /* Для текста этимологии и для транслита устанавливаем нужные
         * CSS-классы в зависимости от конкретного языка. Такая установка
         * проводится и при загрузке страницы и вешается на событие изменения
         * значения поля языка конкретной этимологии. */
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


        /* Скрываем и отображаем поля в зависимости от выбранной части речи. */
        partsOfSpeech = {
            "1": 'noun', // отображение id в справочнике значений категорий
                         // на названия категорий на английском.
            "2": 'verb',
            "3": 'adjective',
            "4": 'adverb',
            "5": 'preposition',
            "6": 'pronoun',
            "7": 'conjunction',
            "8": 'particle',
            "9": 'interjection',
            "40":'participle'
        };

        var v = $('select#id_part_of_speech').val();
        if (v) {
            $('.' + partsOfSpeech[v]).show();
        }

        $('select#id_part_of_speech').change(function(){
            var v = $(this).val();
            $('.noun, .verb, .adjective, .adverb, .preposition, .pronoun, .conjunction, .particle, .interjection, .participle').hide();
            if (v) {
                $('.' + partsOfSpeech[v]).show();
            }
        });


        /* Скрываем или отображаем поля в зависимости от
         * изменяемости/неизменяемости существительного или прилагательного. */
        function checkUninflected() {
            if ( $('#id_uninflected').is(':checked') ) {
                $('.genitive').hide();
                $('.tantum').hide();
                $('.short_form').hide();
            } else {
                $('.genitive').show();
                $('.tantum').show();
                $('.short_form').show();
            }
        }

        checkUninflected();
        $('#id_uninflected').click(checkUninflected);

        /* Скрываем или отображаем поля для выбранного типа имени собственного.
         * */
        onyms = {
            "35": 'canonical_name', // имя
            "36": '',               // топоним
            "37": 'nom_sg',         // народ
            "38": ''                // другое
        }

        v = $('select#id_onym').val();
        if (v) {
            $('.' + onyms[v]).show();
        }

        $('select#id_onym').change(function(){
            var v = $(this).val();
            $('.canonical_name, .nom_sg').hide();
            if (v) {
                $('.' + onyms[v]).show();
            }
        });

        // Создаем гражданское напиание
        // для заглавного слова
        x = $('#id_civil_equivalent');
        v = x.val();
        var v2 = $('#id_orthographic_variants-0-idem').val();
        if (!v && v2) {
            x.val(antconc_civilrus_word(v2));
        }
        if (v && v.indexOf('*') > -1) {
            x.addClass('myerr');
        } else {
            x.removeClass('myerr');
        }

        $('#id_orthographic_variants-0-idem').keyup(function(){
            x.val(antconc_civilrus_word($(this).val()));
            if (x.val() && x.val().indexOf('*') > -1){
                x.addClass('myerr');
            } else {
                x.removeClass('myerr');
            }
        });

        x.keyup(function(){
            if (x.val() && x.val().indexOf('*') > -1){
                x.addClass('myerr');
            } else {
                x.removeClass('myerr');
            }
        });

        // для словосочетаний
        $('input[name|="collocation_set"]')
            .filter('input[name$="-civil_equivalent"]')
            .each(function(){
                var ceq = $(this);
                var ceqv = ceq.val();
                var a = "collocation_set-" + ceq.attr('name').split("-")[1] + "-collocation";
                var collov = $('#id_' + a).val();
                if (!ceqv && collov) {
                    ceq.val(antconc_civilrus_word(collov));
                }
                if (ceqv && ceqv.indexOf('*') > -1){
                    ceq.addClass('myerr');
                } else {
                    ceq.removeClass('myerr');
                }
                ceq.keyup(function(){
                    var ceqv = $(this).val();
                    if (ceqv && ceqv.indexOf('*') > -1){
                        ceq.addClass('myerr');
                    } else {
                        ceq.removeClass('myerr');
                    }
                });
            });

        $('input[name|="collocation_set"]')
            .filter('input[name$="-collocation"]')
            .each(function(){
                $(this).keyup(function(){
                    var collo = $(this);
                    var collov = collo.val();
                    var a = "collocation_set-" + collo.attr('name').split("-")[1] + "-civil_equivalent";
                    var ceq = $('#id_' + a);
                    ceq.val(antconc_civilrus_word(collov));
                    var ceqv = ceq.val();
                    if (ceqv && ceqv.indexOf('*') > -1){
                        ceq.addClass('myerr');
                    } else {
                        ceq.removeClass('myerr');
                    }
                });
            });

        /* Действия, которые необходимо отложить хотя бы на секунду, чтобы они
         * были успешно выполнены. */
        function returnToPostponed(){

            /* Заменяем все надписи "Добавить ещё один" на просто "Добавить". */
            $('div.add-row').each(function(){
                var x = $(this).children('a');
                var t = x.html();
                t = t.replace(/Добавить еще один/, 'Добавить');
                x.html(t);
            });

            /* Для орфографических вариантов если не добавлено ещё ни одного,
             * то добавляем пустое поле. Если же уже есть один или более, то
             * пустого поля не добавляем. */
            var c = $('#id_orthographic_variants-TOTAL_FORMS');
            if (c.val()==0){
                $('#orthographic_variants-group').find('div.add-row a').click();
            }

        }
        setTimeout(returnToPostponed, 1000);
    });
})(django.jQuery);

