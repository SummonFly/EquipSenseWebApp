# templatetags/querystring.py
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    request = context['request']
    qs = request.GET.copy()
    for k, v in kwargs.items():
        if isinstance(v, (list, tuple)):
            qs.setlist(k, v)
        else:
            qs[k] = v
    return qs.urlencode()
