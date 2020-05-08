import datetime
import ast
from django import template

register = template.Library()

@register.inclusion_tag('redirect_button.html')
def redirect_button(url, title, *args, **kwargs):
    return {
        'url': url,
        'title': title,
        'color': kwargs.get('color', ''),
        'method': kwargs.get('method', 'get'),
        'form_id' : kwargs.get('form_id', ''),
        'no_margin': kwargs.get('no_margin', False),
    }

