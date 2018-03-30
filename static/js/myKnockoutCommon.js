ko.observable.fn['htmlSelect'] = function(fieldName, objList){
    this.list = ko.observableArray(objList);
    this.obj = ko.computed(function(){ return this.index2obj(this()); }, this);
    $('#id_' + fieldName).attr('data-bind',
        'options: ' + fieldName + '.list, ' +
        'value: ' + fieldName + ', ' +
        'optionsText: "name", ' +
        'optionsValue: "id"');
    return this;
};

ko.observable.fn['htmlCheckbox'] = function(name){
    var x = $('#id_' + name),
        n = x.next('label[for="id_' + name + '"]').detach(),
        p = x.prev('label[for="id_' + name + '"]').detach();
    x.attr('data-bind', 'checked: ' + name)
        .wrap('<div class="checkbox-group for_id_' + name + '">' +
            '<div class="checkbox for_id_' + name + '" /></div>')
        .parent().after(n).before(p);
    return this;
};

ko.observable.fn['htmlTextInput'] = function(name){
    $('#id_' + name)
        .attr('data-bind', 'textInput: ' + name)
        .attr('autocomplete', 'off')
        .attr('spellcheck', 'false')
        .wrap('<div class="textinput for_id_' + name + '"/>');
    return this;
};

ko.observable.fn['htmlTextValue'] = function(name){
    $('#id_' + name)
        .attr('data-bind', 'value: ' + name)
        .attr('autocomplete', 'off')
        .attr('spellcheck', 'false')
        .wrap('<div class="textinput for_id_' + name + '"/>');
    return this;
};

ko.observable.fn['index2obj'] = function(value){
    var representer = function(item){ return item.id; },
        arr = ko.utils.arrayMap(this.list(), representer),
        index = ko.utils.arrayIndexOf(arr, value);
    if (index < 0){
        console.log('Object list: ', this.list());
        console.log('Array: ', arr);
        console.log('Value to find in the array: ', value);
        throw new Error('Элемент в массиве не найден.');
    }
    return this.list()[index];
};

ko.observable.fn['rememberDefault'] = function(defaultValue){
    this.defaultValue = defaultValue;
    this.getDefaultValue = function(){
        if (vM.filters && vM.filters.showResetAll) {
            vM.filters.showResetAll(true);
        }
        this(this.defaultValue);
        return this;
    };
    this.hasDefaultValue = function(){ return this() === this.defaultValue; };
    vM.meta.defaults.push(this);

    this.subscribe(function(value){
        if (vM.filters && vM.filters.showResetAll && value !== defaultValue) {
            vM.filters.showResetAll(false);
        }
    }, this);

    return this;
};

ko.observable.fn['rememberInitial'] = function(initial){
    this.initialValue = initial;
    this.getInitialValue = function(){ this(this.initialValue); return this; };
    this.hasInitialValue = function(){ return this() === this.initialValue; };
    vM.meta.initials.push(this);
    return this.getInitialValue();
};

ko.bindingHandlers.slide = {
    update: function(element, valueAccessor){
        if (ko.utils.unwrapObservable(valueAccessor())){
            $(element).slideDown();
        } else {
            $(element).slideUp();
        }
    }
};

ko.bindingHandlers.show = {
    update: function(element, valueAccessor){
        if (ko.utils.unwrapObservable(valueAccessor())){
            $(element).show();
        } else {
            $(element).hide();
        }
    }
};

function getCaretPosition(element) {
    var caretPos = 0, sel, range;
    if (window.getSelection) {
        sel = window.getSelection();
        if (sel.rangeCount) {
            range = sel.getRangeAt(0);
            if (range.commonAncestorContainer.parentNode == element) {
                caretPos = range.endOffset;
            }
        }
    } else if (document.selection && document.selection.createRange) {
        range = document.selection.createRange();
        if (range.parentElement() == element) {
            var tempEl = document.createElement("span");
            element.insertBefore(tempEl, element.firstChild);
            var tempRange = range.duplicate();
            tempRange.moveToElementText(tempEl);
            tempRange.setEndPoint("EndToEnd", range);
            caretPos = tempRange.text.length;
        }
    }
    return caretPos;
}

function setCaretPosition(element, caretPos) {
    var textNode = element.firstChild;
    if (textNode === null) {
        return;
    }
    var range = document.createRange(),
        sel;
    range.setStart(textNode, caretPos);
    range.setEnd(textNode, caretPos);
    sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}

ko.bindingHandlers.contenteditable = {
    init: function (element, valueAccessor) {
        var observable = valueAccessor(),
            $element = $(element);
        $element.attr('contenteditable', 'true')
        $element.on('input cut paste drag dragdrop', function() {
            var cursorPos = getCaretPosition(element);
            $element.attr('data-cursor-position', cursorPos);
            observable($element.text());
            $element.trigger('change');
        });
    },
    update: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor()),
            $element = $(element);
        if ((value === null) || (value === undefined)) {
            value = "";
        }
        $element.html(value);
        setCaretPosition(element, $element.attr('data-cursor-position') || 0);
    }
};

ko.bindingHandlers.visibleFocus = {
    update: function(element, valueAccessor){
        if (ko.utils.unwrapObservable(valueAccessor())){
            $(element).show().focus();
        } else {
            $(element).hide();
        }
    }
};
