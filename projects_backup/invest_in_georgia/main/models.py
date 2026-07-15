"""
main/models.py

Data models for the Invest In Georgia real estate platform.

Sections:
  - Property & related (PropertyImage, PropertyFLoorPlan, Property, City, Amenity)
  - Content / CMS pages (WhoWeArePage, ServicesPage, etc.)
  - Blog & News
  - Lead capture (Subscriber, ConsultationBooking, CallRequest, Lead)
  - SEO
  - Supporting models (Team, Investment, Project, InstagramReel)
"""

import os
from io import BytesIO
from uuid import uuid4

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile
from PIL import Image
from ckeditor.fields import RichTextField


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _resize_and_save(instance_image, width, height):
    """
    Resize an ImageField in-place and re-assign it with a UUID filename.

    Opens the current image, converts to RGB, resizes to (width x height)
    using the best available Lanczos resampling, then saves back as JPEG.

    Args:
        instance_image: The ImageField (e.g. self.image).
        width (int): Target width in pixels.
        height (int): Target height in pixels.

    Returns:
        The processed image content as a ContentFile (caller must .save() it).
    """
    img = Image.open(instance_image)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS  # Pillow < 10 fallback

    img = img.resize((width, height), resample)
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())


def _new_filename(original_name):
    """Generate a UUID-based filename preserving the original extension."""
    ext = os.path.splitext(original_name)[-1]
    return f"{uuid4().hex}{ext}"


class TranslatableMixin:
    """
    Mixin that adds a get_translation() helper to any model
    that has a `translations` JSONField.
    """
    def get_translation(self, field, lang='en'):
        """
        Return the translated value for `field` in `lang`.
        Falls back to None if not found.
        """
        return self.translations.get(field, {}).get(lang)


# ─────────────────────────────────────────────────────────────────────────────
# Property & related
# ─────────────────────────────────────────────────────────────────────────────

class City(TranslatableMixin, models.Model):
    """A city that properties can be located in."""
    name         = models.CharField(max_length=255)
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('name',)

    def __str__(self):
        return self.name


