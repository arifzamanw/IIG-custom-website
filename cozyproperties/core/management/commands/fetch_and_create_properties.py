from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
import requests
import logging
import re
from django.core.exceptions import ValidationError
from core.models import (
    Properties, PropertyImage, Location, Sublocation,
    TowerName, Team, Appartype
)
from core.utils import download_image_to_property, get_amenities

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import properties from an XML feed'

    def get_appartment_type(self, code):
        mapping = {
            'AP': 'Apartment / Flat',
            'BW': 'Bungalow',
            'CD': 'Compound',
            'DX': 'Duplex',
            'FF': 'Full floor',
            'HF': 'Half floor',
            'LP': 'Plot',
            'PH': 'Penthouse',
            'TH': 'Townhouse',
            'VH': 'Villa / House',
            'WB': 'Whole Building',
            'HA': 'Hotel Apartment',
            'LC': 'Labor Camp',
            'BU': 'Bulk Units',
            'WH': 'Warehouse',
            'FA': 'Factory',
            'OF': 'Office Space',
            'RE': 'Retail',
            'SH': 'Shop',
            'SR': 'Showroom',
            'SA': 'Staff Accommodation',
        }

        name = mapping.get(code, 'Other')
        appartype, _ = Appartype.objects.get_or_create(app_type=name)
        return appartype

    def get_offer_type(self, ttype):
        status_type = {
            'RS': 'Resident - Sale',
            'RR': 'Resident - Rent',
            'CS': 'Commercial - Sale',
            'CR': 'Commercial - Rent',

        }

        if ttype in status_type:
            return status_type[ttype]
        else:
            return



    def handle(self, *args, **options):
         # Download CSV file
        url = "https://expert.propertyfinder.ae/feed/teona/privatesite/7a700ca42da28a259aaec93c2a40b218"
        response = requests.get(url)
        if response and response.text:
            properites = ET.fromstring(response.text)
            imported_refs = set()
            for ppt in properites:
                property_data = {
                }
                for info in ppt:
                    property_data[info.tag] = info.text

                pictures = ppt.find('photo')
                pictures = pictures.findall('url')
                if pictures:
                    for img in pictures:
                        text = img.text
                        if text:
                            if 'pictures' in property_data:
                                property_data['pictures'] += text + '\n' 
                            else:
                                property_data['pictures'] = text + '\n' 
                        # for i in range(min(5, len(pictures))):
                        #     property_data[f'picture_{i + 1}'] = img.text
                # Set location and apartment type foreign keys
                try:
                    location = Location.objects.get(city__iexact=property_data['city'])
                except Location.DoesNotExist:
                    location = Location.objects.create(city=property_data['city'])

                try:
                    agent = Team.objects.get(email__iexact=ppt.find('agent').find('email').text)
                except Team.DoesNotExist:
                    agent = Team.objects.create(email=ppt.find('agent').find('email').text, phone=ppt.find('agent').find('phone').text, name=ppt.find('agent').find('name').text)

                try:
                    appartment_type = Appartype.objects.get(app_type=self.get_appartment_type(property_data['property_type']))
                except Appartype.DoesNotExist:
                    appartment_type = Appartype.objects.create(app_type=self.get_appartment_type(property_data['property_type']))

                try:
                    sub_location = Sublocation.objects.get(name__iexact=property_data['community'], location=location)
                except Sublocation.DoesNotExist:
                    sub_location, _ = Sublocation.objects.get_or_create(name=property_data['community'], location=location)


                tower_name = None
                if 'property_name' in property_data and property_data['property_name']:
                    try:
                        tower_name = TowerName.objects.get(name__iexact=property_data['property_name'])
                    except TowerName.DoesNotExist:
                        if property_data['property_name'].strip():  # Check if property_name is not empty after stripping leading/trailing whitespace
                            tower_name = TowerName.objects.create(name=property_data['property_name'], sublocation=sub_location )
                
                description = ''
                if property_data['description_en']:
                    description = description.strip()
                    description = re.sub(
                    r"(?i)teona\s*&?\s*co\s*real\s*estate|teona\s*properties", 
                    "Cozy Properties", 
                    description
                )
                else:
                    description = ""
                
                    
                    
                
                # Create or update Property object
                property_obj, created = Properties.objects.update_or_create(
                    ref=property_data['reference_number'],
                    defaults={
                        'is_imported': True,
                        'agent': agent,
                        'permit_number':  property_data['permit_number'],
                        'status': self.get_offer_type(property_data.get('offering_type')),
                        'completion_status': property_data.get('completion_status', ''),
                        'amenities': get_amenities(property_data.get('amenities', '')),
                        'subtype': property_data.get('subtype', '-'),
                        'title': property_data['title_en'],
                        'description': description,
                        'size': property_data['size'],
                        'size_unit': 'SQFT',
                        'price': property_data['price'],
                        'furnished': property_data['furnished'] if 'furnished' in property_data else '',
                        'bedrooms': property_data['bedroom'] if 'bedroom' in property_data else '',
                        'bathroom': property_data['bathroom'] if 'bathroom' in property_data else '',
                      
                        'location': location,
                        'sub_location': sub_location,
                        'appartment_type': appartment_type,
                        'geopoints':property_data['geopoints'],

                    }
                )
                for idx, photo_elem in enumerate(ppt.findall('.//photo/url')):
                    url = photo_elem.text.strip() if photo_elem.text else ''
                    if url:
                        download_image_to_property(property_obj, url, sort_order=idx)
                        
                if tower_name is not None:
                    property_obj.tower_name = tower_name
                if (
    property_data
    and 'completion_status' in property_data
    and property_data['completion_status']
    and (
        'off plan' in property_data['completion_status']
        or 'off_plan_primary' in property_data['completion_status']
        or 'off_plan_secondary' in property_data['completion_status']
    )
):
                    property_obj.off_plan = True
                imported_refs.add(property_data['reference_number'])
                if not created:
                    # Object was updated, perform any additional update logic
                    pass
                    
                    try:
                        property_obj.full_clean()
                    except ValidationError as e:
                        # Handle the validation error
                        error_message = str(e)
                        print(error_message)
                    property_obj.save()
            
                    
                    
            Properties.objects.filter(is_imported=True).exclude(ref__in=imported_refs).delete()
    def get_team(self, prop_elem):
        """Determine the appropriate agent (Team) for a property."""
        agent_email = prop_elem.findtext('agent_email', '').strip()
        agent_name = prop_elem.findtext('agent', '').strip()

        team = None
        if agent_email:
            team = Team.objects.filter(email__iexact=agent_email).first()
        if not team and agent_name:
            team = Team.objects.filter(name__icontains=agent_name).first()

        if not team:
            team = Team.objects.first()
            if team:
                logger.warning(f"No matching agent found. Fallback to: {team.name}")
            else:
                logger.error("No team available in the system.")

        return team

    