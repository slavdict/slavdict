function snapshotObservable(value) {
    return ko.observable(value).publishOn('entry change');
}

function upsert(object, attrname, data, defaultValue, observable) {
    // Upsert property ``attrname`` in the ``object``
    var value = data && data[attrname] || defaultValue;
    observable = observable || snapshotObservable;
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

function Orthvar(entry, data) {
    upsert(this, 'idem', data, '');
    upsert(this, 'order', data, 345);
    upsert(this, 'entry_id', data, entry.id());
    upsert(this, 'id', data, 'orthvar' + Orthvar.counter);
    Orthvar.counter++;
}
Orthvar.counter = 0;

function Collocation(collogroup, data) {
    upsert(this, 'civil_equivalent', data, '');
    upsert(this, 'collocation', data, '');
    upsert(this, 'collogroup_id', data, collogroup.id());
    upsert(this, 'id', data, 'collocation' + Collocation.counter);
    upsert(this, 'order', data, 345);
    Collocation.counter++;
}
Collocation.counter = 0;

function Context(meaning, data) {
    upsert(this, 'context', data, '');
    upsert(this, 'id', data, 'context' + Context.counter);
    upsert(this, 'left_text', data, '');
    upsert(this, 'meaning_id', data, meaning.id());
    upsert(this, 'order', data, 345);
    upsert(this, 'right_text', data, '');
    Context.counter++;
}
Context.counter = 0;

function Greq(example, data) {
    upsert(this, 'additional_info', data, '');
    upsert(this, 'corrupted', data, false);
    upsert(this, 'for_example_id', data, example.id());
    upsert(this, 'id', data, 'greq' + Greq.counter);
    upsert(this, 'initial_form', data, '');
    upsert(this, 'mark', data, '');
    upsert(this, 'position', data, 0);
    upsert(this, 'source', data, '');
    upsert(this, 'unitext', data, '');
    Greq.counter++;
}
Greq.counter = 0;
