from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        result = Decimal(value) * Decimal(arg)
        return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError):
        return ''


@register.filter
def sum_subtotals(order_items):
    total = Decimal('0.00')
    for item in order_items:
        total += item.quantity * item.price_at_purchase
    return total.quantize(Decimal('0.01'))