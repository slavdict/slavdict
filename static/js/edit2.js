try {

function single(object, attrname, data, defaultValue, observable) {
    var value = data && data[attrname] || defaultValue;
    observable = observable || ko.observable;
    if (typeof object[attrname] !== 'undefined') {
        if (ko.isSubscribable(object[attrname])) {
            object[attrname](value);
        } else {
            object[attrname] = value;
        }
    } else {
        object[attrname] = observable(value);
    }
}

function newer(parentObj, data, Constructor, args) {
    var allItems = {
            Etymology: parentObj.etymologies,
            Participle: parentObj.participles,
            Orthvar: parentObj.orthvars,
            Collocation: parentObj.collocations,
            Context: parentObj.contexts,
            Greq: parentObj.greqs,
            Example: vM.entryEdit.ui.allExamples,
            Collogroup: vM.entryEdit.ui.allCollogroups,
            Meaning: vM.entryEdit.ui.allMeanings,
            Entry: [vM.entryEdit.data.entry],
        }[Constructor],
        id = ko.utils.unwrapObservable(data.id),
        object = Constructor.idMap && Constructor.idMap[id];

    if (!object) {
        for (var i = allItems.length; i >= 0; i--) {
            id2 = ko.utils.unwrapObservable(allItems[i].id);
            if (id2 === id) {
                object = allItems[i];
                break;
            }
        }
    }

    // args := [<элементы первоначльного массива args...>, data] 
    args = Array.prototype.concat.call(args, data);

    if (!object) {
        args.unshift(null);  // В начало массива аргументов добавляем null.
        // args := [null, <элементы первоначльного массива args...>, data] 
        object = new (Function.prototype.bind.apply(Constructor, args))();
        allItems.push(object);
    } else {
        // Используем функцию конструктор в качестве апдейтера объекта object.
        Constructor.apply(object, args);
    }
}

function multiple(object, attrname,
                  data, Constructor, args, observableArray) {

    var list = data && data[attrname] || [],
        observableArray = observableArray || ko.observableArray;
    if (typeof object[attrname] !== 'undefined'
        && ko.isObservable(object[attrname]) {
            list.forEach(function (listItem) {
                newer(object, listItem /* data */, Constructor, args)
            });
    } else {
        object[attrname] = observableArray();
        multiple(object, attrname, data, Constructor, args, observableArray);
    }
}

function nonObservable(value) { return value; }

var ac2ucs8 = antconc_ucs8,
    ac2cvlr = antconc_civilrus_word,

    Etymology,
    Participle,
    Orthvar,
    Collocation,
    Context,
    Greq,
    Example,
    Collogroup,
    Meaning,
    Entry;


Etymology = function (entry, collocation, etymonTo, data) {
    single(this, 'additional_info', data, '');
    single(this, 'collocation_id', data, collocation.id());
    single(this, 'corrupted', data, false);
    single(this, 'entry_id', data, entry.id());
    single(this, 'etymon_to_id', data, etymonTo.id());
    single(this, 'gloss', data, '');
    single(this, 'id', data, 'etymon' + Etymology.counter);
    single(this, 'language', data, 'a' /* греческий */);
    single(this, 'mark', data, '');
    single(this, 'meaning', data, '');
    single(this, 'order', data, 345);
    single(this, 'questionable', data, false);
    single(this, 'source', data, '');
    single(this, 'text', data, '');
    single(this, 'translit', data, '');
    single(this, 'unclear', data, false);
    single(this, 'unitext', data, '');
    Etymology.counter++;
};
Etymology.counter = 0;
Etymology.idMap = {};


Participle = function (entry, data) {
    single(this, 'idem', data, '');
    single(this, 'tp', data, '');
    single(this, 'order', data, 345);
    single(this, 'entry_id', data, entry.id(), nonObservable);
    single(this, 'id', data, 'participle' + Participle.counter, nonObservable);
    Participle.counter++;
};
Participle.counter = 0;


Orthvar = function (entry, data) {
    single(this, 'idem', data, '');
    single(this, 'order', data, 345);
    single(this, 'entry_id', data, entry.id(), nonObservable);
    single(this, 'id', data, 'orthvar' + Orthvar.counter, nonObservable);
    Orthvar.counter++;
};
Orthvar.counter = 0;


Collocation = function (collogroup, data) {
};
Collocation.counter = 0;


Context = function (meaning, data) {
};
Context.counter = 0;


Greq = function (example, data) {
};
Greq.counter = 0;


Example = function (meaning, entry, collogroup, data) {
    single(this, 'additional_info', data, '');
    single(this, 'address_text', data, '');
    single(this, 'collogroup_id', data, collogroup && collogroup.id || null);
    single(this, 'entry_id', data, entry.id());
    single(this, 'example', data, '');
    single(this, 'greek_eq_status', data, '');
    multiple(this, 'greqs', data, Greq, [this]);
    single(this, 'hidden', data, false);
    single(this, 'id', data, 'example' + Example.counter);
    single(this, 'meaning_id', data, meaning.id);
    single(this, 'order', data, 345);
    Example.counter++;
    var allExamples = vM.entryEdit.ui.allExamples;
    if (allExamples.indexOf(this) === -1) {
        allExamples.push(this);
    }
};
Example.counter = 0;


Collogroup = function (options, containerType, container) {
    var self = this;
    this.collocations = ko.mapping.fromJS(
            { collocations: options.data.collocations || [] },
            mapping)['collocations'];

    if (typeof options.data !== 'undefined') {
        this.base_entry_id = ko.observable(options.data.base_entry_id);
        this.base_meaning_id = ko.observable(options.data.base_meaning_id);
        this.id = options.data.id;
        this.order = ko.observable(options.data.order);
    } else {
        if (typeof container === 'undefined' ||
            typeof containerType === 'undefined') {

            throw new Error('Конструктору Collogroup требуется передать ' +
                            'объект Entry или Meaning, указав какой ' +
                            'именно. Это в том случае, если в options ' +
                            'нет достаточного количества данных.');
        }
        if (containerType === 'entry') {
            this.base_entry_id = ko.observable(container.id);
            this.base_meaning_id = ko.observable(null);
        }
        if (containerType === 'meaning') {
            this.base_entry_id = ko.observable(null);
            this.base_meaning_id = ko.observable(container.id);
        }
        this.id = 'collogroup' + Collogroup.counter;
        this.order = ko.observable(345); // Порядковый номер по умолчанию.
    }

    this.isExpanded = ko.observable(false);
    this.meanings = ko.mapping.fromJS(
            { meanings: options.data.meanings || [] },
            mapping)['meanings'];
    this.meanings.subscribe(function (changedArray) {
        var i = 1;
        ko.utils.arrayForEach(changedArray, function (item) {
            item.parent_meaning_id(null);
            item.entry_container_id(null);
            item.collogroup_container_id(self.id);
            if (! item._destroy) {
                item.order(i);
                i += 1;
            }
        });
    });
    this.meanings.notifySubscribers(this.meanings());

    Collogroup.counter++;
    vM.entryEdit.ui.allCollogroups.push(this);
};
Collogroup.counter = 0;


Meaning = function (options, containerType, container, parentMeaning) {
    var data = options.data,
        self = this;
    this.meaning = ko.observable(data && data.meaning || '');
    this.gloss = ko.observable(data && data.gloss || '');
    this.metaphorical = ko.observable(data && data.metaphorical || false);
    this.additional_info =
            ko.observable(data && data.additional_info || '')
    this.substantivus = ko.observable(data && data.substantivus || false);
    this.substantivus_type =
            ko.observable(data && data.substantivus_type || '');
    this.hidden = ko.observable(data && data.hidden || false);
    this.contexts = ko.mapping.fromJS(
            { contexts: data && data.contexts || []},
            mapping)['contexts'];

    if (typeof data !== 'undefined') {
        this.entry_container_id =
                ko.observable(data.entry_container_id || null);
        this.collogroup_container_id =
                ko.observable(data.collogroup_container_id || null);
        this.parent_meaning_id =
                ko.observable(data.parent_meaning_id || null);
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
            this.entry_container_id = ko.observable(container.id);
            this.collogroup_container_id = ko.observable(null);
        }
        if (containerType === 'collogroup') {
            this.entry_container_id = ko.observable(null);
            this.collogroup_container_id = ko.observable(container.id);
        }
        this.parent_meaning_id = ko.observable(parentMeaning.id || null);
        this.id = 'meaning' + Meaning.counter;
        this.order = ko.observable(345); // Порядковый номер по умолчанию.
    }

    this.isExpanded = ko.observable(false);
    this.childMeanings = ko.observableArray([]);
    this.childMeanings.subscribe(function (changedArray) {
        var i = 1;
        ko.utils.arrayForEach(changedArray, function (item) {
            item.parent_meaning_id(self.id);
            item.entry_container_id(Meaning.idMap[self.id]
                                    .entry_container_id());
            item.collogroup_container_id(Meaning.idMap[self.id]
                                         .collogroup_container_id());
            if (! item._destroy) {
                item.order(i);
                i += 1;
            }
        });
    });
    this.selfExamples = ko.observableArray([]);
    this.selfExamples.subscribe(function (changedArray) {
        var i = 1;
        ko.utils.arrayForEach(changedArray, function (item) {
            item.meaning_id(self.id);
            item.collogroup_id(self.collogroup_container_id());
            if (! item._destroy) {
                item.order(i);
                i += 1;
            }
        });
    });

    this.collogroups = ko.mapping.fromJS(
            { collogroups: data && data.collogroups || [] },
            mapping)['collogroups'];
    this.collogroups.subscribe(function (changedArray) {
        var i = 1;
        ko.utils.arrayForEach(changedArray, function (item) {
            if (! item._destroy) {
                item.order(i);
                i += 1;
            }
        });
    });
    this.collogroups.notifySubscribers(this.collogroups());

    Meaning.counter++;
    Meaning.idMap[this.id] = this;
    vM.entryEdit.ui.allMeanings.push(this);
};
Meaning.counter = 0;
Meaning.idMap = {};


Entry = function () {
};


expandOrCollapse = function () { this.isExpanded(!this.isExpanded()); }
Collogroup.prototype.expandOrCollapse = expandOrCollapse;
Meaning.prototype.expandOrCollapse = expandOrCollapse;


vM.entryEdit = {
    ui: {
        entry: {},
        choices: vM.dataToInitialize.choices,
        labels: vM.dataToInitialize.labels,
        slugs: vM.dataToInitialize.slugs,
    }
};

// Загрузка данных в модель пользовательского интерфейса и её инициализация
function viewModelInit(data) {

    vM.entryEdit.ui.allMeanings = vM.entryEdit.ui.allMeanings || [];
    vM.entryEdit.ui.allCollogroups = vM.entryEdit.ui.allCollogroups || [];
    vM.entryEdit.ui.allExamples = vM.entryEdit.ui.allExamples || [];

    vM.entryEdit.data = ko.mapping.fromJS(data, mapping);

    var viewModel = vM.entryEdit,
        dataModel = viewModel.data,
        uiModel = viewModel.ui,
        dataEntry = dataModel.entry,
        uiEntry = uiModel.entry;


    dataEntry.orthvars.subscribe(function (changedArray) {
        var i = 1;
        ko.utils.arrayForEach(changedArray, function (item) {
            if (! item._destroy) {
                item.order(i);
                i += 1;
            }
        });
    });
    dataEntry.orthvars.notifySubscribers(dataEntry.orthvars());

    uiEntry.headword = ko.computed(function () {
        var orthvars = dataEntry.orthvars(),
            isNotDestroyed = function (item) { return ! item._destroy; };
        return ko.utils.arrayFilter(orthvars, isNotDestroyed)[0].idem();
    });

    uiEntry.part_of_speech = ko.computed(function () {
        var x = this.data.entry.part_of_speech(),
            y = this.ui.labels.part_of_speech;
        if (x in y) {
            return y[x];
        } else {
            console.log('Часть речи "', x, '" не найдена среди ', y);
            return '';
        }
    }, viewModel);

    uiEntry.meanings = (function () {
        var allMeanings = dataModel.meanings(),
            entryMeanings = ko.observableArray([]),
            i, j, meaning;

        entryMeanings.subscribe(function (changedArray) {
            var i = 1;
            ko.utils.arrayForEach(changedArray, function (item) {
                item.parent_meaning_id(null);
                item.entry_container_id(dataModel.entry.id());
                item.collogroup_container_id(null);
                if (! item._destroy) {
                    item.order(i);
                    i += 1;
                }
            });
        });

        for (i = 0, j = allMeanings.length; i < j; i++) {
            meaning = allMeanings[i];
            if (meaning.parent_meaning_id() === null) {
                entryMeanings.push(meaning);
            } else {
                Meaning.idMap[meaning.parent_meaning_id()]
                    .childMeanings.push(meaning);
            }
        }

        return entryMeanings;
    })();

    // Просматриваем список всех примеров и, если пример должен стоять при
    // определенном значении, а не просто добавлен в мешок примеров при статье,
    // добавляем его в список примеров конкретного значения.
    (function () {
        var allExamples = dataModel.examples(),
            i, j, example;

        for (i = 0, j = allExamples.length; i < j; i++) {
            example = allExamples[i];
            if (example.meaning_id() !== null) {
                Meaning.idMap[example.meaning_id()]
                    .selfExamples.push(example);
            }
        }
    })();

    uiModel.jsonData = function () {
        var entryData = {
                entry: dataEntry,
                collogroups: uiModel.allCollogroups,
                etymologies: dataModel.etymologies,
                examples: uiModel.allExamples,
                meanings: uiModel.allMeanings
            };
        return ko.mapping.toJSON(entryData, mapping);
    };

    viewModel.dirtyFlag = ko.dirtyFlag(dataModel);

}
viewModelInit(vM.dataToInitialize.entry);

var viewModel = vM.entryEdit,
    dataModel = viewModel.data,
    uiModel = viewModel.ui,
    dataEntry = dataModel.entry,
    uiEntry = uiModel.entry;

uiModel.save = function () {
    // Возвращаем promise-объект
    return $.post('/entries/save/', { 'json': uiModel.jsonData() });
};

uiModel.addMeaning = function (meanings, containerType, container, containerMeaning) {
    var meaning = new Meaning({}, containerType, container, containerMeaning);
    meanings.push(meaning);
    uiModel.meaningBeingEdited(meaning);
};

uiModel.destroyMeaning = function (meanings, meaning) {
    if (typeof meaning.id === 'number') {
        meanings.destroy(meaning);
    } else {
        meanings.remove(meaning);
        uiModel.allMeanings.splice(uiModel.allMeanings.indexOf(meaning), 1);
    }
};

uiModel.addExample = function () {
};

uiModel.destroyExample = function (examples, example) {
    if (typeof example.id === 'number') {
        examples.destroy(example);
    } else {
        examples.remove(example);
        uiModel.allExamples.splice(uiModel.allExamples.indexOf(example), 1);
    }
};

uiModel.addCollogroup = function () {
};

uiModel.destroyCollogroup = function (collogroups, collogroup) {
    if (typeof collogroup.id === 'number') {
        collogroups.destroy(collogroup);
    } else {
        collogroups.remove(collogroup);
        uiModel.allCollogroups.splice(
                uiModel.allCollogroups.indexOf(collogroup),
                1);
    }
};

uiModel.addOrthvar = function () {
    dataEntry.orthvars.push(new Orthvar({}, dataEntry));
};

uiModel.destroyOrthvar = function (orthvar) {
    if (typeof orthvar.id === 'number') {
        dataEntry.orthvars.destroy(orthvar);
    } else {
        dataEntry.orthvars.remove(orthvar);
    }
};

uiModel.addParticiple = function () {
    dataEntry.participles.push(new Participle({}, dataEntry));
};

uiModel.destroyParticiple = function (item) {
    if (typeof item.id === 'number') {
        dataEntry.participles.destroy(item);
    } else {
        dataEntry.participles.remove(item);
    }
};

uiModel.meaningBeingEdited = ko.observable(null);
uiModel.showSaveDialogue = ko.observable(false);
uiModel.saveAndExit = function () {
    var persistingDataPromise = uiModel.save();
    persistingDataPromise
        .done(function () {
            viewModel.undoStorage.clear();
            window.location = '/';
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR: ', jqXHR);
            console.log('textStatus: ', textStatus);
            console.log('Error thrown: ', errorThrown);
            alert('При сохранении статьи произошла непредвиденная ошибка.');
        });
}
uiModel.exitWithoutSaving = function () {
    window.location = '/';
}


// Активация работы вкладок
$('nav.tabs li').click(function () {
    $('nav.tabs li.current').removeClass('current');
    $('section.tabcontent.current').removeClass('current');
    var x = $(this);
    x.addClass('current');
    $(x.find('a').attr('href')).addClass('current');
});

// Активация сохранения json-снимков данных в локальном хранилище.
vM.entryEdit.undoStorage = (function () {
    var uS,  // uS -- undoStorage
        snapshotsKey = 'entry.' + ko.utils.unwrapObservable(
                                             vM.entryEdit.data.entry.id),
        cursorKey = snapshotsKey + '.cursor',
        viewModel = vM.entryEdit,
        cursor = ko.observable(0),
        snapshots = ko.observableArray([]),
        shouldSkipDump = false;

    ko.computed(function() {
        console.log(
            'cursor:', cursor(),
            'snapshots().length:', snapshots().length
            );
    });

    function load(N) {
        console.log('load', N);
        var snapshot = JSON.parse(snapshots()[N]);
        viewModelInit(snapshot);
    }

    function dock(N) {
        // Удаление всех дампов после N (обрубание хвоста). Необходимо
        // в том случае, если была произведена операция undo и в статью были
        // внесены дополнительные изменения, поскольку все отменённые дампы
        // становятся после этого ненужными. Напротив, возникает необходимость
        // создания другой ветки дампов.
        console.log('dock', N);
        snapshots.splice(N);
    }

    function dump() {
        if (!shouldSkipDump && viewModel.dirtyFlag.isDirty()) {
            viewModel.dirtyFlag.reset();
            if (cursor.peek() < snapshots.peek().length) {
                dock(cursor.peek())
            }
            console.log('dump');
            snapshots.push(viewModel.ui.jsonData());
            cursor(cursor.peek() + 1);
        }
    }

    function mayNotUndo() {
        return cursor() < 2;
    }

    function mayNotRedo() {
        return snapshots().length === cursor();
    }

    function redo() {
        console.log('redo');
        if (! mayNotRedo()) {
            var n = cursor();
            load(n);
            cursor(n + 1);
        }
    }

    function undo() {
        console.log('undo');
        if (! mayNotUndo()) {
            var n = cursor() - 1;
            load(n);
            cursor(n);
        }
    }

    function clear() {
        cursor(0);
        snapshots.removeAll();
        localStorage.removeItem(snapshotsKey);
        localStorage.removeItem(cursorKey);
    }

    function resumePreviousSession() {
        // Если в локальном хранилище что-то осталось, предлагает пользователю
        // восстанавливить предыдущаю сессию правки статьи. В противном случае
        // молча начинает новую сессию.
        var prevSnapshots = JSON.parse(localStorage.getItem(snapshotsKey)),
            prevCursor = JSON.parse(localStorage.getItem(cursorKey));
        console.log('prev snapshots:', prevSnapshots && prevSnapshots.length, 'prev cursor:', prevCursor);
        // TODO: здесь должно выводиться предложение пользователю восстановить
        // предыдущую сессию, если от неё остались данные.
    }

    function init() {
        // TODO: Здесь должна быть обработка случаев, когда страницу изменения
        // покинули не должным образом и в локальном хранилище что-то осталось.
        // Пользователю надо предложить восстановить последнее созданное им
        // состояние для тех статей, которые не были должным образом сохранены.
        resumePreviousSession();

        snapshots.subscribe(function () {
            localStorage.setItem(snapshotsKey, JSON.stringify(snapshots()));
        });

        cursor.subscribe(function (newValue) {
            localStorage.setItem(cursorKey, newValue);
        });

        clear();
    }

    uS = {
        clear: clear,
        dump: ko.computed(dump).extend({ throttle: 1000 }),
        load: load,
        shouldDisableRedo: ko.computed(mayNotRedo),
        shouldDisableUndo: ko.computed(mayNotUndo),
        redo: redo,
        undo: undo,
    };

    init();

    return uS;
})()

ko.applyBindings(viewModel, $('#main').get(0));

// Поднять занавес
$('.curtain').fadeOut();


} catch(e) {
    $.post('/entries/jserror/',
           {entryId: vM.dataToInitialize.entry.entry.id || 'unknown',
            errorObj: e});
    throw e;
}
