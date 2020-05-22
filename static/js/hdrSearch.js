function Item(item, focused) {

    this.headword = item.headword;
    this.hom = item.hom || '';
    this.pos = item.pos || '';
    this.hint = item.hint || '';
    this.url = item.url;

    this.focusMe = function(){
        focused(this);
    }.bind(this);

    this.isFocused = ko.computed(
        function(){ return focused() === this; },
        this
    );
}

if (!vM) var vM = {};
vM.hdrSearch = {
    searchPrefix: ko.observable(),
    foundItems: ko.observableArray(),
    focusedItem: ko.observable(),
    formSubmit: function(){ $('.headerForm').submit(); }
};

vM.hdrSearch.moveFocusDown = function() {
    var items = this.foundItems();
    var arrLength = items.length;
    var currentItem = this.focusedItem();
    var index = 0;
    if (currentItem) {
        index = ko.utils.arrayIndexOf(items, currentItem);
        index = index > (arrLength - 2) ? 0 : ++index;
    }
    items[index].focusMe();
}.bind(vM.hdrSearch);

vM.hdrSearch.moveFocusUp = function() {
    var items = this.foundItems();
    var arrLength = items.length;
    var currentItem = this.focusedItem();
    var index = arrLength - 1;
    if (currentItem) {
        index = ko.utils.arrayIndexOf(items, currentItem);
        index = index < 1 ? arrLength - 1 : --index;
    }
    items[index].focusMe();
}.bind(vM.hdrSearch);

vM.hdrSearch.go = function(item) {
    window.location.href = item.url;
};

vM.hdrSearch.flushItems = function() {
    this.foundItems.splice(0);
    this.focusedItem(null);
}.bind(vM.hdrSearch);

vM.hdrSearch.navigateFoundItems = function(vM, event) {
    if (event.which == 40) { // down arrow key
        vM.moveFocusDown();
    } else if (event.which == 38) { // up arrow key
        vM.moveFocusUp();
    } else if (event.which == 13) { // enter key
        if (vM.focusedItem()) vM.go(vM.focusedItem());
        else vM.formSubmit();
    } else if (event.which == 27) { // esc key
        vM.foundItems.splice(0);
    } else {
        return true;
    }
};

vM.hdrSearch.searchPrefix.subscribe(function(newValue) {
    if (/^[а-яА-Я]+$/.test(newValue)) {
        var dataToSend = { find: newValue, auth: 0 };
        if (this.lastItemsRequest) { this.lastItemsRequest.abort(); }
        this.lastItemsRequest = $.getJSON(
            "/json/singleselect/entries/urls/",
            dataToSend,
            function(data){
                var mappedData = ko.utils.arrayMap(
                    data,
                    function(item){ return new Item(item, vM.hdrSearch.focusedItem); }
                );
                vM.hdrSearch.foundItems(mappedData);
                if (vM.hdrSearch.foundItems().length==1) {
                    vM.hdrSearch.foundItems()[0].focusMe();
                }
            }
        );
    } else {
        this.flushItems();
    }
}, vM.hdrSearch);

ko.applyBindings(vM.hdrSearch, $('.header').get(0));
