var topic = 'entry change',
    constructors = [Etymology, Participle, Orthvar,
                    Collocation, Context, Greq,
                    Example, Collogroup, Meaning,
                    Entry];

// Функция создающая датчики, оповещающие о том, что словарная статья
// изменилась.
function snapshotObservable(observable) {
    observable = observable || ko.observable;
    return function () {
        return observable.apply(null, arguments).publishOn(topic);
    }
}

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
        var args = [0, voodoo().length].concat(spec);
        Array.prototype.splice.apply(voodoo, args);
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
        if (all[id]) {
            Constructor.call(all[id], specItem);
            object = all[id];
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

    var spec = data[attrname] || [];
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

// Общие для всех свойств-массивов методы добавления/удаления элментов
function itemAdder(args) {
    var item, array = this;
    return {
      do: function () {
        args = [null].concat(args || []);
        item = new (Function.prototype.bind.apply(array.itemConstructor, args));
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
                array.destroy(item);
            } else {
                array.remove(item);
                array.itemConstructor.all.remove(item);
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
        // FIX: Впоследствии Collogroup должно исчезнуть
        // и быть заменено на Collocation. Словосочетания должны также,
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
    upsert(this, 'position', data, 0);
    upsert(this, 'source', data, '');
    upsert(this, 'unitext', data, '');
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
    upsert(this, 'greek_eq_status', data, '');
    upsertArray(this, 'greqs', Greq, data);
    upsert(this, 'hidden', data, false);
    upsert(this, 'id', data, 'example' + Example.all.length);
    upsert(this, 'meaning_id', data, meaning_id);
    upsert(this, 'order', data, 345);
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

    upsertArray(this, 'collocations', Collocation, data);
    upsert(this, 'base_entry_id', data, entry_id);
    upsert(this, 'base_meaning_id', data, meaning_id);
    upsert(this, 'id', data, 'collogroup' + Collogroup.all.length);
    upsert(this, 'order', data, 345);
    upsertArray(this, 'meanings', Meaning, data);
    upsertArray(this, 'unsorted_examples', Example, data);
    upsertArray(this, 'etymologies', Etymology, data);

    this.isExpanded || (this.isExpanded = ko.observable(false));
    Collogroup.all.append(this);
}

function Meaning() {
    /* Meaning(container[, parentMeaning])
     * Meaning(data)
     */
    var data = {},
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
            meaning_id = arguments[1];
        }
    }

    upsert(this, 'meaning', data, '');
    upsert(this, 'gloss', data, '');
    upsert(this, 'metaphorical', data, false);
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
    Meaning.all.append(this);
}

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
}

// Гаранты свойств элементов разных списков.
function guarantor(array, func) {
    array.subscribe(function (changedArray) {
        changedArray.forEach(func);
    }).callback(array());
}

