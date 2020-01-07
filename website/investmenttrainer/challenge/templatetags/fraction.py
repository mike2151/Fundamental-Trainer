
from django import template

register = template.Library()

@register.filter
def fraction(a,b):
    return int((a / (a+b)) * 100)
