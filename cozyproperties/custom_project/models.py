from django.db import models

# Create your models here.
from django.db import models

# Create your models here.




class Projects(models.Model):
    project_title = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_room_infos = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_location_infos = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_price_infos = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_payment_plan_cunstruction = models.CharField(max_length=50, null=True, blank=True, default=None)
    project_payment_plan_handover = models.CharField(max_length=50, null=True, blank=True, default=None)
    project_brochur = models.CharField(max_length=200, null=True, blank=True, default=None)
    project_floorplan = models.CharField(max_length=200, null=True, blank=True, default=None)
    about_the_developper = models.TextField(null=True, blank=True, default=None)
    project_video = models.FileField(null=True, blank=True)
    poject_video_url = models.CharField(max_length=150,null=True, blank=True)
   
   
    has_gym = models.BooleanField(default=False, verbose_name='Gym')
    has_pool = models.BooleanField(default=False, verbose_name='Pool')
    has_private_pool = models.BooleanField(default=False, verbose_name='Private Pool')
    has_private_parking = models.BooleanField(default=False, verbose_name='Private Parking')
    has_laundry = models.BooleanField(default=False, verbose_name='Laundry Facilities')
    has_pet_friendly = models.BooleanField(default=False, verbose_name='Pet-Friendly')
    has_elevator = models.BooleanField(default=False, verbose_name='Elevator')
    has_security = models.BooleanField(default=False, verbose_name='Security')
    has_balcony = models.BooleanField(default=False, verbose_name='Balcony/Patio')
    has_air_conditioning = models.BooleanField(default=False, verbose_name='Air Conditioning')
    has_heating = models.BooleanField(default=False, verbose_name='Heating')
    has_dishwasher = models.BooleanField(default=False, verbose_name='Dishwasher')
    has_internet = models.BooleanField(default=False, verbose_name='Internet')
    has_cable_tv = models.BooleanField(default=False, verbose_name='Cable TV')
    has_fireplace = models.BooleanField(default=False, verbose_name='Fireplace')
    has_furnished = models.BooleanField(default=False, verbose_name='Furnished')
    has_wheelchair_accessible = models.BooleanField(default=False, verbose_name='Wheelchair Accessible')
    has_hardwood_or_tiledfloor   = models.BooleanField(default=False, verbose_name='Hardwood or Tiledfloor')
    has_balcony_or_patio   = models.BooleanField(default=False, verbose_name='Balcony or Patio')
    has_walk_in_closet   = models.BooleanField(default=False, verbose_name='Walk In Closet')
    has_modern_kitchen_appliances   = models.BooleanField(default=False, verbose_name='Modern Kitchen')
    has_soundproofing   = models.BooleanField(default=False, verbose_name='SoundProofing')
    has_smart_home_features   = models.BooleanField(default=False, verbose_name='SmartHome Features')
    has_home_theater   = models.BooleanField(default=False, verbose_name='Home theater')
    has_wine_cellar   = models.BooleanField(default=False, verbose_name='Wine Cellar')
    has_solar_panel  = models.BooleanField(default=False, verbose_name='Solar Panel')
    has_eco_friendly_feature   = models.BooleanField(default=False, verbose_name='eco friendly feature')
    has_sauna_or_steam   = models.BooleanField(default=False, verbose_name='Sauna or Steam')
    has_gated_security = models.BooleanField(default=False, verbose_name='Gated Security')
    has_clubhouse_or_community_center   = models.BooleanField(default=False, verbose_name='Clubhouse or Community Center')
    has_tennis_or_basketball   = models.BooleanField(default=False, verbose_name='Tennis or basketball')
    has_playground_or_park   = models.BooleanField(default=False, verbose_name='PlayingGround or Park')
    has_walking_or_joggin_trail   = models.BooleanField(default=False, verbose_name='Walking or Jogging Trail')
    has_lake_water_feature  = models.BooleanField(default=False, verbose_name='Lake or Water Features')
    has_golf_course   = models.BooleanField(default=False, verbose_name='Golf Course')
    has_restaurant_or_cafee   = models.BooleanField(default=False, verbose_name='Restaurant or Cafee')
    has_shuttle_or_transport_service   = models.BooleanField(default=False, verbose_name='Shuttle or transport service')
    has_buisness_center   = models.BooleanField(default=False, verbose_name='Buisness Center')
    has_community_event_or_classes   = models.BooleanField(default=False, verbose_name='CommunityEvent or classes')
    has_24_hours_maintenance_service = models.BooleanField(default=False, verbose_name='24 Hours Maintenance Service')
    has_landscape_garden = models.BooleanField(default=False, verbose_name='Landscape Garden')
    has_barbecue_or_picnic_aeas = models.BooleanField(default=False, verbose_name='Barbecue Or Picnic Areas')
    has_yoga_space = models.BooleanField(default=False, verbose_name='Yoga Space')
    has_on_site_storage = models.BooleanField(default=False, verbose_name='On Site Storage')
    has_recycling_and_waste_service = models.BooleanField(default=False, verbose_name='Recycling And Waste services')
    has_bike_storage_and_path = models.BooleanField(default=False, verbose_name='Bike Storage and Path')
    has_health_or_spa_centers =  models.BooleanField(default=False, verbose_name='Health or Spa Center')
    
    
    
    
    main_image  =  models.FileField(upload_to='uploads/',null=True, blank=True)
    banner_image  =  models.FileField(upload_to='uploads/',null=True, blank=True)
    STATUS_CHOICES = [
        ('Ready', 'Ready'),
        ('Offplan', 'Offplan'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Ready',  # You can set the default value to 'Ready' or 'Offplan'
    )
  
    def __str__(self):
        return self.project_title
    
    def get_main_infos(self):
        return {'cover_image': self.image.url if  self.image else  None,
                'project_title': self.project_title if self.project_title else None,
                'project_room_infos':self.project_room_infos if self.project_room_infos else None,
                'project_location_infos':self.project_location_infos if self.project_location_infos else None,
                'project_price_infos':self.project_price_infos if self.project_price_infos else None
                }
    def get_feature_details(self):
        return self.projectcomunitydetails_set.filter(is_features=True)
    
    def get_project_details(self):
        return self.projectcomunitydetails_set.filter(is_features=False)

class ProjectComunityDetails(models.Model):
    project_detail_title = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_detail_sub_title = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_detail_description = models.TextField(null=True, blank=True, default=None) 
    project = models.ForeignKey(Projects,null=True,  on_delete=models.SET_NULL)
    is_features =  models.BooleanField(default=False)

    def get_image_url(self):
        return self.images.get(id=self.id).image.url
    
    def __str__(self):
        return self.project_detail_title

class UploadedImage(models.Model):
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='uploads/',null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    project_comunity_details = models.ForeignKey(ProjectComunityDetails,default=None, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.title