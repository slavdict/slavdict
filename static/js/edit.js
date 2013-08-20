var topic = 'entry change';

function snapshotObservable(observable) {
    observable = observable || ko.observable;
    return function () {
        return observable.apply(null, arguments).publishOn(topic);
    }
}

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
    if (!Etymology.idMap.hasOwnProperty(this.id())) {
        Etymology.counter++;
        Etymology.idMap[this.id()] = this;
    }
}
Etymology.counter = 0;
Etymology.idMap = {};

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
    upsert(this, 'id', data, 'participle' + Participle.counter);
    Participle.counter++;
}
Participle.counter = 0;

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
    upsert(this, 'id', data, 'orthvar' + Orthvar.counter);
    Orthvar.counter++;
}
Orthvar.counter = 0;

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
    upsert(this, 'id', data, 'collocation' + Collocation.counter);
    upsert(this, 'order', data, 345);
    Collocation.counter++;
}
Collocation.counter = 0;

function Context() {
    /* Context(meaning)
     * Context(data)
     */
    var data = {},
        meaning_id = null;

    if (arguments[0] instanceof Meaning) meaning_id = arguments[0].id();
    else data = arguments[0];

    upsert(this, 'context', data, '');
    upsert(this, 'id', data, 'context' + Context.counter);
    upsert(this, 'left_text', data, '');
    upsert(this, 'meaning_id', data, meaning_id);
    upsert(this, 'order', data, 345);
    upsert(this, 'right_text', data, '');
    Context.counter++;
}
Context.counter = 0;

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
    upsert(this, 'id', data, 'greq' + Greq.counter);
    upsert(this, 'initial_form', data, '');
    upsert(this, 'mark', data, '');
    upsert(this, 'position', data, 0);
    upsert(this, 'source', data, '');
    upsert(this, 'unitext', data, '');
    Greq.counter++;
}
Greq.counter = 0;

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
    upsert(this, 'id', data, 'example' + Example.counter);
    upsert(this, 'meaning_id', data, meaning_id);
    upsert(this, 'order', data, 345);
    if (!Example.idMap.hasOwnProperty(this.id())) {
        Example.counter++;
        Example.idMap[this.id()] = this;
        Example.all.push(this);
    }
}
Example.counter = 0;
Example.idMap = {};
Example.all = [];
