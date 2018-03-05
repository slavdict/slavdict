(function () {

vM.meta = {
    initials: [],
    defaults: []
};

var valuesToInitialize = vM.valuesToInitialize.entryFilters,
    listsForWidgets = vM.listsForWidgets.entryFilters;

vM.filters = {
    formSubmit: vM.hdrSearch && vM.hdrSearch.formSubmit || function () {
            $('.headerForm').submit();
        },
    isOperated: ko.observable(false)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } }),
    showResetAll: ko.observable(false)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } }),
    closeFilters: function(){
            this.isOperated(false);
            this.getInitialState();
        },

    per_se: ko.observable()
        .rememberInitial(valuesToInitialize.per_se)
        .rememberDefault(false)
        .htmlCheckbox('per_se'),

    find: ko.observable()
        .rememberInitial(valuesToInitialize.find)
        .rememberDefault('')
        .htmlTextInput('find'),

    author: ko.observable()
        .rememberInitial(valuesToInitialize.author)
        .rememberDefault('all')
        .htmlSelect('author', listsForWidgets.authors),

    sortbase: ko.observable()
        .rememberInitial(valuesToInitialize.sortbase)
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('sortbase', listsForWidgets.sortbase),

    sortdir: ko.observable()
        .rememberInitial(valuesToInitialize.sortdir)
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('sortdir', listsForWidgets.sortdir),

    status: ko.observable()
        .rememberInitial(valuesToInitialize.status)
        .rememberDefault('all')
        .htmlSelect('status', listsForWidgets.statuses),

    pos: ko.observable()
        .rememberInitial(valuesToInitialize.pos)
        .rememberDefault('all')
        .htmlSelect('pos', listsForWidgets.pos),

    uninflected: ko.observable()
        .rememberInitial(valuesToInitialize.uninflected)
        .rememberDefault(false)
        .htmlCheckbox('uninflected'),

    gender: ko.observable()
        .rememberInitial(valuesToInitialize.gender)
        .rememberDefault('all')
        .htmlSelect('gender', listsForWidgets.gender),

    tantum: ko.observable()
        .rememberInitial(valuesToInitialize.tantum)
        .rememberDefault('all')
        .htmlSelect('tantum', listsForWidgets.tantum),

    possessive: ko.observable()
        .rememberInitial(valuesToInitialize.possessive)
        .rememberDefault('all')
        .htmlSelect('possessive', listsForWidgets.possessive),

    onym: ko.observable()
        .rememberInitial(valuesToInitialize.onym)
        .rememberDefault('all')
        .htmlSelect('onym', listsForWidgets.onym),

    canonical_name: ko.observable()
        .rememberInitial(valuesToInitialize.canonical_name)
        .rememberDefault('all')
        .htmlSelect('canonical_name', listsForWidgets.canonical_name),

    etymology: ko.observable()
        .rememberInitial(valuesToInitialize.etymology)
        .rememberDefault(false)
        .htmlCheckbox('etymology'),

    variants: ko.observable()
        .rememberInitial(valuesToInitialize.variants)
        .rememberDefault(false)
        .htmlCheckbox('variants'),

    collocations: ko.observable()
        .rememberInitial(valuesToInitialize.collocations)
        .rememberDefault(false)
        .htmlCheckbox('collocations'),

    meaningcontexts: ko.observable()
        .rememberInitial(valuesToInitialize.meaningcontexts)
        .rememberDefault(false)
        .htmlCheckbox('meaningcontexts'),

    additional_info: ko.observable()
        .rememberInitial(valuesToInitialize.additional_info)
        .rememberDefault(false)
        .htmlCheckbox('additional_info'),

    homonym: ko.observable()
        .rememberInitial(valuesToInitialize.homonym)
        .rememberDefault(false)
        .htmlCheckbox('homonym'),

    duplicate: ko.observable()
        .rememberInitial(valuesToInitialize.duplicate)
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
}, vM.filters).extend(
    { rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } });

vM.filters.notInitialState = ko.computed(function(){
    var initials = vM.meta.initials;
    for(var i = 0, j = initials.length; i < j; i++){
        if (!initials[i].hasInitialValue()) return true;
    }
    return false;
}, vM.filters).extend(
    { rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } });

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
}, vM.filters).extend({rateLimit: 500}); // ::js_statusbar_rateLimit

vM.filters.shouldShowFiltersButtons = ko.computed(
    vM.filters.notInitialState
).extend({rateLimit: 500}); /* NOTE: Наличие ``rateLimit`` здесь обязательно,
                              чтобы интерфейс себя вел хорошо в ситуации,
                когда автор нажимает кнопку "мои статьи" ##ui_myentries.
                Через полсекунды после нажатия (см. ##js_statusbar_rateLimit)
                появится статусная строка ##ui_filters_statusbar, если она
                была скрыта. В ней будет указано, что выбран фильтр статьи
                такого-то автора. Кнопка "применить изменения"
                ##ui_filters_apply без ``rateLimit`` будет появляться раньше
                статусной строки, что в пользовательском интерфейсе
                выглядит достаточно странно.  */

})();

$('#id_find')
    .attr('data-bind', 'textInput: find')
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
