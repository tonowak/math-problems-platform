import datetime
import ast
from django import template

register = template.Library()

@register.inclusion_tag('redirect_button.html')
def redirect_button(url, title, *args, **kwargs):
    return {
        'url': url,
        'title': title,
        'color': kwargs['color'] if 'color' in kwargs else '',
        'method': kwargs['method'] if 'method' in kwargs else 'get',
        'form_id' : kwargs['form_id'] if 'form_id' in kwargs else '',
    }

