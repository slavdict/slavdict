(function () {

    vM.meta = {
        initials: [],
        defaults: []
    };

    if (!vM.filters) vM.filters = {};

    var valuesToInitialize = vM.valuesToInitialize.entryFilters,
        listsForWidgets = vM.listsForWidgets.entryFilters,
        f = vM.filters;

    f.formSubmit = function () { $('.headerForm').submit(); };
    f.isOperated = ko.observable(false)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } });
    f.showResetAll = ko.observable(false)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } });
    f.closeFilters = function () {
        this.isOperated(false);
        this.getInitialState();
    };

    f.per_se = ko.observable()
            .rememberInitial(valuesToInitialize.per_se)
            .rememberDefault(false)
            .htmlCheckbox('per_se');

    f.find = ko.observable()
            .rememberInitial(valuesToInitialize.find)
            .rememberDefault('')
            .htmlTextInput('find');

    f.author = ko.observable()
            .rememberInitial(valuesToInitialize.author)
            .rememberDefault('all')
            .htmlSelect('author', listsForWidgets.authors);

    f.sortbase = ko.observable(valuesToInitialize.sortbase)
            // Не определяем здесь дефолтного значение ``.rememberDefault``,
            // и не запоминаем начальное значение ``.rememberInitial``,
            // чтобы изменение значений не влияло на отображение информационной
            // панели фильтров.
            .htmlSelect('sortbase', listsForWidgets.sortbase);

    f.sortdir = ko.observable(valuesToInitialize.sortdir)
            // Не определяем здесь дефолтного значение ``.rememberDefault``,
            // и не запоминаем начальное значение ``.rememberInitial``,
            // чтобы изменение значений не влияло на отображение информационной
            // панели фильтров.
            .htmlSelect('sortdir', listsForWidgets.sortdir);

    f.status = ko.observable()
            .rememberInitial(valuesToInitialize.status)
            .rememberDefault('all')
            .htmlSelect('status', listsForWidgets.statuses);

    f.pos = ko.observable()
            .rememberInitial(valuesToInitialize.pos)
            .rememberDefault('all')
            .htmlSelect('pos', listsForWidgets.pos);

    f.uninflected = ko.observable()
            .rememberInitial(valuesToInitialize.uninflected)
            .rememberDefault(false)
            .htmlCheckbox('uninflected');

    f.gender = ko.observable()
            .rememberInitial(valuesToInitialize.gender)
            .rememberDefault('all')
            .htmlSelect('gender', listsForWidgets.gender);

    f.tantum = ko.observable()
            .rememberInitial(valuesToInitialize.tantum)
            .rememberDefault('all')
            .htmlSelect('tantum', listsForWidgets.tantum);

    f.possessive = ko.observable()
            .rememberInitial(valuesToInitialize.possessive)
            .rememberDefault('all')
            .htmlSelect('possessive', listsForWidgets.possessive);

    f.onym = ko.observable()
            .rememberInitial(valuesToInitialize.onym)
            .rememberDefault('all')
            .htmlSelect('onym', listsForWidgets.onym);

    f.canonical_name = ko.observable()
            .rememberInitial(valuesToInitialize.canonical_name)
            .rememberDefault('all')
            .htmlSelect('canonical_name', listsForWidgets.canonical_name);

    f.etymology = ko.observable()
            .rememberInitial(valuesToInitialize.etymology)
            .rememberDefault(false)
            .htmlCheckbox('etymology');

    f.etymology_sans = ko.observable()
            .rememberInitial(valuesToInitialize.etymology_sans)
            .rememberDefault(false)
            .htmlCheckbox('etymology_sans');

    f.variants = ko.observable()
            .rememberInitial(valuesToInitialize.variants)
            .rememberDefault(false)
            .htmlCheckbox('variants');

    f.collocations = ko.observable()
            .rememberInitial(valuesToInitialize.collocations)
            .rememberDefault(false)
            .htmlCheckbox('collocations');

    f.meaningcontexts = ko.observable()
            .rememberInitial(valuesToInitialize.meaningcontexts)
            .rememberDefault(false)
            .htmlCheckbox('meaningcontexts');

    f.additional_info = ko.observable()
            .rememberInitial(valuesToInitialize.additional_info)
            .rememberDefault(false)
            .htmlCheckbox('additional_info');

    f.homonym = ko.observable()
            .rememberInitial(valuesToInitialize.homonym)
            .rememberDefault(false)
            .htmlCheckbox('homonym');

    f.duplicate = ko.observable()
            .rememberInitial(valuesToInitialize.duplicate)
            .rememberDefault(false)
            .htmlCheckbox('duplicate');

    f.sort = ko.computed({
        read: function(){
            return this.sortdir() + this.sortbase();
        },
        write: function(value){
            this.sortdir(value[0]);
            this.sortbase(value.slice(1));
        },
        owner: f
    });

    f.doSort = function(sort){
        this.sort(sort);
        this.formSubmit();
    };

    f.isOperated.toggle = function(){ this(!this()); }.bind(f.isOperated)

    f.notDefaultState = ko.computed(function(){
        var defaults = vM.meta.defaults;
        for(var i = 0, j = defaults.length; i < j; i++){
            if (!defaults[i].hasDefaultValue()) return true;
        }
        return false;
    }, f).extend(
        { rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } });

    f.notInitialState = ko.computed(function(){
        var initials = vM.meta.initials;
        for(var i = 0, j = initials.length; i < j; i++){
            if (!initials[i].hasInitialValue()) return true;
        }
        return false;
    }, f).extend(
        { rateLimit: { method: 'notifyWhenChangesStop', delay: 400 } });

    f.getDefaultState = function(){
        var defaults = vM.meta.defaults;
        for(var i = 0, j = defaults.length; i < j; i++){
            defaults[i].getDefaultValue();
        }
        f.showResetAll(false);
    };

    f.getInitialState = function(){
        var initials = vM.meta.initials;
        for(var i = 0, j = initials.length; i < j; i++){
            initials[i].getInitialValue();
        }
    };

    f.shouldShowStatusBar = ko.computed(function(){
        return (
            !this.notDefaultState() && this.notInitialState() ||
            this.isOperated() || this.notDefaultState()
        );
    }, f).extend({rateLimit: 500}); // ::jsStatusbarRateLimit

    f.shouldShowFiltersButtons = ko.computed(
        f.notInitialState
    ).extend({rateLimit: 500}); /* NOTE: Наличие ``rateLimit`` здесь
                    обязательно, чтобы интерфейс себя вел хорошо в ситуации,
                    когда автор нажимает кнопку "мои статьи" ##ui_myentries.
                    Через полсекунды после нажатия (см. ##jsStatusbarRateLimit)
                    появится статусная строка ##ui_filters_statusbar, если она
                    была скрыта. В ней будет указано, что выбран фильтр
                    статьи такого-то автора. Кнопка "применить изменения"
                    ##ui_filters_apply без ``rateLimit`` будет появляться
                    раньше статусной строки, что в пользовательском интерфейсе
                    выглядит достаточно странно. */
})();

$('#id_find')
    .attr('data-bind', 'textInput: find')
    .attr('autocomplete', 'off')
    .attr('spellcheck', 'false');

function showFilterButtons() {
    $('.f5s--buttons').slideDown();
}
function goInsensitive() {
    $(this)
        .unbind('change', showFilterButtons)
        .unbind('blur', goInsensitive);
}
function goSensitive() {
    $(this)
        .bind('change', showFilterButtons)
        .bind('blur', goInsensitive);
}

$('#id_sortdir').on('focus', goSensitive);
$('#id_sortbase').on('focus', goSensitive);

ko.applyBindings(vM.filters, $('.filters').get(0));
ko.applyBindings(vM.filters, $('#main').get(0));
if ($('#withExamples').length) {
    ko.applyBindings(vM.filters, $('#withExamples').get(0));
}

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
