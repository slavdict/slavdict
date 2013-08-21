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
        upsertArray(object, attrname, Constructor, data, observableArray);
    } else {
        crudArrayItems(object[attrname], spec, Constructor);
    }
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

    if (arguments.length > 1 && !data) {
        meaning_id = arguments[1];
    } else {
        throw new Error('Неправильный состав аргументов для Meaning.');
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
            tune(item);
        }
    }

    function remove(item) {
        var index = this.indexOf(item);
        if (index >= 0) {
            this.splice(index, 1);
        } else {
            throw new Error('Элемент ' + item.prototype.constructor.name +
                            ' обязан присутствовать в массиве.');
        }
        delete this.idMap[item.id()];
    }

    function tune(item) {
        var tuner = {

            Collogroup: function (cg) {
                cg.meanings.subscribe(function (changedArray) {
                    var i = 1;
                    ko.utils.arrayForEach(changedArray, function (item) {
                        item.parent_meaning_id(null);
                        item.entry_container_id(null);
                        item.collogroup_container_id(cg.id());
                        if (! item._destroy) {
                            item.order(i);
                            i += 1;
                        }
                    });
                });
                cg.meanings.notifySubscribers(cg.meanings());
                cg.isExpanded = cg.isExpanded || ko.observable(false);
            },

            Meaning: function(m) {
                m.meanings.subscribe(function (changedArray) {
                   var i = 1;
                   ko.utils.arrayForEach(changedArray, function (item) {
                      item.parent_meaning_id(m.id());
                      item.entry_container_id(m.entry_container_id());
                      item.collogroup_container_id(m.collogroup_container_id());
                      if (! item._destroy) {
                         item.order(i);
                         i += 1;
                      }
                   });
                });

                m.examples.subscribe(function (changedArray) {
                    var i = 1;
                    ko.utils.arrayForEach(changedArray, function (item) {
                        item.meaning_id(m.id());
                        item.collogroup_id(m.collogroup_container_id());
                        if (! item._destroy) {
                            item.order(i);
                            i += 1;
                        }
                    });
                });

                m.collogroups.subscribe(function (changedArray) {
                    var i = 1;
                    ko.utils.arrayForEach(changedArray, function (item) {
                        if (! item._destroy) {
                            item.order(i);
                            i += 1;
                        }
                    });
                });
                m.collogroups.notifySubscribers(m.collogroups());
                m.isExpanded = m.isExpanded || ko.observable(false);
            }

        }[item.prototype.constructor];
        tuner && tuner(item);
    }

    for (i = constructors.length; i--;) {
        Constructor = constructors[i];
        Constructor.all = [];
        Constructor.all.idMap = {};
        Constructor.all.doesNtContain = doesNtContain;
        Constructor.all.append = append;
        Constructor.all.remove = remove;
    }

    function toggle() { this.isExpanded(!this.isExpanded()); }
    Collogroup.prototype.toggle = toggle;
    Meaning.prototype.toggle = toggle;

})()
