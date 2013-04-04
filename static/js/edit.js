var mapping = {
        meanings: {
            create: function(options){ return new Meaning(options); }
        },
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
            if (typeof entry === 'undefined') {
                throw new Error('Конструктору Orthvar требуется передать ' +
                                'объект Entry, если в options нет ' +
                                'достаточного количества данных.');
            }
            this.entry_id = entry.id;
            this.id = 'orthvar' + Orthvar.counter;
            this.order(Orthvar.largestOrder + 1);
        }

        Orthvar.counter++;

        if (Orthvar.largestOrder < this.order()) {
            Orthvar.largestOrder = this.order();
        }
    },
    Meaning = function(options, containerType, container, parentMeaning) {
        var data = options.data;
        this.meaning = ko.observable(data && data.meaning || '');
        this.gloss = ko.observable(data && data.gloss || '');
        this.metaphorical = ko.observable(data && data.metaphorical || false);
        this.additional_info = ko.observable(data &&
                                             data.additional_info || '')
        this.substantivus = ko.observable(data && data.substantivus || false);
        this.substantivus_type = ko.observable(data &&
                                               data.substantivus_type || '');
        this.hidden = ko.observable(data && data.hidden || false);

        if (typeof data !== 'undefined') {
            this.entry_container_id = data.entry_container_id || null;
            this.collogroup_container_id = data.collogroup_container_id || null;
            this.parent_meaning_id = data.parent_meaning_id || null;
            this.id = data.id;
            this.order = ko.observable(data.order);
        } else {
            if (typeof container === 'undefined' ||
                typeof containerType === 'undefined') {

                throw new Error('Конструктору Meaning требуется передать ' +
                                'объект Entry или Collogroup, указав какой ' +
                                'именно. Это в том случае, если в options ' + 
                                'нет достаточного количества данных.');
            }
            if (containerType === 'entry') {
                this.entry_container_id = container.id;
                this.collogroup_container_id = null;
            }
            if (containerType === 'collogroup') {
                this.entry_container_id = null;
                this.collogroup_container_id = container.id;
            }
            this.parent_meaning_id = parentMeaning.id || null;
            this.id = 'meaning' + Meaning.counter;
            this.order = ko.observable(Meaning.largestOrder + 1);
        }

        Meaning.counter++;

        if (Meaning.largestOrder < this.order()) {
            Meaning.largestOrder = this.order();
        }
    },
    Participle = function(options, entry) {
        this.idem = ko.observable(options.data && options.data.idem || '');
        this.order = ko.observable();
        this.tp = ko.observable(options.data && options.data.tp || '');

        if (typeof options.data !== 'undefined') {
            this.entry_id = options.data.entry_id;
            this.id = options.data.id;
            this.order(options.data.order);
        } else {
            if (typeof entry === 'undefined') {
                throw new Error('Конструктору Participle требуется передать ' +
                                'объект Entry, если в options нет ' +
                                'достаточного количества данных.');
            }
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

Meaning.counter = 0;
Meaning.largestOrder = 0;

var placeholderClass = 'sortable-placeholder';
ko.bindingHandlers.sortable.options = {
    appendTo: document.body,
    axis: 'y',
    cursor: 'move',
    opacity: 0.9,
    placeholder: placeholderClass,
    start: function(event, ui){
        var x = $(ui.item),
            y = x.outerHeight();
        x.addClass('being-dragged');
        $('.' + placeholderClass).height(y);
    },
    stop: function(event, ui){
        $(ui.item).removeClass('being-dragged');
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
