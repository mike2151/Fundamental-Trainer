
from django import template

register = template.Library()

@register.filter
def url_to_str(value):
    return value.replace("_"," ").title()