class Amenity(TranslatableMixin, models.Model):
    """A single amenity tag that can be linked to properties."""
    name         = models.CharField(max_length=255, unique=True)
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class PropertyImage(models.Model):
    """
    An additional image for a Property listing.
    Images are auto-resized to 770×520 px on save.
    """
    property  = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='images')
    image     = models.ImageField(upload_to='properties_images/', blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.image:
            content      = _resize_and_save(self.image, 770, 520)
            new_filename = _new_filename(self.image.name)
            self.image.save(new_filename, content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.property}"


class PropertyFLoorPlan(models.Model):
    """A floor plan image attached to a Property."""
    property  = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='floor_plans')
    title     = models.CharField(max_length=55, blank=True, null=True)
    image     = models.ImageField(upload_to='properties_floors/', blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Floor plan: {self.title or self.property}"


class Property(TranslatableMixin, models.Model):
    """
    Core property listing model.

    Covers residential and commercial property types.
    Main profile image is auto-resized to 370×208 px on save.
    Slug is auto-generated from title + ID on first save.
    """

    PROPERTY_TYPE_CHOICES = [
        ('apartment',  'Apartment'),
        ('house',      'House'),
        ('commercial', 'Commercial'),
        ('loft',       'Loft'),
        ('studio',     'Studio'),
        ('villa',      'Villa'),
        ('townhouse',  'Townhouse'),
        ('penthouse',  'Penthouse'),
        ('duplex',     'Duplex'),
        ('mansion',    'Mansion'),
        ('farmhouse',  'Farmhouse'),
        ('industrial', 'Industrial'),
        ('office',     'Office'),
    ]

    PROPERTY_STATUS_CHOICES = [
        ('available',      'Available'),
        ('sold',           'Sold'),
        ('under_contract', 'Under Contract'),
        ('coming_soon',    'Coming Soon'),
        ('off_market',     'Off Market'),
    ]

    PROPERTY_SALE_CHOICES = [
        ('rent', 'Rent'),
        ('buy',  'Buy'),
    ]

    # Core fields
    title       = models.CharField(max_length=255, null=True, blank=True)
    slug        = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price       = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)

    # Location
    city               = models.ForeignKey(City, on_delete=models.CASCADE, related_name="properties", null=True, blank=True)
    location           = models.CharField(max_length=255, null=True, blank=True)
    location_latitude  = models.CharField(max_length=100, null=True, blank=True, default='')
    location_longitude = models.CharField(max_length=100, null=True, blank=True, default='')

    # Classification
    property_type = models.CharField(max_length=100, choices=PROPERTY_TYPE_CHOICES, null=True, blank=True)
    sale_type     = models.CharField(max_length=100, choices=PROPERTY_SALE_CHOICES, null=True, blank=True)
    status        = models.CharField(max_length=50,  choices=PROPERTY_STATUS_CHOICES, default='available', null=True, blank=True)

    # Details
    size            = models.DecimalField(max_digits=10, decimal_places=5, help_text="Size in square meters", null=True, blank=True)
    bedrooms        = models.CharField(max_length=50, null=True, blank=True, default=None)
    bathroom        = models.CharField(max_length=50, null=True, blank=True, default=None)
    furnished       = models.CharField(max_length=50, null=True, blank=True, default=None)
    parking         = models.CharField(max_length=50, null=True, blank=True, default=None)
    completion_date = models.CharField(max_length=50, null=True, blank=True, default=None)
    ref             = models.CharField(max_length=50, null=True, blank=True, default=None)

    # Media
    image         = models.ImageField(upload_to='property_profileI/', blank=True, null=True)
    youtube_video = models.URLField(blank=True, null=True, help_text="YouTube URL e.g. https://www.youtube.com/watch?v=xxx")

    # Relations
    amenities            = models.ManyToManyField(Amenity, blank=True)
    amenities_description = models.CharField(max_length=400, null=True, blank=True, default=None)
    agent                = models.ForeignKey("Team", null=True, blank=True, on_delete=models.SET_NULL, related_name="properties")

    # Flags
    featured    = models.BooleanField(default=False, null=True, blank=True)
    is_popular  = models.BooleanField(default=False)
    is_imported = models.BooleanField(default=False)

    # SEO / search
    keywords     = models.TextField(blank=True)
    translations = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def formatted_price(self):
        """Return price formatted as '1,234,567 USD' with no decimals."""
        if self.price is not None:
            return f"{self.price:,.0f} USD"
        return "0 USD"

    def save(self, *args, **kwargs):
        # Resize profile image before saving
        if self.image:
            content      = _resize_and_save(self.image, 370, 208)
            new_filename = _new_filename(self.image.name)
            self.image.save(new_filename, content, save=False)

        # First save to get a DB ID
        super().save(*args, **kwargs)

        # Auto-generate slug from title + ID (only once)
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.id}")
            super().save(update_fields=["slug"])

    def __str__(self):
        return self.title or f"Property #{self.id}"


# ─────────────────────────────────────────────────────────────────────────────
# Team
# ─────────────────────────────────────────────────────────────────────────────

class Team(TranslatableMixin, models.Model):
    """An agent/team member displayed on the site."""
    name       = models.CharField("name",     max_length=63)
    position   = models.CharField("position", max_length=63)
    caption    = models.TextField()
    phone      = models.CharField("phone", max_length=63, null=True, blank=True, default=None)
    email      = models.CharField("email", max_length=63, null=True, blank=True, default=None)
    socials    = models.TextField(default={})
    license_no = models.TextField(default={})
    picture    = models.FileField(upload_to='team_images/', null=True, blank=True, default=None)
    bitrix_id  = models.TextField(null=True, blank=True)
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return str(self.name)


# ─────────────────────────────────────────────────────────────────────────────
# Blog & News
# ─────────────────────────────────────────────────────────────────────────────

