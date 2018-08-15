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
    this.initial_form_phraseology = greq.initial_form_phraseology;
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
    this.initial_form_phraseology = ko.observable(greq.initial_form_phraseology || '');
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
                           if (data.greek_eq_status != ex.status()) {
                               ex.status(data.greek_eq_status);
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
                       if (data.greek_eq_status != ex.status()) {
                           ex.status(data.greek_eq_status);
                       }
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
    this.exampleBackups = ko.observableArray([]);
    this.howManyBackups = ko.computed(function () {
        var ret,
            backups = self.exampleBackups(),
            example = self.example();
        if (backups.length == 0) {
            ret = 0;
        } else if (backups[backups.length - 1] != example) {
            ret = backups.length;
        } else {
            ret = backups.length - 1;
        }
        return ret;
     });

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
    this.editExample = function () {
        self.exampleEditable(true);
        self.exampleBackups.push(self.example());
        self.backups = self.exampleBackups().slice();
    };
    this.saveExample = function () {
        self.exampleEditable(false);
        self.antconc(self.example());
        self.leftContext('');
        self.text(antconc_ucs8(self.example(), false /* is affix */));
        self.rightContext('');
        self.saveMe();
    };
    this.cancelExample = function () {
        self.exampleEditable(false);
        self.example(self.backups.pop());
        self.exampleBackups(self.backups);
    };
    this.revertExample = function () {
        if (self.exampleBackups().length > self.howManyBackups()) {
            self.exampleBackups.pop();
            self.example(self.exampleBackups.pop());
        } else {
            self.example(self.exampleBackups.pop());
        }
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
    if (vM.jsonExamplesForEntries) {
        var examples = {},
            keys = Object.keys(vM.jsonExamplesForEntries),
            key, examplesGroup, entryExamples, ex;
        for (var k = 0; keys.length > k; k++) {
            key = keys[k];
            entryExamples = [];
            for (var i = 0; vM.jsonExamplesForEntries[key].length > i; i++) {
                examplesGroup = [];
                for (var j = 0; vM.jsonExamplesForEntries[key][i].length > j; j++) {
                    ex = vM.jsonExamplesForEntries[key][i][j];
                    examplesGroup.push(new Example(ex));
                }
                entryExamples.push(examplesGroup);
            }
            examples[key] = entryExamples;
        }
        if (!vM.filters) vM.filters = {};
        vM.filters.examplesForEntries = examples;
    }
})();
