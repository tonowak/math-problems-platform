import datetime
import ast
from django import template

register = template.Library()

@register.inclusion_tag('files/preview_image.html')
def preview_image(f):
    return {'file': f}

