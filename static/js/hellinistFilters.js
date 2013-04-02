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
    this.additional_info = greq.additional_info;
    this.for_example_id = greq.for_example_id;
}

function Greq(ex, greq) {

    if (!greq) greq = {};

    this.id = ko.observable(greq.id || '');
    this.unitext = ko.observable(greq.unitext || '');
    this.initial_form = ko.observable(greq.initial_form || '');
    this.additional_info = ko.observable(greq.additional_info || '');
    this.for_example_id = ex.id;

    this.beingSaved = ko.observable(false);

    this.removeMe = function() {
        if (this.id()) {
            this.beingSaved(true);
            var dataToSend = { 'delete': this.id() }
            $.post(vM.urls.jsonGreqDeleteURL, dataToSend,
                function(data) {
                    if (data.action=='deleted') {
                        ex.greqs.remove(this);
                    }
                }.bind(this)
            );
        } else {
            ex.greqs.remove(this);
        }
    }.bind(this);

    this.saveMe = function() {
        this.beingSaved(true);
        var dataToSend = { 'greq': ko.toJSON(new GreqForJSON(this)) };
        $.post(vM.urls.jsonGreqSaveURL, dataToSend, function(data) {
            if (data.action=='created') {
                this.id(data.id);
            }
            this.beingSaved(false);
        }.bind(this));
    }.bind(this);
}

function ExForJSON(ex) {
    this.id = ex.id;
    this.greek_eq_status = ex.status;
    this.additional_info = ex.comment;
    this.address_text = ex.address;
}

function Example(ex) {

    this.id = ex.id;
    this.status = ko.observable(ex.status);

    this.address = ko.observable(ex.address);
    this.addressEditable = ko.observable(false);

    this.comment = ko.observable(ex.comment);
    this.commentEditable = ko.observable(false);

    this.leftContext = ex.triplet[0];
    this.text = ex.triplet[1];
    this.rightContext = ex.triplet[2];

    this.antconc = ex.antconc;
    this.antconcVisible = ko.observable(false);

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
    this.toggleAddress = this.TOGGLE(this.addressEditable);
    this.toggleComment = this.TOGGLE(this.commentEditable);

    this.beingSaved = ko.observable(false);
    this.saveMe = function() {
        this.beingSaved(true);
        var dataToSend = { 'ex': ko.toJSON(new ExForJSON(this)) };
        $.post(vM.urls.jsonExSaveURL, dataToSend, function(data) {
            this.beingSaved(false);
        }.bind(this));
    }.bind(this);
}




vM.filters = {
    examples: ko.utils.arrayMap(vM.jsonExamples, function(ex) {
        return new Example(ex); }),

    formSubmit: function(){ $('.headerForm').submit(); },

    hwAuthor: ko.observable()
        .rememberInitial(vM.valuesToInitialize.hwAuthor)
        .rememberDefault('all')
        .htmlSelect('hwAuthor', vM.listsForWidgets.authors),

    hwAddress: ko.observable()
        .rememberInitial(vM.valuesToInitialize.hwAddress)
        .rememberDefault('')
        .htmlTextInput('hwAddress'),

    hwPrfx: ko.observable()
        .rememberInitial(vM.valuesToInitialize.hwPrfx)
        .rememberDefault('')
        .htmlTextInput('hwPrfx'),

    hwSortbase: ko.observable()
        .rememberInitial(vM.valuesToInitialize.hwSortbase)
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('hwSortbase', vM.listsForWidgets.sortbase),

    hwSortdir: ko.observable()
        .rememberInitial(vM.valuesToInitialize.hwSortdir)
        // .rememberDefault... Значения по умолчанию
        // на клиенте намеренно не определяем,
        // хотя оно есть на сервере
        .htmlSelect('hwSortdir', vM.listsForWidgets.sortdir),

    hwStatus: ko.observable()
        .rememberInitial(vM.valuesToInitialize.hwStatus)
        .rememberDefault('all')
        .htmlSelect('hwStatus', vM.listsForWidgets.statuses)

};

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

ko.applyBindings(vM.filters);
