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
        .rememberInitial(vM.valuesToInitialize.find)
        .rememberDefault('')
        .htmlTextInput('find'),

    author: ko.observable()
        .rememberInitial(vM.valuesToInitialize.author)
        .rememberDefault('all')
        .htmlSelect('author', vM.listsForWidgets.authors),

    sortbase: ko.observable()
        .rememberInitial(vM.valuesToInitialize.sortbase)
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('sortbase', vM.listsForWidgets.sortbase),

    sortdir: ko.observable()
        .rememberInitial(vM.valuesToInitialize.sortdir)
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('sortdir', vM.listsForWidgets.sortdir),

    status: ko.observable()
        .rememberInitial(vM.valuesToInitialize.status)
        .rememberDefault('all')
        .htmlSelect('status', vM.listsForWidgets.statuses),

    pos: ko.observable()
        .rememberInitial(vM.valuesToInitialize.pos)
        .rememberDefault('all')
        .htmlSelect('pos', vM.listsForWidgets.pos),

    uninflected: ko.observable()
        .rememberInitial(vM.valuesToInitialize.uninflected)
        .rememberDefault(false)
        .htmlCheckbox('uninflected'),

    gender: ko.observable()
        .rememberInitial(vM.valuesToInitialize.gender)
        .rememberDefault('all')
        .htmlSelect('gender', vM.listsForWidgets.gender),

    tantum: ko.observable()
        .rememberInitial(vM.valuesToInitialize.tantum)
        .rememberDefault('all')
        .htmlSelect('tantum', vM.listsForWidgets.tantum),

    possessive: ko.observable()
        .rememberInitial(vM.valuesToInitialize.possessive)
        .rememberDefault('all')
        .htmlSelect('possessive', vM.listsForWidgets.possessive),

    onym: ko.observable()
        .rememberInitial(vM.valuesToInitialize.onym)
        .rememberDefault('all')
        .htmlSelect('onym', vM.listsForWidgets.onym),

    canonical_name: ko.observable()
        .rememberInitial(vM.valuesToInitialize.canonical_name)
        .rememberDefault('all')
        .htmlSelect('canonical_name', vM.listsForWidgets.canonical_name),

    etymology: ko.observable()
        .rememberInitial(vM.valuesToInitialize.etymology)
        .rememberDefault(false)
        .htmlCheckbox('etymology'),

    collocations: ko.observable()
        .rememberInitial(vM.valuesToInitialize.collocations)
        .rememberDefault(false)
        .htmlCheckbox('collocations'),

    meaningcontexts: ko.observable()
        .rememberInitial(vM.valuesToInitialize.meaningcontexts)
        .rememberDefault(false)
        .htmlCheckbox('meaningcontexts'),

    additional_info: ko.observable()
        .rememberInitial(vM.valuesToInitialize.additional_info)
        .rememberDefault(false)
        .htmlCheckbox('additional_info'),

    homonym: ko.observable()
        .rememberInitial(vM.valuesToInitialize.homonym)
        .rememberDefault(false)
        .htmlCheckbox('homonym'),

    duplicate: ko.observable()
        .rememberInitial(vM.valuesToInitialize.duplicate)
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
