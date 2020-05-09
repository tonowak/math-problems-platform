import datetime
import ast
from django import template

register = template.Library()

@register.inclusion_tag('problems/answer_element.html')
def answer_element(a, b, c, d):
    return {
        'a': a,
        'b': b,
        'c': c,
        'd': d,
    }

