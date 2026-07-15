from django.contrib import admin
from core.models import * 
from django.db import transaction



@admin.register(Location)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('city', )
    
@admin.register(Sublocation)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', )

@admin.register(TowerName)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Appartype)
class SubCityAdmin(admin.ModelAdmin):
    list_display = ('app_type',)
    
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1 
    max_num = 7 


admin.site.register(PropertyImage) 


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
    
    
class PropertyAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']
    list_display = ('title', 'location',
                    
                    
                    'price', 'appartment_type', 'status')  # Customize this as needed
    search_fields = ('title', 'description', 'location')
    inlines = [PropertyImageInline]
    # Add the inline to the Property admin
    # def get_queryset(self, request):
    #     """ Use prefetch_related to speed up database queries. """
    #     queryset = super().get_queryset(request)
    #     return queryset.prefetch_related('images', 'floor_plans')
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """ Override save_model to handle bulk save of images for better performance """
        # Call the parent save_model to save the property itself
        super().save_model(request, obj, form, change)
        
        # Get the images from the form
        images = form.cleaned_data.get('images', [])
        
        # Only proceed if there are images to save
        if images:
            # Create PropertyImage instances for each image
            property_images = [
                PropertyImage(property=obj, image=image) for image in images
            ]
            # Bulk create images (this will save all images in one go)
            PropertyImage.objects.bulk_create(property_images)
        
admin.site.register(Properties, PropertyAdmin)



