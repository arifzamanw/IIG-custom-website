from django.core.management.base import BaseCommand
from django.db.models import ForeignKey, ManyToManyField, DecimalField, IntegerField, FloatField, BooleanField, DateField, DateTimeField
from django.core.cache import cache
from deep_translator import GoogleTranslator
from main.models import (
    Team, OverviewKeyBlog, OverviewKeySection,
    FeaturedPropertySection, MarketinsightSection,
    WhoWeArePage,
    Amenity, BlogPost, City, Property, ServicesPageBlock,
    InvestmentSection, InvestmentFeature
)


LANGUAGES = ['ar', 'ru', 'ka']

# Only text fields. NO foreign keys, NO numeric fields.
FIELDS_TO_TRANSLATE = [
    # generic
    'title', 'description', 'paragraph', 'paragraph1', 'paragraph2',
    'location', 'property_type', 'sale_type',
    'status', 'amenities_description', 'furnished', 'bedrooms', 'bathroom',
    'completion_date', 'parking', 'name', 'position', 'caption',
    'content', 'subtitle',
    # WhoWeArePage
    'hero_script_title', 'hero_title', 'hero_paragraph',
    'mission_script_title', 'mission_title', 'mission_paragraph',
    'vision_script_title', 'vision_title', 'vision_paragraph',
    'values_script_title', 'values_mission_title', 'value_paragraph',
    # ContactPage
    'contact_script_title', 'contact_title', 'contact_paragraph',
    'address',
    # Project
    'price_range',
    # Investment
    'duration', 'risk_level', 'investment_type',
]
MODELS_TO_TRANSLATE = [
    Team, OverviewKeyBlog, OverviewKeySection,
    FeaturedPropertySection, MarketinsightSection,
    WhoWeArePage,
    Amenity, BlogPost, City, Property, ServicesPageBlock,
    InvestmentSection, InvestmentFeature,
]

# Skip-translate field types - never translate these even if listed
SKIP_FIELD_TYPES = (
    ForeignKey, ManyToManyField,
    DecimalField, IntegerField, FloatField,
    BooleanField, DateField, DateTimeField,
)

GOOGLE_LIMIT = 4500  # safe margin under 5000 char limit


def _is_translatable_field(model, field_name):
    """Return True if field exists on model and is a translatable text field."""
    try:
        field = model._meta.get_field(field_name)
    except Exception:
        return False
    if isinstance(field, SKIP_FIELD_TYPES):
        return False
    return True


def _chunk_text(text, max_len=GOOGLE_LIMIT):
    """Split text into chunks under max_len, breaking at sensible boundaries."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to break at paragraph, then sentence, then word
        cut = text.rfind('</p>', 0, max_len)
        if cut == -1:
            cut = text.rfind('. ', 0, max_len)
        if cut == -1:
            cut = text.rfind(' ', 0, max_len)
        if cut == -1:
            cut = max_len
        else:
            cut += 4 if text[cut:cut+4] == '</p>' else 1
        chunks.append(text[:cut])
        text = text[cut:]
    return chunks


def translate_long(text, target):
    """Translate arbitrarily long text by chunking."""
    chunks = _chunk_text(text)
    translator = GoogleTranslator(source='en', target=target)
    return ''.join(translator.translate(c) or '' for c in chunks)

class Command(BaseCommand):
    help = 'Translate text fields of selected models into AR/RU/KA.'

    def handle(self, *args, **options):
        for model in MODELS_TO_TRANSLATE:
            self.stdout.write(f"Translating {model.__name__}...")
            for obj in model.objects.all():
                if not hasattr(obj, 'translations'):
                    continue
                if obj.translations is None:
                    obj.translations = {}

                for field in FIELDS_TO_TRANSLATE:
                    if not _is_translatable_field(model, field):
                        continue

                    value = getattr(obj, field, None)
                    if not value or not isinstance(value, str):
                        continue

                    obj.translations.setdefault(field, {})

                    for lang in LANGUAGES:
                        if lang in obj.translations[field]:
                            continue

                        cache_key = f"translation:{field}:{lang}:{hash(value)}"
                        cached = cache.get(cache_key)
                        if cached:
                            obj.translations[field][lang] = cached
                            continue

                        try:
                            translated = translate_long(value, lang)
                            obj.translations[field][lang] = translated
                            cache.set(cache_key, translated, timeout=86400)
                        except Exception as e:
                            self.stderr.write(
                                f"  ⚠️ {model.__name__}#{obj.pk}.{field} → {lang}: {e}"
                            )

                obj.save(update_fields=['translations'])
            self.stdout.write(self.style.SUCCESS(f"✅ Done {model.__name__}"))
