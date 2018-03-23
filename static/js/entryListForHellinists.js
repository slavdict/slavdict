function EtymologyForJSON(etym) {
    this.id = etym.id;
    this.unitext = etym.unitext;
    this.additional_info = etym.additional_info;
    this.entry_id = etym.entry_id;
}

function Etymology(etym) {

    if (!etym) etym = {};

    this.id = ko.observable(etym.id || '');
    this.unitext = ko.observable(etym.unitext || '');
    this.additional_info = ko.observable(etym.additional_info || '');
    this.entry_id = etym.entry_id;

    this.beingSaved = ko.observable(false);

    this.removeMe = function() {
        if (this.id()) {
            this.beingSaved(true);
            var dataToSend = { 'delete': this.id() }
            $.ajax({
                method: 'POST',
                url: vM.urls.jsonEtymDeleteURL,
                data: dataToSend,
                beforeSend: function (request) {
                    request.setRequestHeader('X-CSRFToken', csrftoken);
                },
                success: function (data) {
                           if (data.action=='deleted') {
                             vM.filters
                                   .etymsForEntries[this.entry_id]
                                   .remove(this);
                           }
                         }.bind(this)
            });
        } else {
            vM.filters.etymsForEntries[this.entry_id].remove(this);
        }
    }.bind(this);

    this.saveMe = function() {
        this.beingSaved(true);
        var dataToSend = { 'etym': ko.toJSON(new EtymologyForJSON(this)) };
        $.ajax({
            method: 'POST',
            url: vM.urls.jsonEtymSaveURL,
            data: dataToSend,
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (data) {
                       if (data.action=='created') {
                         this.id(data.id);
                       }
                       this.beingSaved(false);
                     }.bind(this)
        });
    }.bind(this);
}

(function () {
    var et;
    for (var i = 0; i < vM.jsonEtymologies.length; i++) {
        et = new Etymology(vM.jsonEtymologies[i]);
        vM.filters.etymsForEntries[et.entry_id]().push(et)
    }
    vM.filters.addEtymology = function (entry_id) {
        var data = { entry_id: entry_id },
            et = new Etymology(data);
        vM.filters.etymsForEntries[entry_id].push(et);
    };
})();
