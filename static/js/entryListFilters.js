vM.meta = {
    initials: [],
    defaults: []
};

vM.filters = {
    formSubmit: vM.hdrSearch.formSubmit,
    isOperated: ko.observable(false).extend({throttle: 400}),
    showResetAll: ko.observable(false).extend({throttle: 400}),
    closeFilters: function(){
            this.isOperated(false);
            this.getInitialState();
        },

    find: ko.observable()
        .rememberInitial('{{ filters.find }}')
        .rememberDefault('')
        .htmlTextInput('find'),

    author: ko.observable()
        .rememberInitial('{{ filters.author }}')
        .rememberDefault('all')
        .htmlSelect('author', {{ viewmodel.authors }}),

    sortbase: ko.observable()
        .rememberInitial('{{ filters.sortbase }}')
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('sortbase', {{ viewmodel.sortbase }}),

    sortdir: ko.observable()
        .rememberInitial('{{ filters.sortdir }}')
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('sortdir', {{ viewmodel.sortdir }}),

    status: ko.observable()
        .rememberInitial('{{ filters.status }}')
        .rememberDefault('all')
        .htmlSelect('status', {{ viewmodel.statuses }}),

    pos: ko.observable()
        .rememberInitial('{{ filters.pos }}')
        .rememberDefault('all')
        .htmlSelect('pos', {{ viewmodel.pos }}),

    uninflected: ko.observable()
        .rememberInitial({{ 'true' if filters.uninflected else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('uninflected'),

    gender: ko.observable()
        .rememberInitial('{{ filters.gender }}')
        .rememberDefault('all')
        .htmlSelect('gender', {{ viewmodel.gender }}),

    tantum: ko.observable()
        .rememberInitial('{{ filters.tantum }}')
        .rememberDefault('all')
        .htmlSelect('tantum', {{ viewmodel.tantum }}),

    possessive: ko.observable()
        .rememberInitial('{{ filters.possessive }}')
        .rememberDefault('all')
        .htmlSelect('possessive', {{ viewmodel.possessive }}),

    onym: ko.observable()
        .rememberInitial('{{ filters.onym }}')
        .rememberDefault('all')
        .htmlSelect('onym', {{ viewmodel.onym }}),

    canonical_name: ko.observable()
        .rememberInitial('{{ filters.canonical_name }}')
        .rememberDefault('all')
        .htmlSelect('canonical_name', {{ viewmodel.canonical_name }}),

    etymology: ko.observable()
        .rememberInitial({{ 'true' if filters.etymology else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('etymology'),

    collocations: ko.observable()
        .rememberInitial({{ 'true' if filters.collocations else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('collocations'),

    meaningcontexts: ko.observable()
        .rememberInitial({{ 'true' if filters.meaningcontexts else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('meaningcontexts'),

    additional_info: ko.observable()
        .rememberInitial({{ 'true' if filters.additional_info else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('additional_info'),

    homonym: ko.observable()
        .rememberInitial({{ 'true' if filters.homonym else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('homonym'),

    duplicate: ko.observable()
        .rememberInitial({{ 'true' if filters.duplicate else 'false' }})
        .rememberDefault(false)
        .htmlCheckbox('duplicate')
};

vM.filters.sort = ko.computed({
    read: function(){
        return this.sortdir() + this.sortbase();
    },
    write: function(value){
        if (value.charAt(0) === '-') {
            this.sortdir('-');
            this.sortbase(value.slice(1));
        } else {
            this.sortdir('');
            this.sortbase(value);
        }
    },
    owner: vM.filters
});

vM.filters.doSort = function(sort){
    this.sort(sort);
    this.formSubmit();
};

vM.filters.isOperated.toggle = function(){ this(!this()); }.bind(vM.filters.isOperated)

vM.filters.notDefaultState = ko.computed(function(){
    var defaults = vM.meta.defaults;
    for(var i = 0, j = defaults.length; i < j; i++){
        if (!defaults[i].hasDefaultValue()) return true;
    }
    return false;
}, vM.filters).extend({throttle: 400});

vM.filters.notInitialState = ko.computed(function(){
    var initials = vM.meta.initials;
    for(var i = 0, j = initials.length; i < j; i++){
        if (!initials[i].hasInitialValue()) return true;
    }
    return false;
}, vM.filters).extend({throttle: 400});

vM.filters.getDefaultState = function(){
    var defaults = vM.meta.defaults;
    for(var i = 0, j = defaults.length; i < j; i++){
        defaults[i].getDefaultValue();
    }
    vM.filters.showResetAll(false);
};

vM.filters.getInitialState = function(){
    var initials = vM.meta.initials;
    for(var i = 0, j = initials.length; i < j; i++){
        initials[i].getInitialValue();
    }
};

vM.filters.shouldShowStatusBar = ko.computed(function(){
    return (
        !this.notDefaultState() && this.notInitialState() ||
        this.isOperated() || this.notDefaultState()
    );
}, vM.filters).extend({throttle: 500}); // ::js_statusbar_throttle

vM.filters.shouldShowFiltersButtons = ko.computed(
    vM.filters.notInitialState
).extend({throttle: 500}); /* NOTE: Наличие ``throttle`` здесь обязательно,
                              чтобы интерфейс себя вел хорошо в ситуации,
                когда автор нажимает кнопку "мои статьи" ##ui_myentries.
                Через полсекунды после нажатия (см. ##js_statusbar_throttle)
                появится статусная строка ##ui_filters_statusbar, если она
                была скрыта. В ней будет указано, что выбран фильтр статьи
                такого-то автора. Кнопка "применить изменения"
                ##ui_filters_apply без ``throttle`` будет появляться раньше
                статусной строки, что в пользовательском интерфейсе
                выглядит достаточно странно.  */

$('#id_find')
    .attr('data-bind', 'value: find,' +
        'valueUpdate: "afterkeydown"')
    .attr('autocomplete', 'off')
    .attr('spellcheck', 'false');

ko.applyBindings(vM.filters, $('.filters').get(0));
ko.applyBindings(vM.filters, $('#main').get(0));

$('tr').mouseover(function(){
    $(this).addClass('hover');
}).mouseout(function(){
    $(this).removeClass('hover');
});

$('.icon').mouseover(function(){
    $(this).next('.hint-container').show();
}).mouseout(function(){
    $(this).next('.hint-container').hide();
});
