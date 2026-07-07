from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """Dict lookup by a variable key, e.g. {{ my_dict|get_item:some_id }}."""
    if not mapping:
        return 0
    return mapping.get(key, 0)