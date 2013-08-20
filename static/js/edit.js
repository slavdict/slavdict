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
function Etymology(entry, collocation, etymonTo, data) {
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
    if (!Etymology.idMap.hasOwnProperty(this.id())) {
        Etymology.counter++;
        Etymology.idMap[this.id()] = this;
    }
}
Etymology.counter = 0;
Etymology.idMap = {};
