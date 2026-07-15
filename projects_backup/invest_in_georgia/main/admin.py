from django.contrib import admin
from main.models import *
from django.db import transaction
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase




def add_translations_to_admin(model_admin_cls, model):
    """Append translations field to a ModelAdmin if the model has it."""
    if not hasattr(model, 'translations'):
        return
    if not hasattr(model_admin_cls, 'fieldsets') or model_admin_cls.fieldsets is None:
        return
    existing = list(model_admin_cls.fieldsets)
    if any('translations' in (fs[1].get('fields') or ()) for fs in existing):
        return
    existing.append(('Translations (AR / RU / KA)', {
        'fields': ('translations',),
        'classes': ('collapse',),
    }))
    model_admin_cls.fieldsets = tuple(existing)


# ==========================================================
# Apply translations field to all relevant admins
# ==========================================================

for model, model_admin in admin.site._registry.items():
    add_translations_to_admin(type(model_admin), model)

# ==========================================================
# A. PROPERTIES
# ==========================================================

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    max_num = 7


class PropertyFLoorPlanInline(admin.TabularInline):
    model = PropertyFLoorPlan
    extra = 1
    max_num = 6


admin.site.register(PropertyImage)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'location_latitude', 'location_longitude', 'price', 'property_type', 'status')
    search_fields = ('title', 'description', 'location')
    inlines = [PropertyImageInline, PropertyFLoorPlanInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('images', 'floor_plans')

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        images = form.cleaned_data.get('images', [])
        if images:
            property_images = [PropertyImage(property=obj, image=image) for image in images]
            PropertyImage.objects.bulk_create(property_images)


admin.site.register(Property, PropertyAdmin)


# ==========================================================
# B. AMENITIES
# ==========================================================

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)


# ==========================================================
# C. CITIES
# ==========================================================

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)


# ==========================================================
# D. TEAM
# ==========================================================

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'phone', 'email')


# ==========================================================
# E. BLOG
# ==========================================================

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'author')
    list_filter = ('created_at', 'author')
    ordering = ('-created_at',)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(BlogPost, BlogPostAdmin)


# ==========================================================
# F. INSTAGRAM
# ==========================================================

@admin.register(InstagramReel)
class InstagramReelAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')


# ==========================================================
# G. FEATURED PROPERTY SECTION
# ==========================================================

@admin.register(FeaturedPropertySection)
class FeaturedPropertySectionAdmin(admin.ModelAdmin):
    list_display = ('title',)


# ==========================================================
# H. INVESTMENT SECTION
# ==========================================================

class InvestmentFeatureInline(admin.TabularInline):
    model = InvestmentFeature
    extra = 1


@admin.register(InvestmentSection)
class InvestmentSectionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    inlines = [InvestmentFeatureInline]


# ==========================================================
# I. MARKET INSIGHT SECTION
# ==========================================================

@admin.register(MarketinsightSection)
class MarketinsightSectionAdmin(admin.ModelAdmin):
    list_display = ('title',)


# ==========================================================
# J & K. OVERVIEW SECTIONS
# ==========================================================

@admin.register(OverviewKeySection)
class OverviewKeySectionAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(OverviewKeyBlog)
class OverviewKeyBlogAdmin(admin.ModelAdmin):
    list_display = ('block_position', 'title', 'position')
    ordering = ('block_position',)


# ==========================================================
# L. SUBSCRIBERS
# ==========================================================

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')


# ==========================================================
# M. CALL REQUESTS
# ==========================================================

@admin.register(CallRequest)
class CallRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'submitted_at')


# ==========================================================
# N. CONSULTATION BOOKINGS
# ==========================================================

@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'date_subscribed')


# ==========================================================
# Z1. WHO WE ARE PAGE
# ==========================================================



@admin.register(WhoWeArePage)
class WhoWeArePageAdmin(SortableAdminBase, admin.ModelAdmin):

    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_script_title', 'hero_title', 'hero_paragraph')
        }),
        ('Mission Card', {
            'fields': ('mission_script_title', 'mission_title', 'mission_paragraph')
        }),
        ('Vision Card', {
            'fields': ('vision_script_title', 'vision_title', 'vision_paragraph')
        }),
        ('Core Values Card', {
            'fields': ('values_script_title', 'values_mission_title', 'value_paragraph')
        }),
    )

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

# ==========================================================
# Z2. SERVICES PAGE
# ==========================================================

class ServicesPageBlockInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ServicesPageBlock
    extra = 1
    fields = ( 'title', 'paragraph'),


@admin.register(ServicesPage)
class ServicesPageAdmin(SortableAdminBase, admin.ModelAdmin):  # SortableAdminBase is required on the parent
    inlines = [ServicesPageBlockInline]

    fieldsets = (
        ('Services Header Section', {
            'fields': ('hero_script_title', 'hero_title', 'hero_paragraph')
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False
# ==========================================================
# Z3. CONTACT PAGE
# ==========================================================

@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Page Header', {
            'fields': ('hero_title',)
        }),
        ('Contact Info Cards', {
            'fields': ('address', 'phone', 'email', 'whatsapp_number')
        }),
        ('Google Map', {
            'fields': ('map_embed_url',)
        }),
        ('Get in Touch Section', {
            'fields': ('contact_script_title', 'contact_title', 'contact_paragraph')
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SEO)
class SEOAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'page_key', 'meta_title', 'robots_meta')
    list_editable = ('meta_title',)
    search_fields = ('page_name', 'page_key', 'meta_title')
    prepopulated_fields = {'page_key': ('page_name',)}
    fieldsets = (
        ('Page Identity', {
            'fields': ('page_name', 'page_key')
        }),
        ('SEO Fields', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords','og_title', 'og_description','og_url', 'schema_json', 'robots_meta')
        }),
    )


# Apply translations field to all admins that have fieldsets defined
for model, model_admin in admin.site._registry.items():
    add_translations_to_admin(type(model_admin), model)
