from django import template

register = template.Library()


@register.filter
def espace_milliers(value):
    """Formate un nombre avec des espaces comme separateurs de milliers (ex: 980000 -> '980 000')."""
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return value

    return f"{number:,}".replace(",", " ")
