from django import template
from django.utils import timezone

from store.utils import format_money, gregorian_to_jalali, to_persian_digits

register = template.Library()


@register.filter
def fa(value):
    """Convert Latin digits to Persian digits."""
    return to_persian_digits(value)


@register.filter
def money(value):
    """1234000 -> ۱٬۲۳۴٬۰۰۰"""
    return format_money(value)


@register.filter
def jalali(value, with_time=False):
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
    result = f"{jy:04d}/{jm:02d}/{jd:02d}"
    if with_time:
        result += f" - {value.hour:02d}:{value.minute:02d}"
    return to_persian_digits(result)


@register.filter
def stars(value):
    """Render a 0-5 rating as filled/empty star characters."""
    try:
        rating = float(value)
    except (TypeError, ValueError):
        rating = 0
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full)


@register.simple_tag
def current_jalali_year():
    today = timezone.localdate()
    jy, _, _ = gregorian_to_jalali(today.year, today.month, today.day)
    return to_persian_digits(jy)
