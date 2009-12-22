# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.directory.models import (
    
    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    SyntActant,
    SubcatFrame,

)

admin.site.register(PartOfSpeech)
admin.site.register(Gender)
admin.site.register(Tantum)
admin.site.register(Onym)
admin.site.register(SyntActant)
admin.site.register(SubcatFrame)
