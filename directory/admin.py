# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.directory.models import (
    
    PartOfSpeech,
    Gender,
    Tantum,
    Onym,

)

admin.site.register(PartOfSpeech)
admin.site.register(Gender)
admin.site.register(Tantum)
admin.site.register(Onym)
