try {

function newer(obj, data, Constructor, args) {
    var allItems = {
            Etymology: obj && obj.etymologies,
            Participle: obj && obj.participles,
            Orthvar: obj && obj.orthvars,
            Collocation: obj && obj.collocations,
            Context: obj && obj.contexts,
            Greq: obj && obj.greqs,
            Example: vM.entryEdit.ui.allExamples,
            Collogroup: vM.entryEdit.ui.allCollogroups,
            Meaning: vM.entryEdit.ui.allMeanings,
            Entry: vM.entryEdit.data.entry ? [vM.entryEdit.data.entry]:[],
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

function upsert(object, attrname, data, defaultValue, observable) {
    // Upsert property ``attrname`` in the ``object``
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

function upsertArray(object, attrname,
                     data, Constructor, args, observableArray) {
    // Upsert array property ``attrname`` in the ``object``

    var list = data && data[attrname] || [],
        observableArray = observableArray || ko.observableArray;
    if (typeof object[attrname] !== 'undefined'
        && ko.isObservable(object[attrname]) {
            list.forEach(function (listItem) {
                newer(object, listItem /* data */, Constructor, args)
            });
    } else {
        object[attrname] = observableArray();
        upsertArray(object, attrname, data, Constructor, args, observableArray);
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
    upsert(this, 'additional_info', data, '');
    upsert(this, 'collocation_id', data, collocation.id());
    upsert(this, 'corrupted', data, false);
    upsert(this, 'entry_id', data, entry.id());
    upsert(this, 'etymon_to_id', data, etymonTo.id());
    upsert(this, 'gloss', data, '');
    upsert(this, 'id', data, 'etymon' + Etymology.counter);
    upsert(this, 'language', data, 'a' /* греческий */);
    upsert(this, 'mark', data, '');
    upsert(this, 'meaning', data, '');
    upsert(this, 'order', data, 345);
    upsert(this, 'questionable', data, false);
    upsert(this, 'source', data, '');
    upsert(this, 'text', data, '');
    upsert(this, 'translit', data, '');
    upsert(this, 'unclear', data, false);
    upsert(this, 'unitext', data, '');
    Etymology.counter++;
};
Etymology.counter = 0;
Etymology.idMap = {};


Participle = function (entry, data) {
    upsert(this, 'idem', data, '');
    upsert(this, 'tp', data, '');
    upsert(this, 'order', data, 345);
    upsert(this, 'entry_id', data, entry.id(), nonObservable);
    upsert(this, 'id', data, 'participle' + Participle.counter, nonObservable);
    Participle.counter++;
};
Participle.counter = 0;


Orthvar = function (entry, data) {
    upsert(this, 'idem', data, '');
    upsert(this, 'order', data, 345);
    upsert(this, 'entry_id', data, entry.id(), nonObservable);
    upsert(this, 'id', data, 'orthvar' + Orthvar.counter, nonObservable);
    Orthvar.counter++;
};
Orthvar.counter = 0;


Collocation = function (collogroup, data) {
    upsert(this, 'civil_equivalent', data, '');
    upsert(this, 'collocation', data, '');
    upsert(this, 'collogroup_id', data, collogroup.id);
    upsert(this, 'id', data, 'collocation' + Collocation.counter, nonObservable);
    upsert(this, 'order', data, 345);
    Collocation.counter++;
};
Collocation.counter = 0;


Context = function (meaning, data) {
    upsert(this, 'context', data, '');
    upsert(this, 'id', data, 'context' + Context.counter, nonObservable);
    upsert(this, 'left_text', data, '');
    upsert(this, 'meaning_id', data, meaning.id);
    upsert(this, 'order', data, 345);
    upsert(this, 'right_text', data, '');
    Context.counter++;
};
Context.counter = 0;


Greq = function (example, data) {
    upsert(this, 'additional_info', data, '');
    upsert(this, 'corrupted', data, false);
    upsert(this, 'for_example_id', data, example.id);
    upsert(this, 'id', data, 'greq' + Greq.counter, nonObservable);
    upsert(this, 'initial_form', data, '');
    upsert(this, 'mark', data, '');
    upsert(this, 'position', data, 0);
    upsert(this, 'source', data, '');
    upsert(this, 'unitext', data, '');
    Greq.counter++;
};
Greq.counter = 0;


Example = function (meaning, entry, collogroup, data) {
    upsert(this, 'additional_info', data, '');
    upsert(this, 'address_text', data, '');
    upsert(this, 'collogroup_id', data, collogroup ? collogroup.id : null);
    upsert(this, 'entry_id', data, entry.id());
    upsert(this, 'example', data, '');
    upsert(this, 'greek_eq_status', data, '');
    upsertArray(this, 'greqs', data, Greq, [this]);
    upsert(this, 'hidden', data, false);
    upsert(this, 'id', data, 'example' + Example.counter);
    upsert(this, 'meaning_id', data, meaning.id);
    upsert(this, 'order', data, 345);
    if (vM.entryEdit.ui.allExamples.indexOf(this) === -1) {
        Example.counter++;
        vM.entryEdit.ui.allExamples.push(this);
    }
};
Example.counter = 0;


Collogroup = function (containerType, container, data) {
    // containerType := 'entry' | 'meaning'
    var defaultBaseEntryId = (containerType === 'entry'? container.id():null),
        defaultBaseMeaningId = (containerType === 'meaning'? container.id:null),
        defaultId = 'collogroup' + Collogroup.counter,
        self = this;

    upsertArray(this, 'collocations', data, Collocation, [this]);
    upsert(this, 'base_entry_id', data, defaultBaseEntryId);
    upsert(this, 'base_meaning_id', data, defaultBaseMeaningId);
    upsert(this, 'id', data, defaultId, nonObservable);
    upsert(this, 'order', data, 345);
    upsertArray(this, 'meanings', data, Meaning, ['collogroup', this, null]);

    this.isExpanded = this.isExpanded || ko.observable(false);

    if (vM.entryEdit.ui.allCollogroups.indexOf(this) === -1) {
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
    }
};
Collogroup.counter = 0;


Meaning = function () {
    var data = {},
        containerType = '',
        container = null,
        parentMeaning = null;

    switch (arguments.length) {
    case 1:
        data = arguments[0];
        break;
    case 3:
        parentMeaning = arguments[2];
        // проваливаемся ниже, обрабатываем первые два аргумента.
    case 2:
        containerType = arguments[0];
        container = arguments[1];
        break;
    default:
        throw new Error('Неправильное количество аргументов для Meaning');
    }

    var d4ltEntryCntrId = (containerType === 'entry'? container.id():null),
        d4ltCgCntrId = (containerType === 'collogroup'? container.id:null),
        self = this;

    upsert(this, 'meaning', data, '');
    upsert(this, 'gloss', data, '');
    upsert(this, 'metaphorical', data, false);
    upsert(this, 'additional_info', data, '');
    upsert(this, 'substantivus', data, false);
    upsert(this, 'substantivus_type', data, '');
    upsert(this, 'hidden', data, false);
    upsertArray(this, 'contexts', data, Context, [this]);
    upsert(this, 'entry_container_id', data, d4ltEntryCntrId);
    upsert(this, 'collogroup_container_id', data, d4ltCgCntrId);
    upsert(this, 'parent_meaning_id', data, parentMeaning.id || null);
    upsert(this, 'id', data, 'meaning' + Meaning.counter, nonObservable);
    upsert(this, 'order', data, 345);
    upsertArray(this, 'collogroups', data, Collogroup, ['meaning', this]);

    this.isExpanded = this.isExpanded || ko.observable(false);
    this.childMeanings = this.childMeanings || ko.observableArray([]);
    this.selfExamples = this.selfExamples || ko.observableArray([]);

    if () {
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
    }
};
Meaning.counter = 0;
Meaning.idMap = {};


Entry = function (data) {
    upsert(this, 'additional_info', data, '');
    upsert(this, 'antconc_query', data, '');
    upsert(this, 'canonical_name', data, '');
    upsert(this, 'civil_equivalent', data, '');
    upsert(this, 'derivation_entry_id', data, null);
    upsert(this, 'duplicate', data, false);
    upsert(this, 'gender', data, '');
    upsert(this, 'genitive', data, '');
    upsert(this, 'good', data, 'b' /* статья не подходит */);
    upsert(this, 'hidden', data, false);
    upsert(this, 'homonym_gloss', data, '');
    upsert(this, 'homonym_order', data, null);
    upsert(this, 'id', data, null);
    upsert(this, 'nom_sg', data, '');
    upsert(this, 'onym', data, '');
    upsert(this, 'part_of_speech', data, '');
    upsert(this, 'participle_type', data, '');
    upsert(this, 'possessive', data, false);
    upsert(this, 'questionable_headword', data, false);
    upsert(this, 'reconstructed_headword', data, false);
    upsert(this, 'sg1', data, '');
    upsert(this, 'sg2', data, '');
    upsert(this, 'short_form', data, '');
    upsert(this, 'status', data, 'c' /* Статья создана */);
    upsert(this, 'tantum', data, '');
    upsert(this, 'uninflected', data, false);
    upsertArray(this, 'participles', data, Participle, [this]);
    upsertArray(this, 'orthvars', data, Orthvar, [this]);
    upsertArray(this, 'author_ids', data, Number, []);
};


expandOrCollapse = function () { this.isExpanded(!this.isExpanded()); }
Collogroup.prototype.expandOrCollapse = expandOrCollapse;
Meaning.prototype.expandOrCollapse = expandOrCollapse;


vM.entryEdit = {
    data: {},
    ui: {
        entry: {},
        choices: vM.dataToInitialize.choices,
        labels: vM.dataToInitialize.labels,
        slugs: vM.dataToInitialize.slugs,
    }
};

// Загрузка данных в модель пользовательского интерфейса и её инициализация
function viewModelInit(data) {
    var firstRun = (vM.entryEdit.data.entry ? false:true);

    vM.entryEdit.ui.allEtymologies = vM.entryEdit.ui.allEtymologies || [];
    vM.entryEdit.ui.allMeanings = vM.entryEdit.ui.allMeanings || [];
    vM.entryEdit.ui.allCollogroups = vM.entryEdit.ui.allCollogroups || [];
    vM.entryEdit.ui.allExamples = vM.entryEdit.ui.allExamples || [];

    if (firstRun) {
        vM.entryEdit.data.entry = new Entry(data.entry);
        data.etymologies.forEach(funtion (item) {
            vM.entryEdit.ui.allEtymologies.push(new Etymology(item));
        });
        data.meanings.forEach(funtion (item) {
            vM.entryEdit.ui.allMeanings.push(new Meaning(item));
        });
    } else {
        Entry.call(vM.entryEdit.data.entry, data.entry);
    }


    var viewModel = vM.entryEdit,
        dataModel = viewModel.data,
        uiModel = viewModel.ui,
        dataEntry = dataModel.entry,
        uiEntry = uiModel.entry;


    if (firstRun) {

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

    }

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
    var meaning = new Meaning(containerType, container, containerMeaning);
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
