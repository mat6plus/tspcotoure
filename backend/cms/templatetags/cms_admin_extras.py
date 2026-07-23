import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def split(value, delimiter=','):
    return [item.strip() for item in re.split(delimiter, value) if item.strip()]
