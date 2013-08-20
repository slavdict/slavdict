function snapshotObservable(value) {
    return ko.observable(value).publishOn('entry change');
}
