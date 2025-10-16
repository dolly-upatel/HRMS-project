from django import template
from datetime import datetime

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mod(value, arg):
    """Modulo operation"""
    try:
        return float(value) % float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def calculate_working_hours(attendance):
    """Calculate working hours for an attendance record"""
    if not attendance.check_in or not attendance.check_out:
        return "--"
    
    try:
        # Convert times to minutes since midnight
        check_in_minutes = attendance.check_in.hour * 60 + attendance.check_in.minute
        check_out_minutes = attendance.check_out.hour * 60 + attendance.check_out.minute
        
        total_minutes = check_out_minutes - check_in_minutes
        
        if total_minutes <= 0:
            return "--"
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
            
    except (AttributeError, TypeError):
        return "--"