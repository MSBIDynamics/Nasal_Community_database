from django import template

register = template.Library()

@register.filter
def join_and_truncate(values, limit):
    """Join values with comma then truncate after limit words."""
    text = ", ".join(str(v) for v in values)
    words = text.split()
    limit = int(limit)

    if len(words) <= limit:
        return text

    return " ".join(words[:limit]) + "..."

@register.filter
def truncate(value, limit = 20):
    """Join values with comma then truncate after limit words."""
    if not value:
        return value
    value = str(value)
    return value if len(value) <= limit else value[:limit] + "..."
