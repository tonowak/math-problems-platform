import datetime
import ast
from django import template

register = template.Library()

@register.inclusion_tag('tags/submit_button.html')
def submit_button(title, form_id):
    return {
        'title': title,
        'form_id': form_id,
    }

@register.inclusion_tag('tags/textarea.html')
def textarea(title, rows, form_id, name):
    return {
        'title': title,
        'rows': rows,
        'form_id': form_id,
        'name': name,
    }
