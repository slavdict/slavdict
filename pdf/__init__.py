# -*- coding: utf-8 -*-
from django import http
from django.template.loader import render_to_string
from django.template import RequestContext
import ho.pisa as pisa
import cStringIO as StringIO
from django.conf import settings

def write_pdf(request, template_src, context_dict):
    html  = render_to_string(template_src, context_dict, RequestContext(request))
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(
        StringIO.StringIO(html.encode('UTF-8')),
        result,
        path=settings.STATIC_ROOT + 'stub')
        # Аргумент path внутренне используется следующим образом.
        # pisaDocument преполагает, что это тот путь, по которому должен был
        # быть расположен наш html-файл. На основе этого пути вычисляется
        # путь объемлющей директории. И он принимается за отправную точку
        # для вычисления относительных ссылок в файле. В данном случае
        # строчка 'stub' в `path = settings.STATIC_ROOT + 'stub'` используется
        # только для того, чтобы она была отсечена и чтобы в качестве отправной
        # директории использовался путь settings.STATIC_ROOT.
    if not pdf.err:
        response = http.HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s' % context_dict['filename']
        return response
    return http.HttpResponseRedirect('/')