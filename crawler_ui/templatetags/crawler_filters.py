"""Custom template filters for the crawler UI."""
from django import template
import locale

register = template.Library()


@register.filter(name='format_number')
def format_number(value):
    """Format a number with thousands separators (space-separated).
    
    Examples:
        29000 -> "29 000"
        145000 -> "145 000"
        5300 -> "5 300"
    """
    if value is None or value == '':
        return '-'
    try:
        num = int(float(value))
        # Use space as thousands separator (European convention)
        return f'{num:,}'.replace(',', ' ')
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='format_price_bgn')
def format_price_bgn(value):
    """Format a BGN price with thousands separator and currency."""
    if value is None or value == '' or value == 0:
        return '-'
    try:
        num = int(float(value))
        formatted = f'{num:,}'.replace(',', ' ')
        return f'{formatted} лв.'
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='format_price_eur')
def format_price_eur(value):
    """Format a EUR price with thousands separator and currency."""
    if value is None or value == '' or value == 0:
        return '-'
    try:
        num = float(value)
        if num == int(num):
            formatted = f'{int(num):,}'.replace(',', ' ')
        else:
            formatted = f'{num:,.1f}'.replace(',', ' ')
        return f'{formatted} €'
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='format_avg_price')
def format_avg_price(value):
    """Format average price for dashboard metrics (rounded to integer with separators)."""
    if value is None or value == '' or value == 0:
        return 'N/A'
    try:
        num = int(round(float(value)))
        return f'{num:,}'.replace(',', ' ')
    except (ValueError, TypeError):
        return 'N/A'
