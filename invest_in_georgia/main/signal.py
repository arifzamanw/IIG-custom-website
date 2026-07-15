"""
main/signals.py

Django signals for the Invest In Georgia platform.

Responsibilities:
  - Cache invalidation: clears the full cache whenever any
    key model is saved or deleted.
  - Auto-translation: translates text fields into AR/RU/KA
    using Google Translate before saving (currently disabled,
    uncomment the registration block at the bottom to enable).
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from deep_translator import GoogleTranslator

from .models import (
    Team, OverviewKeyBlog, OverviewKeySection,
    FeaturedPropertySection, MarketinsightSection,
    WhoWeArePage, Amenity, BlogPost, City, Property,
)


# ─────────────────────────────────────────────────────────────────────────────
# Cache invalidation
# ─────────────────────────────────────────────────────────────────────────────

# Models whose changes should bust the entire cache
CACHED_MODELS = (
    Team, OverviewKeyBlog, OverviewKeySection,
    FeaturedPropertySection, MarketinsightSection,
    WhoWeArePage, Amenity, BlogPost, Property,
)


def _clear_cache(sender, **kwargs):
    """Clear the full cache on any save or delete."""
    cache.clear()


# Register cache-busting for every model in CACHED_MODELS
for _model in CACHED_MODELS:
    post_save.connect(_clear_cache, sender=_model)
    post_delete.connect(_clear_cache, sender=_model)


# ─────────────────────────────────────────────────────────────────────────────
# Auto-translation
# ─────────────────────────────────────────────────────────────────────────────

# Target languages for auto-translation
TRANSLATION_LANGUAGES = ['ar', 'ru', 'ka']

# Fields to attempt translation on (only those present on the model are used)
FIELDS_TO_TRANSLATE = [
    'title', 'description', 'paragraph', 'paragraph1', 'paragraph2',
    'price', 'city', 'location', 'property_type', 'sale_type',
    'size', 'status', 'amenities_description', 'furnished',
    'bedrooms', 'bathroom', 'completion_date', 'parking',
    'name', 'position',
]

# Models to auto-translate
MODELS_TO_TRANSLATE = [
    Team, OverviewKeyBlog, OverviewKeySection,
    FeaturedPropertySection, MarketinsightSection,
    WhoWeArePage, Amenity, BlogPost, City, Property,
]


def auto_translate_instance(sender, instance, **kwargs):
    """
    Pre-save signal handler that auto-translates text fields.

    For each field in FIELDS_TO_TRANSLATE that exists on the instance,
    translates the English value into each language in TRANSLATION_LANGUAGES
    and stores the result in instance.translations[field][lang].

    Skips fields that are already translated, so repeated saves don't
    re-translate unchanged content.

    Requires the model to have a JSONField named `translations`.
    """
    if not hasattr(instance, 'translations'):
        return  # Model doesn't support translations

    if not instance.translations:
        instance.translations = {}

    for field in FIELDS_TO_TRANSLATE:
        base_text = getattr(instance, field, None)
        if not base_text:
            continue

        if field not in instance.translations:
            instance.translations[field] = {}

        for lang in TRANSLATION_LANGUAGES:
            # Skip if already translated
            if lang in instance.translations[field]:
                continue
            try:
                translated = GoogleTranslator(source='en', target=lang).translate(str(base_text))
                instance.translations[field][lang] = translated
            except Exception as e:
                print(f"[auto_translate] {sender.__name__}.{field} → {lang}: {e}")


# Uncomment to enable auto-translation on save:
# for _model in MODELS_TO_TRANSLATE:
#     pre_save.connect(auto_translate_instance, sender=_model)