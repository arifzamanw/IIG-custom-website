from django.db import models
from django.utils.text import slugify

def rename_file(instance, filename):
    # Your custom file renaming function here
    return f"property_images/{filename}"

class Location(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    city = models.CharField("city", max_length=63)
    image = models.FileField(upload_to=rename_file, null=True, blank=True, default=None)

    def __str__(self):
        return self.city

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.city)
            # Ensure slug uniqueness
            original_slug = self.slug
            num = 1
            while Location.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)


class Sublocation(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    name = models.CharField("sub_location", max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sublocations")

    def __str__(self):
        return f"{self.name} ({self.location.city})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            num = 1
            while Sublocation.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)


class TowerName(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    name = models.CharField("tower_name", max_length=255)
    sublocation = models.ForeignKey(Sublocation, on_delete=models.CASCADE, related_name="towers")

    def __str__(self):
        return f"{self.name} ({self.sublocation.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            num = 1
            while TowerName.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)


class Appartype(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    app_type = models.CharField("app_type", max_length=63)

    def __str__(self):
        return self.app_type

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.app_type)
            original_slug = self.slug
            num = 1
            while Appartype.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    license_no = models.CharField(max_length=50, null=True, blank=True)
    picture = models.ImageField(upload_to='team_photos/', null=True, blank=True)  # Image upload field

    def __str__(self):
        return self.name




class Infos(models.Model):
    title = models.CharField(max_length=56, unique=True, null=True, blank=True, default=None)
    description = models.TextField(max_length=20000)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
            Generate a unique code for model.
        """
        return super().save(*args, **kwargs)


class Properties(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    permit_number = models.BigIntegerField()
    status = models.CharField(max_length=50, null=True, blank=True)
    amenities = models.JSONField(default=dict, blank=True)
    completion_status = models.CharField(max_length=150, null=True, blank=True)
    subtype = models.CharField(max_length=50, null=True, blank=True)
    ref = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    size = models.CharField(max_length=50, null=True, blank=True)
    size_unit = models.CharField(max_length=50, null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    furnished = models.CharField(max_length=50, null=True, blank=True)
    bedrooms = models.CharField(max_length=50, null=True, blank=True)
    bathroom = models.CharField(max_length=50, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    sub_location = models.ForeignKey(Sublocation, on_delete=models.SET_NULL, null=True, blank=True)
    tower_name = models.ForeignKey(TowerName, on_delete=models.SET_NULL, null=True, blank=True)
    agent = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    appartment_type = models.ForeignKey(Appartype, on_delete=models.SET_NULL, null=True, blank=True)
    is_imported = models.BooleanField(default=False)
    off_plan = models.BooleanField(default=False)
    offering_type = models.CharField(max_length=10, null=True, blank=True)
    property_type = models.CharField(max_length=10, null=True, blank=True)
    price_on_application = models.BooleanField(default=False)
    completion_status = models.CharField(max_length=150, null=True, blank=True)
    geopoints =  models.CharField(max_length=150, null=True, blank=True, default=None)
    
    

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            num = 1
            while Properties.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)


class PropertyImage(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to=rename_file, null=True, blank=True)
    caption = models.CharField(max_length=255, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.property.title}"
