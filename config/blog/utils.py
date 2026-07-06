from django.utils.text import slugify
import uuid


def generate_unique_slug(instance, source_value, slug_field_name="slug", max_length=220):
    """
    Build a unique slug for `instance` from `source_value`.

    Reused by Category, Tag and Blog to avoid duplicating the same
    "slugify + collision check" logic in every model's save().
    """
    model_class = instance.__class__
    base_slug = slugify(source_value, allow_unicode=True)[:max_length] or "item"
    slug = base_slug
    queryset = model_class.objects.filter(**{slug_field_name: slug})
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.exists():
        slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        queryset = model_class.objects.filter(**{slug_field_name: slug})
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

    return slug
