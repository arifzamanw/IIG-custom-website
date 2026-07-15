import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
from core.models import PropertyImage
import os

def download_image_to_property(property_instance, image_url, sort_order=0):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        filename = os.path.basename(urlparse(image_url).path)
        content = ContentFile(response.content)

        img = PropertyImage(property=property_instance, sort_order=sort_order)
        img.image.save(filename, content, save=True)

    except Exception as e:
        print(f"Failed to download or save image from {image_url}: {e}")
        
def get_amenities(strr):
    amenities = {
        'BA': "Balcony",
        'AC': "Air Conditioning",
        'CP': "Covered Parking",
        'BK': "Built in Kitchen Appliances",
        'MB': "Maids Room",
        'GA': "Gymnasium",
        'SA': "Shared Pool",
        'SP': "Study Room",
        'SR': "Storage Room",
        'VW': "View of Water",
        'SE': "Security",
        'MT': "Maintenance",
        'SG': "Swimming Pool",
        'CV': "Central A/C & Heating",
        'CW': "Concierge Service",
        'HO': "Housekeeping",
        'SM': "Steam Room",
        'ML': "Marble Flooring",
        'PT': "Pets Allowed",
        'MO': "Mosque",
        'PK': "Public Park",
        'RT': "Retail Outlets",
        'CS': "Children's Play Area",
        'SS': "Sauna",
        'SY': "School"
    }

    amenities_list = []
    for amenity in strr.split(','):
        if amenity in amenities:
            amenities_list.append(amenities[amenity])

    return amenities_list
