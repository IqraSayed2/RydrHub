# main_app/templatetags/my_custom_filters.py

from django import template
from datetime import datetime
import math

register = template.Library()

@register.filter
def timesince_float(value, arg):
    if not isinstance(value, datetime) or not isinstance(arg, datetime):
        return 0.0 
    
    if value < arg:
        value, arg = arg, value 

    duration = value - arg
    return duration.total_seconds() / (24 * 3600)

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0.0 
    
@register.filter
def floordiv(value, arg):
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0: 
            return 0
        return math.floor(value / arg) 
    except (ValueError, TypeError):
        return 0 