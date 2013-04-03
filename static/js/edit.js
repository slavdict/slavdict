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

    Orthvar = function(options, entry) {
        this.idem = ko.observable(options.data && options.data.idem || '');
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

ko.bindingHandlers.wax = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        var value = valueAccessor(),
            cssClasses = allBindingsAccessor().waxCss || 'cslav';
        value.wax = ko.computed(function() {
                var word = value(),
                    isAffix = (word[0] === '-'),
                    dash = isAffix ? '<span>-</span>': '',
                    text = ('<span class="' + cssClasses + '">' +
                            ac2ucs8(isAffix ? word.slice(1) : word, isAffix) +
                            '</span>');
                    return dash + text;
            });
        $(element).html(value.wax());
    },
    update: function(element, valueAccessor) {
        var value = valueAccessor();
        $(element).html(value.wax());
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


uiEntry.headword = ko.computed(function() {
    return dataEntry.orthvars()[0].idem();
});

uiEntry.part_of_speech = ko.computed(function() {
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

// Активация работы вкладок
$('nav.tabs li').click(function(){
    $('nav.tabs li.current').removeClass('current');
    $('section.tabcontent.current').removeClass('current');
    var x = $(this);
    x.addClass('current');
    $(x.find('a').attr('href')).addClass('current');
});
