from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('analytics.html')
def analytics():
    analytics_enabled = settings.PRODUCTION
    print(analytics_enabled)
    return {
        'analytics_enabled': analytics_enabled,
    }

