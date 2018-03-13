function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

ko.bindingHandlers['visibleActive'] = {
    'update': function (element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());
        var isCurrentlyVisible = !(element.style.display == "none");
        if (value && !isCurrentlyVisible) {
            element.style.display = "";
            element.focus();
        } else if ((!value) && isCurrentlyVisible)
            element.style.display = "none";
    }
};

function GreqForJSON(greq) {
    this.id = greq.id;
    this.unitext = greq.unitext;
    this.initial_form = greq.initial_form;
    this.note = greq.note;
    this.aliud = greq.aliud;
    this.additional_info = greq.additional_info;
    this.for_example_id = greq.for_example_id;
}

function Greq(ex, greq) {

    if (!greq) greq = {};

    this.id = ko.observable(greq.id || '');
    this.unitext = ko.observable(greq.unitext || '');
    this.initial_form = ko.observable(greq.initial_form || '');
    this.aliud = ko.observable(greq.aliud || false);
    this.note = ko.observable(greq.note || '');
    this.additional_info = ko.observable(greq.additional_info || '');
    this.for_example_id = ex.id;

    this.beingSaved = ko.observable(false);

    this.removeMe = function() {
        if (this.id()) {
            this.beingSaved(true);
            var dataToSend = { 'delete': this.id() }
            $.ajax({
                method: 'POST',
                url: vM.urls.jsonGreqDeleteURL,
                data: dataToSend,
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken);
                },
                success: function (data) {
                           if (data.action=='deleted') {
                             ex.greqs.remove(this);
                           }
                         }.bind(this)
            });
        } else {
            ex.greqs.remove(this);
        }
    }.bind(this);

    this.saveMe = function() {
        this.beingSaved(true);
        var dataToSend = { 'greq': ko.toJSON(new GreqForJSON(this)) };
        $.ajax({
            method: 'POST',
            url: vM.urls.jsonGreqSaveURL,
            data: dataToSend,
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (data) {
                       if (data.action=='created') {
                         this.id(data.id);
                       }
                       this.beingSaved(false);
                     }.bind(this)
        });
    }.bind(this);
}

function ExForJSON(ex) {
    this.id = ex.id;
    this.greek_eq_status = ex.status;
    this.additional_info = ex.comment;
    this.address_text = ex.address;
    this.example = ex.example;
    this.audited = ex.audited() || false;
    this.saveAuditTime = ex.saveAuditTime;
}

function Example(ex) {
    var self = this;

    this.id = ex.id;
    this.status = ko.observable(ex.status);
    this.audited = ko.observable(ex.audited);
    this.audited.subscribe(function () { self.saveAuditTime = true; })

    this.address = ko.observable(ex.address);
    this.comment = ko.observable(ex.comment);
    this.commentEditable = ko.observable(false);

    this.leftContext = ko.observable(ex.triplet[0]);
    this.text = ko.observable(ex.triplet[1]);
    this.rightContext = ko.observable(ex.triplet[2]);

    this.antconc = ko.observable(ex.antconc);
    this.antconcVisible = ko.observable(false);

    this.initialExample = ex.example;
    this.example = ko.observable(ex.example);
    this.exampleEditable = ko.observable(false);

    this.greqs = ko.observableArray(
        ko.utils.arrayMap(
            ex.greqs,
            function(greq){
                return new Greq(this, greq);
            }.bind(this)
        )
    );

    this.addGreq = function() {
        this.greqs.push(new Greq(this));
    }.bind(this);

    this.TOGGLE = function(param) {
        return function() {
            var value = param();
            param(!value);
        }
    };

    this.toggleAntconc = this.TOGGLE(this.antconcVisible);
    this.toggleComment = this.TOGGLE(this.commentEditable);
    this.editExample = function () { self.exampleEditable(true); };
    this.saveExample = function () {
        self.exampleEditable(false);
        self.antconc(self.example());
        self.leftContext('');
        self.text(antconc_ucs8(self.example(), false /* is affix */));
        self.rightContext('');
        self.saveMe();
    };
    this.cancelExample = function () {
        self.example(self.initialExample);
    };

    this.timeoutId = null;
    this.beingSaved = ko.observable(false);
    this.saveMe = function () {
        if (this.timeoutId !== null) {
            clearTimeout(this.timeoutId);
        }
        this.timeoutId = setTimeout(this.doSave, 500);
    }.bind(this);
    this.doSave = function () {
        this.beingSaved(true);
        var dataToSend = { 'ex': ko.toJSON(new ExForJSON(this)) };
        $.ajax({
            method: 'POST',
            url: vM.urls.jsonExSaveURL,
            data: dataToSend,
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (data) {
                       this.beingSaved(false);
                     }.bind(this)
        });
    }.bind(this);
}


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
