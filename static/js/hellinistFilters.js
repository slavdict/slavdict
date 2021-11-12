(function () {

    var valuesToInitialize = vM.valuesToInitialize.examplesFilters,
        listsForWidgets = vM.listsForWidgets.examplesFilters,
        filterFieldsList = [
            'hwAddress',
            'hwAllExamples',
            'hwAuthor',
            'hwExample',
            'hwExamplesIds',
            'hwPrfx',
            'hwSortbase',
            'hwSortdir',
            'hwStatus',
            'hwVolume'
        ];

    vM.filters = {
        examples: ko.utils.arrayMap(vM.jsonExamples, function(ex) {
            return new Example(ex); }),

        formSubmit: function(){
            var qs = new URLSearchParams(window.location.search);
            filterFieldsList.forEach(field => {
                if (vM.filters[field].hasDefaultValue())
                    qs.delete(field);
                else
                    qs.set(field, vM.filters[field]());
            });
            window.location.search = qs.toString();
        },

        hwAuthor: ko.observable()
            .rememberInitial(valuesToInitialize.hwAuthor)
            .rememberDefault('all')
            .htmlSelect('hwAuthor', listsForWidgets.authors, 'all'),

        hwAddress: ko.observable()
            .rememberInitial(valuesToInitialize.hwAddress)
            .rememberDefault('')
            .htmlTextValue('hwAddress'),

        hwPrfx: ko.observable()
            .rememberInitial(valuesToInitialize.hwPrfx)
            .rememberDefault('')
            .htmlTextValue('hwPrfx'),

        hwVolume: ko.observable()
            .rememberInitial(valuesToInitialize.hwVolume)
            .rememberDefault('all')
            .htmlSelect('hwVolume', listsForWidgets.volumes, 'all'),

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
            .rememberDefault('addr')
            .htmlSelect('hwSortbase', listsForWidgets.sortbase,
                        valuesToInitialize.hwSortbase),

        hwSortdir: ko.observable()
            .rememberInitial(valuesToInitialize.hwSortdir)
            .rememberDefault('-')
            .htmlSelect('hwSortdir', listsForWidgets.sortdir,
                        valuesToInitialize.hwSortdir),

        hwAllExamples: ko.observable()
            .rememberInitial(valuesToInitialize.hwAllExamples)
            .rememberDefault(false)
            .htmlCheckbox('hwAllExamples'),

        hwStatus: ko.observable()
            .rememberInitial(valuesToInitialize.hwStatus)
            .rememberDefault('all')
            .htmlSelect('hwStatus', listsForWidgets.statuses, 'all')

    };
    vM.filters.chgg = ko.computed(function () {
        var x = vM.filters,
            y = x.hwAuthor() + '|' +
                x.hwAddress() + '|' +
                x.hwPrfx() + '|' +
                x.hwVolume() + '|' +
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
