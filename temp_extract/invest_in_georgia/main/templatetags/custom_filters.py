from django import template
from django.utils import translation
import random

register = template.Library()

@register.filter
def in_amenities_list(value, amenities):
    amenities_list = amenities.split(',')
    return value in amenities_list


@register.filter
def get_item(dictionary, key):
    """Gets the value for a key from a dictionary."""
    return dictionary.get(key)

@register.filter
def replace(value, args):
    """Replace a substring with a new substring."""
    try:
        old, new = args.split(',')
        return value.replace(old, new)
    except ValueError:
        return value
    
    
@register.filter
def get_icon(amenity_name, icons_dict):
    # Clean up the amenity name (replace spaces with underscores and convert to lowercase)
    cleaned_name = amenity_name.replace(" ", "_").lower()
    # Return the corresponding icon, or a default if not found
    return icons_dict.get(cleaned_name, "default_icon")  #



@register.filter
def get_subdomain(value):
    """Extract subdomain from the full host"""
    # Ensure there's a host value, and split it
    if value:
        return value.split('.')[0]
    return value


@register.filter
def split(value, delimiter="."):
    """Splits a string by the given delimiter and returns a list."""
    return value.split(delimiter) if value else []

@register.filter
def translate_property(obj, field):
    lang = translation.get_language()
    
    # try to get translation
    value = ''
    if hasattr(obj, 'get_translation'):
        value = obj.get_translation(field, lang)

    # fallback to original field if no translation
    if not value:
        value = getattr(obj, field, '')
    
    return value
@register.filter
def split(value, separator=","):
    """
    Splits a string by the given separator.
    Usage: {{ value|split:"," }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(separator)]


@register.filter
def dict_get(d, key):
    """Get a value from dictionary safely."""
    return d.get(key, "")


@register.filter
def lstrip_slash(value):
    """Remove leading slash from string."""
    if isinstance(value, str):
        return value.lstrip('/')
    return value