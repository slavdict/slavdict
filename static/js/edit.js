var mapping = {
        orthvars: {
            create: function(options){ return new Orthvar(options); }
        },
        participles: {
            create: function(options){ return new Participle(options); }
        }
    },

    ac2ucs8 = antconc_ucs8,
    ac2cvlr = antconc_civilrus_word,

    wax = function wax(field) {
        var field = this(),
            isAffix = (field[0] === '-');
        return ac2ucs8(isAffix? field.slice(1):field,
                       isAffix? true:false);
    },

    Orthvar = function(options, entry) {
        this.idem = ko.observable(options.data && options.data.idem || '');
        this.idem_ucs = ko.computed(wax, this.idem);
        this.order = ko.observable();

        if (typeof options.data !== 'undefined') {
            this.entry_id = options.data.entry_id;
            this.id = options.data.id;
            this.order(options.data.order);
        } else {
            this.entry_id = entry.id;
            this.id = 'orthvar' + Orthvar.counter;
            this.order(Orthvar.largestOrder + 1);
        }

        Orthvar.counter++;

        if (Orthvar.largestOrder < this.order()) {
            Orthvar.largestOrder = this.order();
        }
    },
    Meaning = function(options) {},
    Participle = function(options, entry) {
        this.idem = ko.observable(options.data && options.data.idem || '');
        this.idem_ucs = ko.computed(wax, this.idem);
        this.order = ko.observable();
        this.tp = ko.observable(options.data && options.data.tp || '');

        if (typeof options.data !== 'undefined') {
            this.entry_id = options.data.entry_id;
            this.id = options.data.id;
            this.order(options.data.order);
        } else {
            this.entry_id = entry.id;
            this.id = 'participle' + Participle.counter;
            this.order(Participle.largestOrder + 1);
        }

        Participle.counter++;

        if (Participle.largestOrder < this.order()) {
            Participle.largestOrder = this.order();
        }
    };

Orthvar.counter = 0;
Orthvar.largestOrder = 0;

Participle.counter = 0;
Participle.largestOrder = 0;

ko.mapping.defaultOptions().ignore.splice(0, 0, 'idem_ucs');

var placeholderClass = 'sortable-placeholder';
ko.bindingHandlers.sortable.options = {
    axis: 'y',
    cursor: 'move',
    cursorAt: { left: 50, bottom: 0 },
    forceHelperSize: true,
    forcePlaceholderSize: true,
    helper: 'clone',
    opacity: 0.7,
    placeholder: placeholderClass,
    start: function(event, ui){
        var y = ui.helper.outerHeight();
        $('.' + placeholderClass).height(y);
    },
    tolerance: 'pointer'
};

ko.bindingHandlers.sortable.afterMove = function(arg) {
    var i, j, arr = arg.targetParent();
    for (i=0, j=arr.length; i<j; i++) {
        arr[i].order(i);
    }
};



vM.entryEdit = {
    data: ko.mapping.fromJS(vM.dataToInitialize.entry, mapping),
    ui: {
        entry: {},
        choices: vM.dataToInitialize.choices,
        labels: vM.dataToInitialize.labels,
        slugs: vM.dataToInitialize.slugs
    }
};

var viewModel = vM.entryEdit,
    dataModel = viewModel.data,
    uiModel = viewModel.ui,
    dataEntry = dataModel.entry,
    uiEntry = uiModel.entry;


uiEntry.genitive = ko.computed(wax, dataEntry.genitive);
uiEntry.headword = ko.computed(wax, dataEntry.orthvars()[0].idem);
uiEntry.nom_sg = ko.computed(wax, dataEntry.nom_sg);
uiEntry.sg1 = ko.computed(wax, dataEntry.sg1);
uiEntry.sg2 = ko.computed(wax, dataEntry.sg2);
uiEntry.short_form = ko.computed(wax, dataEntry.short_form);

uiEntry.part_of_speech = ko.computed(function(){
    var x = this.data.entry.part_of_speech(),
        y = this.ui.labels.part_of_speech;
    if (x in y) {
        return y[x];
    } else {
        console.log('Часть речи "', x, '" не найдена среди ', y);
        return '';
    }
}, viewModel);

uiModel.save = function() {
    $.post('/entries/save/', {data: ko.mapping.toJSON(dataModel, mapping)});
};

uiModel.addMeaing = function() {
    this.meanings.push(new Meaning({}));
}.bind(dataModel);

uiModel.addOrthvar = function() {
    this.orthvars.push(new Orthvar({}, this));
}.bind(dataEntry);

uiModel.destroyOrthvar = function(orthvar) {
    if (typeof orthvar.id === 'number') {
        this.orthvars.destroy(orthvar);
    } else {
        this.orthvars.remove(orthvar);
    }
}.bind(dataEntry);

uiModel.addParticiple = function() {
    this.participles.push(new Participle({}, this));
}.bind(dataEntry);

uiModel.destroyParticiple = function(item) {
    if (typeof item.id === 'number') {
        this.participles.destroy(item);
    } else {
        this.participles.remove(item);
    }
}.bind(dataEntry);

ko.applyBindings(viewModel, $('#main').get(0));

$('nav.tabs li').click(function(){
    $('nav.tabs li.current').removeClass('current');
    $('section.tabcontent.current').removeClass('current');
    var x = $(this);
    x.addClass('current');
    $(x.find('a').attr('href')).addClass('current');
});