class BlogPost(TranslatableMixin, models.Model):
    """A blog post. Slug is auto-generated from title on first save."""
    title        = models.CharField(max_length=255)
    slug         = models.SlugField(unique=True, blank=True)
    author       = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    content      = RichTextField()
    tags         = models.TextField(_("tags"), blank=True, null=True)
    image        = models.ImageField(upload_to='news_images/', blank=True, null=True)
    translations = models.JSONField(default=dict, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# Lead capture
# ─────────────────────────────────────────────────────────────────────────────

class Subscriber(models.Model):
    """Newsletter subscriber."""
    email           = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ConsultationBooking(models.Model):
    """A consultation request submitted via the property detail page."""
    full_name       = models.CharField(max_length=255)
    email           = models.EmailField(unique=True)
    phone           = models.CharField(max_length=15)
    message         = models.TextField()
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class CallRequest(models.Model):
    """A call-back request submitted via the contact widget."""
    CONTACT_WAY_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
    ]
    name         = models.CharField(max_length=100)
    phone        = models.CharField(max_length=15)
    email        = models.EmailField()
    contact_way  = models.CharField(max_length=20, choices=CONTACT_WAY_CHOICES)
    branch       = models.CharField(max_length=100, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


class Lead(models.Model):
    """
    A general lead captured from the website.
    Linked optionally to a specific property.
    """
    SOURCE_CHOICES = [
        ('website',      'Website'),
        ('email',        'Email'),
        ('social_media', 'Social Media'),
    ]
    STATUS_CHOICES = [
        ('new',       'New'),
        ('contacted', 'Contacted'),
        ('closed',    'Closed'),
    ]
    name              = models.CharField(max_length=255)
    email             = models.EmailField()
    phone_number      = models.CharField(max_length=15, blank=True, null=True)
    message           = models.TextField(blank=True, null=True)
    source            = models.CharField(max_length=100, choices=SOURCE_CHOICES)
    status            = models.CharField(max_length=100, choices=STATUS_CHOICES)
    property_interest = models.ForeignKey(Property, on_delete=models.CASCADE, blank=True, null=True, related_name="leads")
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lead: {self.name} ({self.status})"


# ─────────────────────────────────────────────────────────────────────────────
# SEO
# ─────────────────────────────────────────────────────────────────────────────

class SEO(models.Model):
    """
    Per-page SEO settings managed via Django admin.
    Identified by a unique `page_key` slug (e.g. 'home', 'properties').
    """
    ROBOTS_CHOICES = [
        ('index',     'Index'),
        ('noindex',   'Noindex'),
        ('follow',    'Follow'),
        ('nofollow',  'Nofollow'),
    ]
    page_name        = models.CharField(max_length=255)
    page_key         = models.SlugField(max_length=100, unique=True, blank=True, null=True,
                                        help_text="Unique key to identify this page (e.g. 'home', 'properties')")
    meta_title       = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords    = models.CharField(max_length=255, blank=True, null=True)
    og_title         = models.CharField(max_length=255, blank=True, null=True)
    og_description   = models.TextField(blank=True, null=True)
    og_url           = models.URLField(blank=True, null=True)
    schema_json      = models.TextField(blank=True, null=True,
                                        help_text="Raw JSON-LD schema content (without <script> tags)")
    robots_meta      = models.CharField(max_length=50, choices=ROBOTS_CHOICES, default='index')

    def __str__(self):
        return self.page_name


# ─────────────────────────────────────────────────────────────────────────────
# CMS / Page content
# ─────────────────────────────────────────────────────────────────────────────

class OverviewKeySection(TranslatableMixin, models.Model):
    """Header section for the News/Overview page."""
    title        = models.CharField(max_length=255)
    paragraph    = models.TextField(max_length=555)
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class OverviewKeyBlog(TranslatableMixin, models.Model):
    """
    A content block on the News/Overview page.
    Can be positioned left or right, ordered by block_position.
    """
    POSITION_CHOICES = [
        ('left',  'Left'),
        ('right', 'Right'),
    ]
    position       = models.CharField(max_length=100, choices=POSITION_CHOICES)
    block_position = models.PositiveIntegerField(null=True, blank=True, unique=True)
    title          = models.CharField(max_length=255)
    paragraph1     = models.TextField()
    paragraph2     = models.TextField()
    image          = models.ImageField(upload_to='overview_blocks/', blank=True, null=True)
    image_alt      = models.CharField(max_length=255, blank=True, null=True)
    translations   = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["block_position"]

    def __str__(self):
        return f"Block {self.block_position}: {self.title}"


class FeaturedPropertySection(TranslatableMixin, models.Model):
    """Homepage featured property section header."""
    title        = models.CharField(max_length=55)
    paragraph    = models.TextField(help_text="Main paragraph or description")
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class MarketinsightSection(TranslatableMixin, models.Model):
    """Homepage market insight section header."""
    title        = models.CharField(max_length=55)
    paragraph    = models.TextField(max_length=255)
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class InvestmentSection(TranslatableMixin, models.Model):
    """Homepage investment section header."""
    title        = models.CharField(max_length=255, help_text="Main heading of the section")
    subtitle     = models.TextField(help_text="Main paragraph or description")
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class InvestmentFeature(TranslatableMixin, models.Model):
    """A feature bullet within an InvestmentSection."""
    section      = models.ForeignKey(InvestmentSection, on_delete=models.CASCADE, related_name='features')
    icon         = models.CharField(max_length=100, help_text="Icon class e.g. 'fa-solid fa-globe'")
    title        = models.CharField(max_length=100)
    description  = models.TextField()
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.title} ({self.section.title})"