function orderGuarantor(object, attrname) {
    guarantor(object[attrname], function (item, index) {
        item.order(index);
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
                item.order(index); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

function meaningsGuarantor(object, attrname) {
    var func = {

            'Entry': function (item, index) {
                item.parent_meaning_id(null);
                item.entry_container_id(object.id());
                item.collogroup_container_id(null);
                item.order(index); },

            'Collogroup': function (item, index) {
                item.parent_meaning_id(null);
                item.entry_container_id(null);
                item.collogroup_container_id(object.id());
                item.order(index); },

            'Meaning': function (item, index) {
                item.parent_meaning_id(object.id());
                item.entry_container_id(object.entry_container_id());
                item.collogroup_container_id(object.collogroup_container_id());
                item.order(index); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

function collogroupsGuarantor(object, attrname) {
    var func = {

            'Meaning': function (item, index) {
                item.base_entry_id(null);
                item.base_meaning_id(object.id());
                item.order(index); },

            'Entry': function (item, index) {
                item.base_entry_id(object.id());
                item.base_meaning_id(null);
                item.order(index); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

function etymologiesGuarantor(object, attrname) {
    var func = {

            'Etymology': function (item, index) {
                item.entry_id(null);
                item.collocation_id(null);
                item.etymon_to_id(object.id());
                item.order(index); },

            'Collogroup': function (item, index) {
                item.entry_id(null);
                item.collocation_id(object.id());
                item.etymon_to_id(null);
                item.order(index); },

            'Entry': function (item, index) {
                item.entry_id(object.id());
                item.collocation_id(null);
                item.etymon_to_id(null);
                item.order(index); }

        }[object.constructor.name];

    guarantor(object[attrname], func);
}

// Дополнительная однократная настройка конструкторов
(function () {
    var i, Constructor;

    function doesNtContain(item) {
        return !this.idMap[item.id()];
    }

    function append(item) {
        if (this.doesNtContain(item)) {
            this.push(item);
            this.idMap[item.id()] = item;
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

    function editItem() { this.constructor.itemBeingEdited(this); }
    function stopEditing() { this.constructor.itemBeingEdited(null); }

    for (i = constructors.length; i--;) {
        Constructor = constructors[i];
        Constructor.all = [];
        Constructor.all.idMap = {};
        Constructor.all.doesNtContain = doesNtContain;
        Constructor.all.append = append;
        Constructor.all.remove = remove;
        Constructor.bag = [];
        Constructor.bag.idMap = {};
        Constructor.itemBeingEdited = ko.observable(null);
        Constructor.prototype.edit = editItem;
        Constructor.prototype.stopEditing = stopEditing;
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
    var i, j,
        meaning,
        etymology,
        collogroup,
        example;

    function buildObjects(dataArray, Constructor) {
        for (var i = 0, j = dataArray.length; i < j; i++) {
            new Constructor(dataArray[i]);
        }
    }

    // Строим объекты вуду-модели
    dataModel.entry = new Entry(vM.dataToInitialize.entry.entry);
    buildObjects(vM.dataToInitialize.entry.etymologies, Etymology);
    buildObjects(vM.dataToInitialize.entry.collogroups, Collogroup);
    buildObjects(vM.dataToInitialize.entry.meanings, Meaning);
    buildObjects(vM.dataToInitialize.entry.examples, Example);

    // Сортируем значения, прикрепляя их к нужным значениям, словосочетаниями
    // или лексемам.
    for (i = 0, j = Meaning.all.length; i < j; i++) {
        meaning = Meaning.all[i];
        // У meaning возможны следующие сочетания значений полей
        // entry_container_id (E), collogroup_container_id (C)
        // и parent_meaning_id (M):
        //
        //      E, C, EM, CM.
        //
        // Присутствие буквы означает, что соотвествующее поле имеет
        // значение отличное от null.
        if (meaning.parent_meaning_id() !== null) {
            Meaning.all.idMap[meaning.parent_meaning_id()]
                .meanings.push(meaning);
        } else {
            if (meaning.collogroup_container_id() !== null) {
                Collogroup.all.idMap[meaning.collogroup_container_id()]
                    .meanings.push(meaning);
            } else {
                dataModel.entry.meanings.push(meaning);
            }
        }
    }

    // Сортируем этимоны.
    for (i = 0, j = Etymology.all.length; i < j; i++) {
        etymology = Etymology.all[i];
        // У etymology возможны следующие сочетания значений полей
        // entry_id (E), collocation_id (C) и etymon_to_id (e):
        //
        //      E, C, Ee, Ce.
        //
        // Присутствие буквы обозначает, что соответствующее поле имеет
        // значение отличное от null.
        if (etymology.etymon_to_id() !== null) {
            Etymology.all.idMap[etymology.id()].etymologies.push(etymology);
        } else {
            if (etymology.collocation_id() !== null) {
                Collogroup.all.idMap[etymology.collocation_id()]
                    .etymologies.push(etymology);
            } else {
                dataModel.entry.etymologies.push(etymology);
            }
        }
    }

    // Сортируем словосочетания.
    for (i = 0, j = Collogroup.all.length; i < j; i++) {
        collogroup = Collogroup.all[i];
        // У collogroup возможны следующие сочетания значений полей
        // base_entry_id (E) и base_meaning_id (M):
        //
        //      E, M.
        //
        // Присутствие буквы обозначает, что соответствующее поле имеет
        // значение отличное от null.
        if (collogroup.base_meaning_id() !== null) {
                Meaning.all.idMap[collogroup.base_meaning_id()]
                    .collogroups.push(collogroup);
        } else {
            dataModel.entry.collogroups.push(collogroup);
        }
    }

    // Сортируем примеры.
    for (i = 0, j = Example.all.length; i < j; i++) {
        example = Example.all[i];
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
        if (example.meaning_id() !== null) {
            Meaning.all.idMap[example.meaning_id()].examples.push(example);
        } else {
            if (example.collogroup_id() !== null) {
                Collogroup.all.idMap[example.collogroup_id()]
                    .unsorted_examples.push(example);
            } else {
                dataModel.entry.unsorted_examples.push(example);
            }
        }
    }

    // Добавлям разные датчики второго порядка
    uiEntry.headword = ko.computed({
        read: function () {
            var orthvars = dataModel.entry.orthvars(),
                isNotDestroyed = function (item) { return ! item._destroy; };
            return ko.utils.arrayFilter(orthvars, isNotDestroyed)[0].idem();
        },
        write: function (value) {
            var orthvars = dataModel.entry.orthvars(),
                isNotDestroyed = function (item) { return ! item._destroy; };
            ko.utils.arrayFilter(orthvars, isNotDestroyed)[0].idem(value);
        }
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

    // Активация работы вкладок
    $('nav.tabs li').click(function () {
        $('nav.tabs li.current').removeClass('current');
        $('section.tabcontent.current').removeClass('current');
        var x = $(this);
        x.addClass('current');
        $(x.find('a').attr('href')).addClass('current');
    });

    ko.applyBindings(viewModel, $('#main').get(0));

    // Поднять занавес
    $('.curtain').fadeOut();

})()
