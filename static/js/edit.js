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
