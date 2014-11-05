try {


var topic = 'entry_change',
    constructors = [Etymology, Participle, Orthvar,
                    Collocation, Context, Greq,
                    Example, Collogroup, Meaning,
                    Entry];

constructors.nameMap = {'Etymology': Etymology, 'Participle': Participle,
    'Orthvar': Orthvar, 'Collocation': Collocation, 'Context': Context,
    'Greq': Greq, 'Example': Example, 'Collogroup': Collogroup,
    'Meaning': Meaning, 'Entry': Entry};

// Функция создающая датчики, оповещающие о том, что словарная статья
// изменилась.
function snapshotObservable(observable) {
    observable = observable || ko.observable;
    return function () {
        var o = observable.apply(null, arguments);
        o.__$ID$__ = snapshotObservable.counter++;
        o.subscribe(function (value) {
            ko.postbox.publish(topic, [o.__$ID$__, value]);
        });
        return o;
    };
}
snapshotObservable.counter = 0;

// Вспомогательные для конструкторов-реставраторов функции.
function upsert(object, attrname, data, defaultValue, observable) {
    // Upsert property ``attrname`` in the ``object``
    var value = data && data[attrname] || defaultValue;
    observable = observable || snapshotObservable();
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

function crudArrayItems(voodoo, spec, Constructor) {
    // Create, update or delete voodoo array items
    // according to spec.

    if (!Constructor) {
        voodoo(spec);
        return;
    }

    var all = Constructor.all,
        bag = Constructor.bag,
        specItem, voodooItem,
        id, otherId,
        object;

    for (var i = 0, j = spec.length; i < j; i++) {
        specItem = spec[i];
        id = specItem.id;
        object = all.idMap[id];
        if (object) {
            Constructor.call(object, specItem);
        } else {
            object = new Constructor(specItem);
        }

        bag.push(object);
        bag.idMap[id] = object;

        voodooItem = voodoo()[i];
        otherId = voodooItem && voodooItem.id();
        if (otherId !== id) {
            voodoo.splice(i, 1, object);
        }
    }
    voodoo.splice(i);
}

function upsertArray(object, attrname, Constructor, data, observableArray) {
    // Upsert array property ``attrname`` in the ``object``

    var spec = data && data[attrname] || [];
    observableArray = observableArray || snapshotObservable(ko.observableArray);

    if (!object.hasOwnProperty(attrname)) {
        object[attrname] = observableArray();
        if (Constructor) {
            object[attrname].itemConstructor = Constructor;
            object[attrname].itemAdder = itemAdder;
            object[attrname].itemDestroyer = itemDestroyer;
            Constructor.guarantor && Constructor.guarantor(object, attrname);
        }
        upsertArray(object, attrname, Constructor, data, observableArray);
    } else {
        crudArrayItems(object[attrname], spec, Constructor);
    }
}

// Общие для всех свойств-массивов методы добавления/удаления элементов
function itemAdder() {
    var array = this,
        constructorArguments = Array.prototype.slice.call(arguments);
    return {
        do: function () {
            var item = new (Function.prototype.bind.apply(
                array.itemConstructor, [null].concat(constructorArguments)));
            array.push(item);
            item.edit();
        }
    };
}

function itemDestroyer(item) {
    var array = this;
    return {
        do: function () {
            if (typeof item.id() === 'number') {
                array.itemConstructor.shredder.push(item.id());
            }
            array.remove(item);
            array.itemConstructor.all.remove(item);
        }
    };
}

function itemPoolReturner(item) {
    var array = this;
    return {
        do: function () {
            array.remove(item);
            if (item.collogroup_id() !== null) {
                Collogroup.all.idMap[item.collogroup_id()]
                    .unsorted_examples.push(item);
            } else {
                dataModel.entry.unsorted_examples.push(item);
            }
        }
    };
}

// Конструкторы-реставраторы
function Etymology() {
    /* Etymology(container[, etymonTo])
     * Etymology(data)
     */
    var data = {},
        collocation_id = null,
        entry_id = null,
        etymonTo_id = null;

    if (arguments[0] instanceof Entry) {
        entry_id = arguments[0].id();
    } else if (arguments[0] instanceof Collogroup) {
        // FIX: Впоследствии Collogroup должно исчезнуть,
        // будучи заменено на Collocation. Словосочетания должны также,
        // как и лексемы просто иметь разные варианты написания.
        collocation_id = arguments[0].id();
    } else {
        data = arguments[0];
    }

    if (arguments.length > 1 && arguments[1]) {
        etymonTo_id = arguments[1].id();
    }

    upsert(this, 'additional_info', data, '');
    upsert(this, 'collocation_id', data, collocation_id);
    upsert(this, 'corrupted', data, false);
    upsert(this, 'entry_id', data, entry_id);
    upsert(this, 'etymon_to_id', data, etymonTo_id);
    upsert(this, 'gloss', data, '');
    upsert(this, 'id', data, 'etymon' + Etymology.all.length);
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
    upsertArray(this, 'etymologies', Etymology, data);
    Etymology.all.append(this);
}
Etymology.hideFromServer = ['etymologies'];

function Participle() {
    /* Participle(entry)
     * Participle(data)
     */
    var data = {},
        entry_id = null;

    if (arguments[0] instanceof Entry) entry_id = arguments[0].id();
    else data = arguments[0];

    upsert(this, 'idem', data, '');
    upsert(this, 'tp', data, '');
    upsert(this, 'order', data, 345);
    upsert(this, 'entry_id', data, entry_id);
    upsert(this, 'id', data, 'participle' + Participle.all.length);
    Participle.all.append(this);
}

function Orthvar() {
    /* Orthvar(entry)
     * Orthvar(data)
     */
    var data = {},
        entry_id = null;

    if (arguments[0] instanceof Entry) entry_id = arguments[0].id();
    else data = arguments[0];

    upsert(this, 'idem', data, '');
    upsert(this, 'order', data, 345);
    upsert(this, 'entry_id', data, entry_id);
    upsert(this, 'id', data, 'orthvar' + Orthvar.all.length);
    Orthvar.all.append(this);
}

function Collocation() {
    /* Collocation(collogroup)
     * Collocation(data)
     */
    var data = {},
        collogroup_id = null;

    if (arguments[0] instanceof Collogroup) collogroup_id = arguments[0].id();
    else data = arguments[0];

    upsert(this, 'civil_equivalent', data, '');
    upsert(this, 'collocation', data, '');
    upsert(this, 'collogroup_id', data, collogroup_id);
    upsert(this, 'id', data, 'collocation' + Collocation.all.length);
    upsert(this, 'order', data, 345);
    Collocation.all.append(this);
}

function Context() {
    /* Context(meaning)
     * Context(data)
     */
    var data = {},
        meaning_id = null;

    if (arguments[0] instanceof Meaning) meaning_id = arguments[0].id();
    else data = arguments[0];

    upsert(this, 'context', data, '');
    upsert(this, 'id', data, 'context' + Context.all.length);
    upsert(this, 'left_text', data, '');
    upsert(this, 'meaning_id', data, meaning_id);
    upsert(this, 'order', data, 345);
    upsert(this, 'right_text', data, '');
    Context.all.append(this);
}

function Greq() {
    /* Greq(example)
     * Greq(data)
     */
    var data = {},
        example_id = null;

    if (arguments[0] instanceof Example) example_id = arguments[0].id();
    else data = arguments[0];

    upsert(this, 'additional_info', data, '');
    upsert(this, 'corrupted', data, false);
    upsert(this, 'for_example_id', data, example_id);
    upsert(this, 'id', data, 'greq' + Greq.all.length);
    upsert(this, 'initial_form', data, '');
    upsert(this, 'mark', data, '');
    upsert(this, 'note', data, '');
    upsert(this, 'position', data, 0);
    upsert(this, 'source', data, '');
    upsert(this, 'unitext', data, '');
    upsert(this, 'order', data, 345);
    Greq.all.append(this);
}

function Example() {
    /* Example(meaning, entry[, collogroup])
     * Example(data)
     */
    var data = {},
        meaning_id = null,
        entry_id = null,
        collogroup_id = null;

    if (arguments[0] instanceof Meaning) {
        meaning_id = arguments[0].id();
        entry_id = arguments[1].id();
        if (arguments.length > 2) {
            collogroup_id = arguments[2].id();
        }
    } else {
        data = arguments[0];
    }

    upsert(this, 'additional_info', data, '');
    upsert(this, 'address_text', data, '');
    upsert(this, 'collogroup_id', data, collogroup_id);
    upsert(this, 'entry_id', data, entry_id);
    upsert(this, 'example', data, '');
    upsert(this, 'context', data, '');
    upsert(this, 'greek_eq_status', data, 'L');  // NOTE: По умолчанию ставить
                  // статус 'L' -- "необходимо найти греческие параллели".
    upsertArray(this, 'greqs', Greq, data);
    upsert(this, 'hidden', data, false);
    upsert(this, 'id', data, 'example' + Example.all.length);
    upsert(this, 'meaning_id', data, meaning_id);
    upsert(this, 'note', data, '');
    upsert(this, 'order', data, 345);

    this.context.isVisible || (this.context.isVisible = ko.observable(false));
    Example.all.append(this);
}

function Collogroup() {
    /* Collogroup(container)
     * Collogroup(data)
     */
    var data = {},
        entry_id = null,
        meaning_id = null;

    if (arguments[0] instanceof Entry) {
        entry_id = arguments[0].id();
    } else if (arguments[0] instanceof Meaning) {
        meaning_id = arguments[0].id();
    } else {
        data = arguments[0];
    }

    upsert(this, 'additional_info', data, '');
    upsertArray(this, 'collocations', Collocation, data);
    upsert(this, 'base_entry_id', data, entry_id);
    upsert(this, 'base_meaning_id', data, meaning_id);
    upsert(this, 'id', data, 'collogroup' + Collogroup.all.length);
    upsert(this, 'order', data, 345);
    upsertArray(this, 'meanings', Meaning, data);
    upsertArray(this, 'unsorted_examples', Example, data);
    upsertArray(this, 'etymologies', Etymology, data);

    this.isExpanded || (this.isExpanded = ko.observable(false));
    this.collocations.notEmpty = ko.computed(function () {
        var array = this.collocations();
        if (array.length === 0) {
            array.push(new Collocation(this))
        }
    }, this);
    Collogroup.all.append(this);
}
Collogroup.hideFromServer = ['meanings', 'unsorted_examples', 'etymologies',
    'isExpanded'];

function Meaning() {
    /* Meaning(container[, parentMeaning])
     * Meaning(data)
     */
    var data = null,
        entry_id = null,
        collogroup_id = null,
        meaning_id = null;

    if (arguments[0] instanceof Entry) {
        entry_id = arguments[0].id();
    } else if (arguments[0] instanceof Collogroup) {
        collogroup_id = arguments[0].id();
    } else {
        data = arguments[0];
    }

    if (arguments.length > 1) {
        if (data) {
            throw new Error('Неправильный состав аргументов для Meaning.');
        } else {
            meaning_id = arguments[1].id();
        }
    }
    data = data || {};

    upsert(this, 'meaning', data, '');
    upsert(this, 'gloss', data, '');
    upsert(this, 'metaphorical', data, false);
    upsert(this, 'figurative', data, false);
    upsert(this, 'additional_info', data, '');
    upsert(this, 'substantivus', data, false);
    upsert(this, 'substantivus_type', data, '');
    upsert(this, 'hidden', data, false);
    upsertArray(this, 'contexts', Context, data);
    upsert(this, 'entry_container_id', data, entry_id);
    upsert(this, 'collogroup_container_id', data, collogroup_id);
    upsert(this, 'parent_meaning_id', data, meaning_id);
    upsert(this, 'id', data, 'meaning' + Meaning.all.length);
    upsert(this, 'order', data, 345);
    upsertArray(this, 'collogroups', Collogroup, data);
    upsertArray(this, 'meanings', Meaning, data);
    upsertArray(this, 'examples', Example, data);

    this.isExpanded || (this.isExpanded = ko.observable(false));
    this.substantivus_type.label = ko.pureComputed(
            Meaning.prototype.substantivus_type_label, this);
    Meaning.all.append(this);
}
Meaning.hideFromServer = ['collogroups', 'meanings', 'examples', 'isExpanded'];

function Entry(data) {
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
    upsertArray(this, 'participles', Participle, data);
    upsertArray(this, 'orthvars', Orthvar, data);
    upsertArray(this, 'author_ids', undefined, data);
    upsertArray(this, 'unsorted_examples', Example, data);
    upsertArray(this, 'meanings', Meaning, data);
    upsertArray(this, 'collogroups', Collogroup, data);
    upsertArray(this, 'etymologies', Etymology, data);

    this.part_of_speech.label = ko.pureComputed(
            Entry.prototype.part_of_speech_label, this);
    Entry.all.append(this);
}
Entry.hideFromServer = ['unsorted_examples', 'meanings', 'collogroups',
    'etymologies', 'author_ids'];

// У meaning возможны следующие сочетания значений полей
// entry_container_id (E), collogroup_container_id (C)
// и parent_meaning_id (M):
//
//      E, C, EM, CM.
//
// У etymology возможны следующие сочетания значений полей
// entry_id (E), collocation_id (C) и etymon_to_id (e):
//
//      E, C, Ee, Ce.
//
// У collogroup возможны следующие сочетания значений полей
// base_entry_id (E) и base_meaning_id (M):
//
//      E, M.
//
// У example возможны следующие сочетания значений полей
// entry_id (E), collogroup_id (C) и meaning_id (M):
//
//      E, EM, EC, ECM.
//
// FIX: впоследствии необходимо сделать так:
//
//      E, EM, C, CM.
//
// Присутствие буквы обозначает, что соответствующее поле имеет
// значение отличное от null.


// Гаранты свойств элементов разных списков.
function guarantor(array, func) {
    var subscriber = function (changedArray) { changedArray.forEach(func); };
    array.subscribe(subscriber);
    subscriber(array());
}

function orderGuarantor(object, attrname) {
    guarantor(object[attrname], function (item, index) {
        item.order(index + 1);
    });
}

function examplesGuarantor(object, attrname) {
    var func = {

            'Entry': function (item) {
                item.meaning_id(null);
                item.collogroup_id(null);
                item.entry_id(object.id()); },

            'Collogroup': function (item) {
                item.meaning_id(null);
                item.collogroup_id(object.id()); },

            'Meaning': function (item, index) {
                item.meaning_id(object.id());
                item.collogroup_id(object.collogroup_container_id());
                item.order(index + 1); }

        }[object.constructor.name];

    guarantor(object[attrname], func);

    // NOTE: С практической точки зрения, добавление метода массиву элементов
    // вполне может быть реализовано здесь, как это и сделано ниже. Но от этого
    // разрушается красивая картина, при которой гаранты наделяют массив только
    // функционалом, который при каждом изменении этого массива удостоверяют,
    // что каждый элемент обладает правильным для массива свойствами.
    if (object.constructor.name === 'Meaning') {
        object[attrname].itemPoolReturner = itemPoolReturner;
    }
}

function meaningsGuarantor(object, attrname) {
    var func = {

            'Entry': function (item, index) {
                item.parent_meaning_id(null);
                item.entry_container_id(object.id());
                item.collogroup_container_id(null);
                item.order(index + 1); },

            'Collogroup': function (item, index) {
                item.parent_meaning_id(null);
                item.entry_container_id(null);
                item.collogroup_container_id(object.id());
                item.order(index + 1); },

            'Meaning': function (item, index) {
                item.parent_meaning_id(object.id());
                item.entry_container_id(object.entry_container_id());
                item.collogroup_container_id(object.collogroup_container_id());
                item.order(index + 1); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

function collogroupsGuarantor(object, attrname) {
    var func = {

            'Meaning': function (item, index) {
                item.base_entry_id(null);
                item.base_meaning_id(object.id());
                item.order(index + 1); },

            'Entry': function (item, index) {
                item.base_entry_id(object.id());
                item.base_meaning_id(null);
                item.order(index + 1); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

function etymologiesGuarantor(object, attrname) {
    var func = {

            'Etymology': function (item, index) {
                item.entry_id(null);
                item.collocation_id(null);
                item.etymon_to_id(object.id());
                item.order(index + 1); },

            'Collogroup': function (item, index) {
                item.entry_id(null);
                item.collocation_id(object.id());
                item.etymon_to_id(null);
                item.order(index + 1); },

            'Entry': function (item, index) {
                item.entry_id(object.id());
                item.collocation_id(null);
                item.etymon_to_id(null);
                item.order(index + 1); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

// Дополнительная однократная настройка конструкторов
(function () {
    var i, Constructor;

    function append(item) {
        if (uiModel.vMUpdateTransaction) {
            if (this.cache.indexOf(item) === -1) {
                this.cache.push(item);
                this.idMap[item.id()] = item;
            }
        } else {
            if (this.indexOf(item) === -1) {
                this.push(item);
                this.idMap[item.id()] = item;
            }
        }
    }

    function cacheCommit() {
        if (uiModel.vMUpdateTransaction) {
            Array.prototype.splice.apply(this,
                    [0, this.length].concat(this.cache));
            this.cache.splice(0, this.cache.length);
        }
    }

    function remove(item) {
        var index = this.indexOf(item);
        if (index >= 0) {
            this.splice(index, 1);
        } else {
            throw new Error('Элемент ' + item.constructor.name +
                            ' обязан присутствовать в массиве.');
        }
        delete this.idMap[item.id()];
    }

    function editItem() {
        if (['Collogroup', 'Meaning', 'Example']
                .indexOf(this.constructor.name) > -1)
            uiModel.navigationStack.push(this);
    }

    for (i = constructors.length; i--;) {
        Constructor = constructors[i];
        Constructor.all = [];
        Constructor.all.cache = [];
        Constructor.all.idMap = {};
        Constructor.all.append = append;
        Constructor.all.remove = remove;
        Constructor.all.cacheCommit = cacheCommit;
        Constructor.bag = [];
        Constructor.bag.idMap = {};
        Constructor.shredder = [];
        Constructor.prototype.edit = editItem;
    }

    function toggle() { this.isExpanded(!this.isExpanded()); }
    Collogroup.prototype.toggle = toggle;
    Meaning.prototype.toggle = toggle;

    Meaning.guarantor = meaningsGuarantor;
    Collogroup.guarantor = collogroupsGuarantor;
    Example.guarantor = examplesGuarantor;
    Etymology.guarantor = etymologiesGuarantor;

    Context.guarantor = orderGuarantor;
    Collocation.guarantor = orderGuarantor;
    Greq.guarantor = orderGuarantor;
    Participle.guarantor = orderGuarantor;
    Orthvar.guarantor = orderGuarantor;

    function label(attrname) {
        return function () {
            var x = this[attrname](),
                y = viewModel.ui.labels[attrname];
            if (x in y) {
                return y[x];
            } else {
                if (x !== '') {
                    console.log(attrname, '«' + x + '» is not found among', y);
                }
                return '';
            }
        };
    }
    Meaning.prototype.substantivus_type_label = label('substantivus_type');
    Entry.prototype.part_of_speech_label = label('part_of_speech');
})()

// Пространство имен вуду-модели интерфейса редактирования статьи.
vM.entryEdit = {
    data: {},
    ui: {
        entry: {},
        choices: vM.dataToInitialize.choices,
        labels: vM.dataToInitialize.labels,
        slugs: vM.dataToInitialize.slugs,
    }
};

var viewModel = vM.entryEdit,
    dataModel = viewModel.data,
    uiModel = viewModel.ui,
    uiEntry = uiModel.entry;

// Однократная настройка вуду-модели
(function () {
    // Строим объекты вуду-модели
    uiModel.vMUpdateTransaction = true;
    dataModel.entry = new Entry(vM.dataToInitialize.entry);
    constructors.forEach(function (Constructor) {
        Constructor.all.cacheCommit();
    });
    uiModel.vMUpdateTransaction = false;

    // Добавлям разные датчики второго порядка
    uiEntry.headword = ko.pureComputed({
        read: function () {
            var entry = dataModel.entry;
            if (entry.orthvars().length === 0) {
                entry.orthvars.unshift(new Orthvar(entry));
            }
            return entry.orthvars()[0].idem();
        },
        write: function (value) {
            dataModel.entry.orthvars()[0].idem(value);
        }
    });

    uiModel.currentForm = ko.observable('info');

    // Буфер для перемещения значений, примеров, словосочетаний
    uiModel.cutBuffer = (function () {
        var buffer = ko.observableArray(),
            kopC = ko.pureComputed,
            contentType = function () {
                var x = buffer();
                if (x.length === 0) {
                    return '';
                } else {
                    return x[0].constructor.name;
                }
            },
            contains = function (constructor) {
                return function () {
                    return buffer.contentType() === constructor.name;
                };
            },
            emptyOrContains = function (constructor) {
                return function () {
                    var x = buffer.contentType();
                    return x === '' || x === constructor.name;
                };
            },
            containsCollogroups = contains(Collogroup),
            containsMeanings = contains(Meaning),
            containsExamples = contains(Example),
            emptyOrContainsCollogroups = emptyOrContains(Collogroup),
            emptyOrContainsMeanings = emptyOrContains(Meaning),
            emptyOrContainsExamples = emptyOrContains(Example),
            cutFrom = function (list) {
                return function (item) {
                    if (emptyOrContains(item.constructor)) {
                        list.remove(item);
                        buffer.push(item);
                    } else {
                        console.log(item.constructor.name + ' не может быть ' +
                                    'помещено в буфер обмена, так как он уже ' +
                                    'содержит "' + contentType() + '".');
                    }
                };
            },
            pasteInto = function (list) {
                return function (item) {
                    if (list.itemConstructor.name === contentType()) {
                        list.push.apply(list, buffer.removeAll());
                    }
                };
            };
        buffer.contentType = ko.computed(contentType);
        buffer.containsCollogroups = kopC(containsCollogroups);
        buffer.containsMeanings = kopC(containsMeanings);
        buffer.containsExamples = kopC(containsExamples);
        buffer.emptyOrContainsCollogroups = kopC(emptyOrContainsCollogroups);
        buffer.emptyOrContainsMeanings = kopC(emptyOrContainsMeanings);
        buffer.emptyOrContainsExamples = kopC(emptyOrContainsExamples);
        buffer.cutFrom = cutFrom;
        buffer.pasteInto = pasteInto;
        return buffer;
    })();

    // Навигационный стек
    uiModel.navigationStack = (function () {
        var stack = ko.observableArray([dataModel.entry]),
            entryTab = 'info',
            collogroupTab = {'default': 'variants'},
            meaningTab = {'default': 'editMeaning'},
            previousStack = stack(),
            currentStack = previousStack,
            previousForm = entryTab,
            currentForm = previousForm,
            uiChangeTopic = 'ui_change';

        function rememberUI() {
            previousForm = currentForm;
            previousStack = currentStack;
            currentForm = uiModel.currentForm();
            currentStack = stack.slice(); // NOTE: Вызов метода slice необходим,
            // иначе currentStack и previousStack будут всегда совпадать, т.к.
            // обе переменные будут содержать ссылку на один и тот же массив
            // из недр вудушного массива stack.
        }

        function wait() {
            clearTimeout(rememberUI.timeoutID);
            rememberUI.timeoutID = setTimeout(rememberUI, 300);
        }

        ko.postbox.subscribe(topic, wait);
        ko.postbox.subscribe(uiChangeTopic, wait);
        stack.publishOn(uiChangeTopic);
        uiModel.currentForm.publishOn(uiChangeTopic);

        function stackTop() {
            var s = stack();
            return s.length ? s[s.length - 1] : null;
        }

        function templateName() {
            var obj = stack.top(),
                type = obj && obj.constructor.name || 'none'
                key = obj && obj.id() || 'default';
            uiModel.currentForm({
                'Entry': stack.entryTab,
                'Collogroup': stack.collogroupTab[key] ||
                    stack.collogroupTab['default'],  // NOTE: Второй дизъюнкт
                    // нужен на тот случай, если id найдется, но при
                    // использовании его в качестве ключа ничего в словаре
                    // найдено не будет.
                'Meaning': stack.meaningTab[key] || stack.meaningTab['default'],
                'Example': 'editExample',
                'none': 'saveDialogue'
            }[type]);
        }

        function pop() {
            stack.splice(-1, 1)
        }

        function dump() {
            var i, j, item,
                pSDump = [], cSDump = [];
            for (i=0, j=currentStack.length; i<j; i++) {
                item = currentStack[i];
                cSDump.push([item.constructor.name, item.id()]);
            }
            for (i=0, j=previousStack.length; i<j; i++) {
                item = previousStack[i];
                pSDump.push([item.constructor.name, item.id()]);
            }
            return { previousStack: pSDump, currentStack: cSDump,
                     previousForm: previousForm, currentForm: currentForm };
        }

        function load(array) {
            var i, j, item, stackItem, Constructor;
            // Просматриваем массив с уликами объектов, которые были в стеке,
            // и заменяем улики самими объектами.
            for (i=0, j=array.length; i<j; i++) {
                Constructor = constructors.nameMap[array[i][0]];
                array[i] = Constructor.all.idMap[array[i][1]];
            }
            // Сравниваем полученные объекты с теми, что сейчас в стеке.
            // На основе этого производим обновление стека.
            for (i=0, j=array.length; i<j; i++) {
                item = array[i];
                stackItem = stack()[i];
                if (typeof stackItem === 'undefined' || item !== stackItem) {
                    ko.observableArray.fn.splice.apply(stack,
                            [i, stack().length].concat(array.slice(i)));
                    return;
                }
            }
            // Если в стеке что-то ещё осталось, всё это удаляем.
            stack.splice(i, stack().length);
        }

        // общедоступный API стека
        stack.top = ko.computed(stackTop);

        stack.entryTab = entryTab;
        stack.collogroupTab = collogroupTab;
        stack.meaningTab = meaningTab;
        stack.subscribe(templateName);

        stack.pop = pop;
        stack.dump = dump;
        stack.load = load;

        return stack;
    })();


    // Иерархия объектов статьи.
    uiModel.hierarchy = (function () {
        var hierarchy = {},
            stack = uiModel.navigationStack;

        function getParent(x, propertyList) {
            // propertyList ::=
            //      [[propName1, Constructor1], [propName2, Constructor2], ...]
            var i, j, propName, Constructor;
            for (var i = 0, j = propertyList.length; i < j; i++) {
            propName = propertyList[i][0];
                Constructor = propertyList[i][1];
                if (x[propName]() !== null) {
                    return Constructor.all.idMap[x[propName]()];
                }
            }
            throw new Error('Ancestor cannot be found!');
        }

        function getSelfOrUpwardNearest(x, type) {
            var i, map = {
                'Meaning': [['parent_meaning_id', Meaning],
                    ['collogroup_container_id', Collogroup],
                    ['entry_container_id', Entry]],

                'Example': [['meaning_id', Meaning],
                    ['collogroup_id', Collogroup],
                    ['entry_id', Entry]],

                'Collogroup': [['base_meaning_id', Meaning],
                    ['x.base_entry_id', Entry]] };

            if (!x) return null;
            if (x.constructor.name === type) return x;
            do {
                i = map[x.constructor.name];
                if (typeof i === 'undefined') return null;
                x = getParent(x, i)
            } while (x.constructor.name !== type);

            return x;
        }

        function collogroup() {
            return getSelfOrUpwardNearest(stack.top(), 'Collogroup');
        }

        function meaning() {
            var x, y, top = stack.top();
            if (!top || top.constructor.name === 'Collogroup') return null;
            x = getSelfOrUpwardNearest(top, 'Meaning');
            if (x) {
                y = getParent(x, [['parent_meaning_id', Meaning],
                                  ['collogroup_container_id', Collogroup],
                                  ['entry_container_id', Entry]]);
                if (y && y.constructor.name === 'Meaning') return y;
            }
            return x;
        }

        function usage() {
            var x, y, top = stack.top();
            if (!top || top.constructor.name === 'Collogroup') return null;
            x = getSelfOrUpwardNearest(stack.top(), 'Meaning');
            if (x) {
                y = getParent(x, [['parent_meaning_id', Meaning],
                                  ['collogroup_container_id', Collogroup],
                                  ['entry_container_id', Entry]]);
                if (y && y.constructor.name === 'Meaning') return x;
            }
            return null;
        }

        function example() {
            var top = stack.top();
            if (top && top.constructor.name === 'Example')
                return top;
            else
                return null;
        }

        function makeSlug(text, wordLimit) {
            var toBeChanged;
            wordLimit = wordLimit || 2,
            text = text.split(/\s+/);
            toBeChanged = (text.length > wordLimit);
            if (toBeChanged && (text[0].length < 3 || text[1].length < 3)) {
                wordLimit += 1;
            }
            text = text.slice(0, wordLimit).join(' ');
            if (toBeChanged) {
                text += '…'
                text = text.replace(/[\.\,\;\:\?\!…]+$/, '…');
            }
            return text;
        }

        function collogroupSlug() {
            var x = hierarchy.collogroup();
            return x ? x.collocations()[0].collocation() : '';
        }

        function makeMeaningSlug(x) {
            if (x) {
                x = x.meaning() || x.gloss() || '';
                return makeSlug(x);
            } else {
                return '';
            }
        }

        function meaningSlug() { return makeMeaningSlug(hierarchy.meaning()); }
        function usageSlug() { return makeMeaningSlug(hierarchy.usage()); }

        function exampleSlug() {
            var x = hierarchy.example();
            x = (x ? makeSlug(x.example()) : '');
            return x.replace(/[\.\,\!\?\;\:…]$/, '');
        }

        // Общедоступное API
        hierarchy.collogroup = ko.pureComputed(collogroup);
        hierarchy.meaning = ko.pureComputed(meaning);
        hierarchy.usage = ko.pureComputed(usage);
        hierarchy.example = ko.pureComputed(example);

        hierarchy.collogroupSlug = ko.pureComputed(collogroupSlug);
        hierarchy.meaningSlug = ko.pureComputed(meaningSlug);
        hierarchy.usageSlug = ko.pureComputed(usageSlug);
        hierarchy.exampleSlug = ko.pureComputed(exampleSlug);

        return hierarchy;
    })();


    // Изменение отступа в навигационной цепочке в зависимости от того,
    // редактируется ли словосочетание.
    function breadCrumbsPadder() {
        var x = $('#firstBreadCrumb'),
            hierarchy = uiModel.hierarchy,
            collogroup = hierarchy.collogroup(),
            meaning = hierarchy.meaning(),
            width = $('#eA--entry').outerWidth() +
                parseInt($('#eA--collocation').css('paddingLeft'));
        if (collogroup) {
            x.css('paddingLeft', width);
        } else {
            x.css('paddingLeft', '');
        }
    }
    uiModel.navigationStack.subscribe(breadCrumbsPadder);


    // Диалог сохранения.
    uiModel.saveDialogue = (function () {

        function prepareOne(x, Constructor) {
            var array = Constructor.hideFromServer, i, j;
            x = ko.toJS(x);
            if (array) {
                for (i=0, j=array.length; i<j; i++) {
                    delete x[array[i]];
                }
            }
            return x;
        }

        function prepareAll(Constructor) {
            var i, j, x, array = [], all = Constructor.all;
            for (i=0, j=all.length; i<j; i++) {
                x = prepareOne(all[i], Constructor);
                array.push(x);
            }
            return array;
        }

        function saveAndExit() {
            var data, persistingDataPromise,
                toDestroy = {};

            constructors.forEach(function (item) {
                toDestroy[item.name] = item.shredder;
            });

            data = ko.toJSON({
                // FIX: Необходимо либо избавиться от collogroups, etymologies,
                // examples и meanings ниже, и тогда необходимо менять способ
                // обработки сохраняемых данных на сервере. Либо в entry
                // вырезАть все свойства, которые уже присутствуют в этих
                // collogroups, etymologies и т.п.
                        entry: prepareOne(dataModel.entry, Entry),
                        collogroups: prepareAll(Collogroup),
                        etymologies: prepareAll(Etymology),
                        examples: prepareAll(Example),
                        meanings: prepareAll(Meaning),
                        toDestroy: toDestroy,
                });

            // Получаем promise-объект
            persistingDataPromise = $.post('/entries/save/', {'json': data});

            persistingDataPromise
                .done(uiModel.saveDialogue.exitWithoutSaving)
                .fail(function (jqXHR, textStatus, errorThrown) {
                    console.log('jqXHR: ', jqXHR);
                    console.log('textStatus: ', textStatus);
                    console.log('Error thrown: ', errorThrown);
                    alert('При сохранении статьи произошла непредвиденная ошибка.');
                });
        }

        function exitWithoutSaving() {
            viewModel.undoStorage.clear();
            window.location = vM.entryURL;
        }

        function cancel() {
            uiModel.navigationStack.push(viewModel.data.entry)
        }

        // saveDialogue API
        return {
            saveAndExit: saveAndExit,
            exitWithoutSaving: exitWithoutSaving,
            cancel: cancel,
        };
    })();

    // Активация работы вкладок
    $('nav.breadTabs').on('click', 'li.tab', function () {
        var x = $(this),
            y = x.data('href').slice(1),
            stack = uiModel.navigationStack,
            top = stack.top(),
            key = top && top.id();
        uiModel.currentForm(y);
        switch (top && top.constructor.name) {
        case 'Entry':
            stack.entryTab = y;
            break;
        case 'Collogroup':
            stack.collogroupTab[key] = y;
            break;
        case 'Meaning':
            stack.meaningTab[key] = y;
            break;
        }
    });

    // Активация сохранения json-снимков данных в локальном хранилище.
    viewModel.undoStorage = (function () {
        var uS,  // uS -- undoStorage
            argus,
            snapshotsKey = 'entry.' + dataModel.entry.id(),
            cursorKey = snapshotsKey + '.cursor',
            cursor = ko.observable(0),
            snapshots = ko.observableArray([]);

        argus = (function () {
            var io = ko.observable();

            function guard() {
                if (!io()) {
                    io(ko.postbox.subscribe(topic, wait));
                }
                uiModel.vMUpdateTransaction = false;
            }

            function doze() {
                if (io()) {
                    io().dispose();
                    io(null);
                }
                uiModel.vMUpdateTransaction = true;
            }

            return { guard: guard,
                     doze:  doze };
        })();

        function load(N, M) {
            var snapshot = JSON.parse(snapshots()[N]);
            argus.doze();
            Entry.call(dataModel.entry, snapshot.entry);
            constructors.forEach(function (item) {
                item.shredder = snapshot.toDestroy[item.name];
                item.all.cacheCommit();
            });
            if (M === N) {
                uiModel.navigationStack.load(snapshot.view.currentStack);
                uiModel.currentForm(snapshot.view.currentForm);
            } else {
                snapshot = JSON.parse(snapshots()[M]);
                uiModel.navigationStack.load(snapshot.view.previousStack);
                uiModel.currentForm(snapshot.view.previousForm);
            }
            argus.guard();
        }

        function dock(N) {
            // Удаление всех дампов после N (обрубание хвоста). Необходимо
            // в том случае, если была произведена операция undo и в статью
            // были внесены дополнительные изменения, поскольку все отменённые
            // дампы становятся после этого ненужными. Напротив, возникает
            // необходимость создания другой ветки дампов.
            snapshots.splice(N);
        }

        function dump() {
            if (cursor() < snapshots().length) {
                dock(cursor())
            }
            var snapshot = { entry: dataModel.entry,
                             view: uiModel.navigationStack.dump(),
                             toDestroy: {} }
            constructors.forEach(function (item) {
                snapshot.toDestroy[item.name] = item.shredder;
            });
            snapshots.push(ko.toJSON(snapshot));
            cursor(cursor() + 1);
        }

        function wait() {
            clearTimeout(dump.timeoutID);
            dump.timeoutID = setTimeout(dump, 1000);
        }

        function mayNotUndo() {
            return cursor() < 2;
        }

        function mayNotRedo() {
            return snapshots().length === cursor();
        }

        function redo() {
            if (! mayNotRedo()) {
                var n = cursor();
                load(n, n);
                cursor(n + 1);
            }
        }

        function undo() {
            if (! mayNotUndo()) {
                var n = cursor() - 2;
                load(n, n + 1);
                cursor(n + 1);
            }
        }

        function clear() {
            cursor(0);
            snapshots.removeAll();
            localStorage.removeItem(snapshotsKey);
            localStorage.removeItem(cursorKey);
        }

        function resumePreviousSession() {
            // Если в локальном хранилище что-то осталось, предлагает
            // пользователю восстанавливить предыдущаю сессию правки статьи.
            // В противном случае молча начинает новую сессию.
            var prevSnapshots = JSON.parse(localStorage.getItem(snapshotsKey)),
                prevCursor = JSON.parse(localStorage.getItem(cursorKey));
            // TODO: здесь должно выводиться предложение пользователю
            // восстановить предыдущую сессию, если от неё остались данные.
        }

        function init() {
            // TODO: Здесь должна быть обработка случаев, когда страницу
            // изменения покинули не должным образом и в локальном хранилище
            // что-то осталось.  Пользователю надо предложить восстановить
            // последнее созданное им состояние для тех статей, которые не были
            // должным образом сохранены.
            resumePreviousSession();

            snapshots.subscribe(function () {
                localStorage.setItem(snapshotsKey, JSON.stringify(snapshots()));
            });

            cursor.subscribe(function (newValue) {
                localStorage.setItem(cursorKey, newValue);
            });

            clear();
            dump();
            argus.guard();
        }

        uS = {
            shouldDisableRedo: ko.computed(mayNotRedo),
            shouldDisableUndo: ko.computed(mayNotUndo),
            redo: redo,
            undo: undo,
            clear: clear,
        };

        init();

        return uS;
    })();

    uiModel.nAdjV = ko.pureComputed(function () {
        return (dataModel.entry
            .part_of_speech.label().match(/^(сущ|прил|гл)\.$/));
    });

    ko.applyBindings(viewModel, $('body').get(0));

    // Инициализация ZeroClipboard и Opentip для кнопки копирования
    // AntConc-запроса.
    var copyButton = $('#copy_antconc_query'),
        clip = new ZeroClipboard(copyButton),
        tip = new Opentip(copyButton,
                    'Запрос для AntConc скопирован в буфер обмена.',
                    { target: true, tipJoint: 'bottom center',
                      removeElementsOnHide: true, hideEffectDuration: 2.5,
                      stemLength: 12, stemBase: 15,
                      background: 'rgb(252, 243, 208)',
                      borderColor: 'rgb(232, 213, 178)'});
    clip.on('dataRequested', function (client, args) {
        client.setText(dataModel.entry.antconc_query());
        tip.show();
        tip.hide();
    });

    // Поднять занавес
    $('.curtain').fadeOut();

})()


} catch(e) {
    $.post('/entries/jserror/',
           {entryId: vM.dataToInitialize.entry.id || 'unknown',
            errorObj: e,
            userAgent: window.navigator.userAgent});
    throw e;
}
