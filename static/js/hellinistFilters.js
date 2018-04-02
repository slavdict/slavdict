(function () {

    var valuesToInitialize = vM.valuesToInitialize.examplesFilters,
        listsForWidgets = vM.listsForWidgets.examplesFilters;

    vM.filters = {
        examples: ko.utils.arrayMap(vM.jsonExamples, function(ex) {
            return new Example(ex); }),

        formSubmit: function(){ $('.headerForm').submit(); },

        hwAuthor: ko.observable()
            .rememberInitial(valuesToInitialize.hwAuthor)
            .rememberDefault('all')
            .htmlSelect('hwAuthor', listsForWidgets.authors),

        hwAddress: ko.observable()
            .rememberInitial(valuesToInitialize.hwAddress)
            .rememberDefault('')
            .htmlTextValue('hwAddress'),

        hwPrfx: ko.observable()
            .rememberInitial(valuesToInitialize.hwPrfx)
            .rememberDefault('')
            .htmlTextValue('hwPrfx'),

        hwExample: ko.observable()
            .rememberInitial(valuesToInitialize.hwExample)
            .rememberDefault('')
            .htmlTextValue('hwExample'),

        hwExamplesIds: ko.observable()
            .rememberInitial(valuesToInitialize.hwExamplesIds)
            .rememberDefault('')
            .htmlTextValue('hwExamplesIds'),

        hwSortbase: ko.observable()
            .rememberInitial(valuesToInitialize.hwSortbase)
            // .rememberDefault... Значения по умолчанию
            // на клиенте намеренно не определяем,
            // хотя оно есть на сервере
            .htmlSelect('hwSortbase', listsForWidgets.sortbase),

        hwSortdir: ko.observable()
            .rememberInitial(valuesToInitialize.hwSortdir)
            // .rememberDefault... Значения по умолчанию
            // на клиенте намеренно не определяем,
            // хотя оно есть на сервере
            .htmlSelect('hwSortdir', listsForWidgets.sortdir),

        hwAllExamples: ko.observable()
            .rememberInitial(valuesToInitialize.hwAllExamples)
            .rememberDefault(false)
            .htmlCheckbox('hwAllExamples'),

        hwStatus: ko.observable()
            .rememberInitial(valuesToInitialize.hwStatus)
            .rememberDefault('all')
            .htmlSelect('hwStatus', listsForWidgets.statuses)

    };
    vM.filters.chgg = ko.computed(function () {
        var x = vM.filters,
            y = x.hwAuthor() + '|' +
                x.hwAddress() + '|' +
                x.hwPrfx() + '|' +
                x.hwExample() + '|' +
                x.hwExamplesIds() + '|' +
                x.hwSortbase() + '|' +
                x.hwSortdir() + '|' +
                x.hwAllExamples() + '|' +
                x.hwStatus();
        return y;
    }).extend({rateLimit: 500});
    vM.filters.chgg.subscribe(vM.filters.formSubmit);

    vM.filters.notDefaultState = ko.computed(function(){
        var defaults = vM.meta.defaults;
        for(var i = 0, j = defaults.length; i < j; i++){
            if (!defaults[i].hasDefaultValue()) return true;
        }
        return false;
    }, vM.filters);

    vM.filters.notInitialState = ko.computed(function(){
        var initials = vM.meta.initials;
        for(var i = 0, j = initials.length; i < j; i++){
            if (!initials[i].hasInitialValue()) return true;
        }
        return false;
    }, vM.filters);

    vM.filters.getDefaultState = function(){
        var defaults = vM.meta.defaults;
        for(var i = 0, j = defaults.length; i < j; i++){
            defaults[i].getDefaultValue();
        }
    };

    vM.filters.getInitialState = function(){
        var initials = vM.meta.initials;
        for(var i = 0, j = initials.length; i < j; i++){
            initials[i].getInitialValue();
        }
    };

})();

ko.applyBindings(vM.filters);
