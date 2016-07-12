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

        /* Меняем заголовок в списке лексем для колонки с флажками,
         * указывающими представлен ли вариант без титла в текстах или нет */
        $('.column-untitled_exists').html('Титл');

        /* Добавляем ссылки на отображение статей помимо ссылок редактирования */
        var RE = /entry\/(\d+)\//;
        $('th.field-headword a').each(function(){
            var x = $(this).parent().prev('td.field-civil_inv'),
                text = x.html(),
                y = RE.exec(this.href),
                id = y && y[1];
            if (id) {
                x.html('<a href="/entries/' + id + '/">' + text + '</a>');
            }
        });

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
        var y = $('.field-civil_equivalent').parent('fieldset');
        x.insertBefore(y);

        /* Переносим группу полей словоформ (пока в списке типов только
         * причастия) в расположение после полей форм глагола. */
        x = $('#participle_set-group').detach();
        x.addClass('hidden verb');
        y = $('#id_sg1').closest('fieldset');
        x.insertAfter(y);

        /* Переносим группу полей с этимологиями в расположение после поля
         * "образовано от" (морфолгическая деривация). */
        x = $('#etymology_set-group').detach();
        y = $('.field-derivation_entry').parent('fieldset');
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
         * значения поля языка конкретной этимологии.
         *
         * Для всех языков кроме того отображаем поле text, но скрываем
         * unitext. Для греческого поле unitext отображаем всегда, а text
         * только, если там что-нибудь есть. */
        lang2cssclass = {
            'a': 'grec',
            'b': 'hebrew',
            'c': 'akkadian',
            'd': 'aramaic',
            'e': 'armenian',
            'f': 'georgian',
            'g': 'coptic',
            'h': 'latin',
            'i': 'syriac'
        }
        langclsss1 = 'grec hebrew akkadian aramaic armenian georgian coptic latin syriac'
        langclsss2 = 'grec-translit hebrew-translit akkadian-translit aramaic-translit armenian-translit georgian-translit coptic-translit latin-translit syriac-translit'

        function changeLangCSSClass(x, v){
            if (v){
                var c1 = lang2cssclass[v];
                var c2 = c1 + '-translit';
                x.nextAll('.field-text').find('input[id$="-text"]')
                    .removeClass( langclsss1 )
                    .addClass( c1 );
                x.nextAll('.field-translit').find('input[id$="-translit"]')
                    .removeClass( langclsss2 )
                    .addClass( c2 );
            }
        }
        function textAndUnitext(x, v) {
            var isGreek,
                text = x.nextAll('.field-text').find('input[id$="-text"]'),
                unitext = x.nextAll('.field-unitext').find('input[id$="-unitext"]'),
                show = function(field) { field.parent().removeClass('hidden'); },
                hide = function(field) { field.parent().addClass('hidden'); };
            if (v){
                isGreek = (lang2cssclass[v] == 'grec');
                if( isGreek ) {
                    show(unitext);
                    if( text.val() ) { show(text); } else { hide(text); }
                } else {
                    show(text);
                    hide(unitext);
                }
            } else {
                show(text);
                show(unitext);
            }
        }

        $('#etymology_set-group .form-row.field-language').each(function(){
            var x = $(this);
            var v = x.find('select').val();
            changeLangCSSClass(x, v);
            textAndUnitext(x, v);
        });
        $('#etymology_set-group .form-row.field-language select').change(function(){
            var i = $(this);
            var x = i.closest('.form-row.field-language');
            var v = i.val();
            changeLangCSSClass(x, v);
            textAndUnitext(x, v);
        });


        /* Скрываем и отображаем поля в зависимости от выбранной части речи. */
        partsOfSpeech = {
            "a": 'noun', // отображение id в справочнике значений категорий
                         // на названия категорий на английском.
            "b": 'adjective',
            "c": 'pronoun',
            "d": 'verb',
            "e": 'participle',
            "f": 'adverb',
            "g": 'conjunction',
            "h": 'preposition',
            "i": 'particle',
            "j": 'interjection'
        };

        var v = $('select#id_part_of_speech').val();
        if (v && v !== '.') {
            $('.' + partsOfSpeech[v]).show();
        }

        $('select#id_part_of_speech').change(function(){
            var v = $(this).val();
            $('.noun, .verb, .adjective, .adverb, .preposition, .pronoun, .conjunction, .particle, .interjection, .participle').hide();
            if (v && v !== '.') {
                $('.' + partsOfSpeech[v]).show();
            }
        });


        /* Скрываем или отображаем поля в зависимости от
         * изменяемости/неизменяемости существительного или прилагательного. */
        function checkUninflected() {
            if ( $('#id_uninflected').is(':checked') ) {
                $('.field-genitive').hide();
                $('.field-tantum').hide();
                $('.field-short_form').hide();
            } else {
                $('.field-genitive').show();
                $('.field-tantum').show();
                $('.field-short_form').show();
            }
        }

        checkUninflected();
        $('#id_uninflected').click(checkUninflected);

        /* Скрываем или отображаем поля для выбранного типа имени собственного.
         * */
        onyms = {
            "a": 'canonical_name', // имя
            "b": '',               // топоним
            "c": 'nom_sg',         // народ
            "d": ''                // другое
        }

        v = $('select#id_onym').val();
        if (v && v !== '.') {
            $('.field-' + onyms[v]).show();
        }

        $('select#id_onym').change(function(){
            var v = $(this).val();
            $('.field-canonical_name, .field-nom_sg').hide();
            if (v && v !== '.') {
                $('.field-' + onyms[v]).show();
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

        /* Вся клетка с галочкой "фразеологизм" должна реагировать на щелчок
         * мыши, а не только сама галочка */
        $('input[id$="-phraseological"]').each(function(){
            var x = $(this);
            x.parent().click(function(){
                x.prop('checked', !x.prop('checked'));
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


            var x = $('#id_orthographic_variants-0-idem');
            x.keyup(function(){
                var x = $('#id_civil_equivalent');
                var v = $(this).val();
                x.val(antconc_civilrus_word(v));
                if (v && v.indexOf('*') > -1){
                    x.addClass('myerr');
                } else {
                    x.removeClass('myerr');
                }
            });
            x.focus();

        }
        setTimeout(returnToPostponed, 1000);
    });
})(django.jQuery);

