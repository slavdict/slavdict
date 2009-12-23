# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.directory.models import (
    
    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    Transitivity,
    SyntArgument,
    SubcatFrame,

)

admin.site.register(PartOfSpeech)
admin.site.register(Gender)
admin.site.register(Tantum)
admin.site.register(Onym)
admin.site.register(Transitivity)
admin.site.register(SyntArgument)
admin.site.register(SubcatFrame)
