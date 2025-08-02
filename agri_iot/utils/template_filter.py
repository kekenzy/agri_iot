from django import template

register = template.Library()

@register.filter
def filesizeformat_bytes(value):
    try:
        value = int(value)
        if value < 1024:
            return f"{value} B"
        elif value < 1024 ** 2:
            return f"{value / 1024:.2f} KB"
        elif value < 1024 ** 3:
            return f"{value / 1024 ** 2:.2f} MB"
        else:
            return f"{value / 1024 ** 3:.2f} GB"
    except (ValueError, TypeError):
        return "0 B"