class WhoWeArePage(TranslatableMixin, models.Model):
    """Singleton-style model for the Who We Are page content."""

    # Hero section
    hero_script_title = models.CharField(max_length=255, default="Expert Cross-Border Investment Consultant")
    hero_title        = models.CharField(max_length=255, default="Who We Are")
    hero_paragraph    = RichTextField(default='')

    # Mission section
    mission_script_title = models.CharField(max_length=255, default="Vision & Mission")
    mission_title        = models.CharField(max_length=255, default="Our Mission")
    mission_paragraph    = RichTextField(default='')

    # Vision section
    vision_script_title = models.CharField(max_length=25, default="Vision")
    vision_title        = models.CharField(max_length=255, default="Our Vision")
    vision_paragraph    = RichTextField(default='')

    # Core values section
    values_script_title  = models.CharField(max_length=25, default="Vision")
    values_mission_title = models.CharField(max_length=255, default="Our Values")
    value_paragraph      = RichTextField(default='')

    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name        = "Who We Are Page"
        verbose_name_plural = "Who We Are Page"

    def __str__(self):
        return "Who We Are Page"


class ServicesPage(TranslatableMixin, models.Model):
    """Singleton-style model for the Services page header."""
    hero_script_title = models.CharField(max_length=255, default="Our Services Includes")
    hero_title        = models.CharField(max_length=255, default="Services")
    hero_paragraph    = RichTextField(default='')
    translations      = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name        = "Services Page"
        verbose_name_plural = "Services Page"

    def __str__(self):
        return "Services Page"


class ServicesPageBlock(TranslatableMixin, models.Model):
    """An individual content block within the Services page."""
    page         = models.ForeignKey(ServicesPage, on_delete=models.CASCADE, related_name='blocks', null=True)
    order        = models.PositiveIntegerField(default=0, db_index=True)
    title        = models.CharField(max_length=255)
    paragraph    = RichTextField()
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering        = ['order']
        verbose_name    = "Service Block"
        verbose_name_plural = "Service Blocks"

    def __str__(self):
        return self.title


class ContactPage(TranslatableMixin, models.Model):
    """Singleton-style model for the Contact page content."""

    # Header
    hero_title = models.CharField(max_length=255, default="Contact Us")

    # Contact info
    address          = models.TextField(default='')
    phone            = models.CharField(max_length=50, default='')
    email            = models.EmailField(default='')
    whatsapp_number  = models.CharField(max_length=50, default='',
                                         help_text="Number only, e.g. 97145477804")

    # Map
    map_embed_url = models.URLField(max_length=1000, default='')

    # Get in touch section
    contact_script_title = models.CharField(max_length=255, default="Have Questions")
    contact_title        = models.CharField(max_length=255, default="Get in Touch")
    contact_paragraph    = models.TextField(default='')

    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name        = "Contact Page"
        verbose_name_plural = "Contact Page"

    def __str__(self):
        return "Contact Page"


# ─────────────────────────────────────────────────────────────────────────────
# Supporting models
# ─────────────────────────────────────────────────────────────────────────────

class Project(TranslatableMixin, models.Model):
    """A real estate development project grouping multiple properties."""
    title        = models.CharField(max_length=255)
    description  = models.TextField()
    location     = models.CharField(max_length=255)
    price_range  = models.CharField(max_length=100, help_text="Price range for available units")
    start_date   = models.DateField()
    end_date     = models.DateField()
    featured     = models.BooleanField(default=False)
    properties   = models.ManyToManyField(Property, related_name="projects")
    translations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class Investment(TranslatableMixin, models.Model):
    """An investment opportunity (not currently used in views)."""
    TYPE_CHOICES = [
        ('real_estate', 'Real Estate'),
        ('stocks',      'Stocks'),
        ('bonds',       'Bonds'),
        ('crypto',      'Cryptocurrency'),
    ]
    RISK_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]
    title           = models.CharField(max_length=255)
    description     = models.TextField()
    investment_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    expected_roi    = models.DecimalField(max_digits=5, decimal_places=2)
    duration        = models.CharField(max_length=100)
    risk_level      = models.CharField(max_length=100, choices=RISK_CHOICES)
    translations    = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class InstagramReel(models.Model):
    """An Instagram reel displayed on the site."""
    title      = models.CharField(max_length=255, blank=True, help_text="Optional display title")
    url        = models.URLField(help_text="Direct link to the Instagram reel")
    is_active  = models.BooleanField(default=True, help_text="Show this reel on the site?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.url