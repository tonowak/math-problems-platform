import datetime
from django import template

register = template.Library()

@register.inclusion_tag('selectize.html', takes_context=True)
def select_tags(context, form_id):
    selected_tags = []
    if 'selected_tags' in context:
        selected_tags = context['selected_tags']
    return {
        'all_tags': context['all_tags'],
        'selected_tags': selected_tags,
        'form_id': form_id,
    }

