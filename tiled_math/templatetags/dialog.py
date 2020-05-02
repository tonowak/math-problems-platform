import datetime
import ast
from django import template

register = template.Library()

@register.inclusion_tag('redirect_dialog.html')
def dialog(title, url, method, form_values, yes, no, button_id):
    return {
        'title': title,
        'url': url,
        'yes': yes,
        'no': no,
        'button_id': button_id,
        'method': method,
        'form_values': ast.literal_eval(form_values),
    }

