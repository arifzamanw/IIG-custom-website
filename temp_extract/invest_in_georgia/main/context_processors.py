"""
main/context_processors.py

Custom template context processors for the Invest In Georgia platform.
Each function is registered in settings.py under TEMPLATES > context_processors
and injects variables into every template automatically.
"""

from django.utils import translation
from django.conf import settings

from .models import SEO


def seo(request):
    """
    Inject an SEO object into every template based on the current URL name.

    Looks up the SEO entry whose page_key matches the resolved URL name
    (e.g. 'home', 'property_search'). Falls back to the 'default' entry
    if no match is found, or returns None if neither exists.

    Context variable: `seo`
    """
    page_key = None

    if hasattr(request, 'resolver_match') and request.resolver_match:
        page_key = request.resolver_match.url_name

    seo_obj = None
    if page_key:
        seo_obj = SEO.objects.filter(page_key=page_key).first()

    if not seo_obj:
        seo_obj = SEO.objects.filter(page_key='default').first()

    return {'seo': seo_obj}


def language_code(request):
    """
    Inject the current active language code and flag map into every template.

    Context variables:
        `LANGUAGE_CODE` — active language (e.g. 'en', 'ar')
        `FLAG_MAP`      — dict mapping language codes to flag identifiers
    """
    return {
        'LANGUAGE_CODE': translation.get_language(),
        'FLAG_MAP':      settings.FLAG_MAP,
    }


def href_lang_map(request):
    """
    Inject the hreflang map into every template (used in <head> alternate tags).

    Context variable: `HREFLANG_MAP`
    """
    return {
        'HREFLANG_MAP': settings.HREFLANG_MAP,
    }


def flag_data(request):
    """
    Inject the flag CDN map into every template.

    Context variable: `FLAG_CDN`
    """
    return {
        'FLAG_CDN': settings.FLAG_CDN,
    }