import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "real_estate.settings")
django.setup()

import json
from django.core.files import File
from django.utils.text import slugify

from main.models import Property, PropertyImage, PropertyFLoorPlan, Amenity, City, Team


def create_property(data):
    """Create a property, images, floor plans, and amenities"""

    # Ensure City exists
    city_name = data.get("city")
    city = None
    if city_name:
        city, _ = City.objects.get_or_create(name=city_name.strip())

    # Ensure Agent exists (optional)
    agent_name = data.get("agent")
    agent = None
    if agent_name:
        agent, _ = Team.objects.get_or_create(name=agent_name.strip())

    # Create Property
    prop = Property.objects.create(
        title=data["title"],
        description=data.get("description", ""),
        price=data.get("price"),
        city=city,
        location=data.get("location"),
        featured=data.get("featured", False),
        property_type=data.get("property_type"),
        sale_type=data.get("sale_type"),
        location_latitude=data.get("location_latitude"),
        location_longitude=data.get("location_longitude"),
        size=data.get("size"),
        status=data.get("status", "available"),
        amenities_description=data.get("amenities_description"),
        image=data.get("image"),
        agent=agent,
        ref=data.get("ref"),
        furnished=data.get("furnished"),
        bedrooms=data.get("bedrooms"),
        bathroom=data.get("bathroom"),
        completion_date=data.get("completion_date"),
        parking=data.get("parking"),
        is_imported=True,
        youtube_video=data.get("youtube_video"),
        is_popular=data.get("is_popular", False),
        translations=json.loads(data.get("translations", "{}")),
        keywords=data.get("keywords", ""),
    )

    # Slug
    if not prop.slug or "none" in prop.slug:
        prop.slug = slugify(f"{prop.title}-{prop.id}")
        prop.save(update_fields=["slug"])

    # Add Amenities
    amenities = data.get("amenities", [])
    for a in amenities:
        amenity, _ = Amenity.objects.get_or_create(name=a.strip())
        prop.amenities.add(amenity)

    # Add Images
    for img in data.get("images", []):
        PropertyImage.objects.create(
            property=prop,
            image=img["path"],
            image_alt=img.get("alt", ""),
        )

    # Add Floor Plans
    for fp in data.get("floor_plans", []):
        PropertyFLoorPlan.objects.create(
            property=prop,
            title=fp.get("title"),
            image=fp["path"],
            image_alt=fp.get("alt", ""),
        )

    return prop


def run():
    # List of all properties
    properties = [
  {
    "title": "The Pinnacle of Luxury Living — Limited Edition Penthouse",
    "description": "Own the crown jewel of VR Shekvetili Forest~Beach • By Paragraph—a truly rare Three-Bedroom Penthouse offering unmatched elegance and exclusivity. Spanning an extraordinary 385.8 sq.m (4,152 sq.ft), including 222.4 sq.m (2,393 sq.ft) of expansive outdoor space, this top-floor residence delivers panoramic sea and forest views, ultimate privacy, and a refined lifestyle beyond compare. Thoughtfully designed in turnkey condition with premium finishes, this is a sanctuary for those who seek the extraordinary. Ideal for high-net-worth investors, this limited-edition penthouse offers exceptional ROI potential, driven by prime location, luxury demand, and resort-style living beside the renowned Paragraph Resort & Spa. With flexible payment terms, 5% rental income tax, and no ownership restrictions, this is your chance to secure a legacy asset in Georgia’s most coveted destination. Completion: August 2027.",
    "price": 2810000,
    "city": "Shekvetili",
      "latitude": 41.8037,
      "longitude": 41.7752,
      "location": "Shekvetili, Guria Region, Georgia",
    "property_type": "Penthouse",
    "sale_type": "BUY",
    "size_sqm": 385.8,
    "size_sqft": 4152,
    "bedrooms": 3,
    "bathrooms": 3,
    "furnished": True,
    "completion_date": "August 2027",
    "status": "Available",
    "featured": False,
    "parking": True,
    "youtube_video": "",
    "is_popular": False,
    "agent": "Teona Buzaladze",
    "amenities": [
      "BASEMENT", "BASEMENT PARKING", "BEACH ACCESS", "CARPETS", "CITY VIEW",
      "COMMUNITY VIEW", "DRIVERS ROOM", "EAST ORIENTATION", "FULLY FITTED KITCHEN",
      "GARDEN VIEW", "GAZEBO", "GOLF VIEW", "HEATING", "INDOOR SWIMMING POOL",
      "MAINTENANCE", "MARBLE FLOORS", "NEAR AIRPORT", "NEAR GOLF", "NEAR HOSPITAL",
      "NEAR MALL", "NEAR METRO", "NEAR MOSQUE", "NEAR PUBLIC TRANSPORTATION",
      "NEAR RESTAURANTS", "NEAR SCHOOL", "NEAR SUPERMARKET", "NEAR VETERINARY",
      "NORTH ORIENTATION", "ON HIGH FLOOR", "ON LOW FLOOR", "ON MID FLOOR",
      "PRIVATE GARAGE", "PUBLIC PARKS", "SAUNA", "SOUTH ORIENTATION",
      "STEAM ROOM", "STORAGE ROOM", "TERRACE", "UPGRADED INTERIOR", "WEST ORIENTATION",
      "WITHIN A COMPOUND", "WOOD FLOORING", "BALCONY", "BBQ AREA", "BUILT IN WARDROBES",
      "CABLE-READY", "CENTRAL AIR CONDITIONING", "CHILDREN’S PLAY AREA", "CHILDREN’S POOL",
      "CONCIERGE SERVICE", "COVERED PARKING", "KITCHEN APPLIANCES", "LOBBY IN BUILDING",
      "MAID SERVICE", "MAIDS ROOM", "PETS ALLOWED", "PRIVATE GARDEN", "PRIVATE GYM",
      "PRIVATE JACUZZI", "PRIVATE POOL", "SEA/WATER VIEWS", "SECURITY", "SHARED GYMS",
      "SHARED SWIMMING POOLS", "SPA", "STUDY", "VASTU-COMPLIANT", "VIEW OF LANDMARK",
      "WALK IN CLOSET", "Fine Dining Restaurants", "Exclusive Spa", "Private pool",
      "Indoor Pool", "Riviera Beach Pool", "Private Valet and Public Valet",
      "Bugatti Exhibition Gallery", "VIP Owners’ Lounge", "5* Restaurant and Cafe",
      "Spa Lounge", "Kids Play Area", "Communal pools", "Sandy Beach Pools",
      "25 m Lap Swimming Pool", "Paddle Courts", "Squash Courts", "Private Cafe Lounge",
      "Gymnasium", "Wellness Center", "Meeting Rooms", "Fitness Centres", "Sports Park",
      "Play Areas", "Swimming Pools", "Parks and open space", "Parking area",
      "Water Play Areas", "Running Track", "Multi-use games and Sports Lawns",
      "Tennis and Squash Courts", "Half-Court Basketball", "Skateable Landscape",
      "Health Care Centres", "Ample Parking Spaces", "Retail Outlets", "BQQ Area",
      "Parks and Gardens", "Bicycle & Running Tracks", "Basketball Court", "Cycling Trails",
      "Gardens and Parks", "Jogging Trails", "Kids Park", "Outdoor Gymnasium",
      "Outdoor Sitting Area", "Restaurant and Cafe", "Schools and Institutes", "Spa and Sauna",
      "Tennis Courts", "Rooftop Restaurants", "Indoor and outdoor swimming pool",
      "Designer brand services facilities", "Healthcare services", "5-star hospitality experience",
      "Beautifully Landscaped Gardens", "State of the art fitness centre", "Clubhouse",
      "Gate House", "Lagoon Beach", "Gymnasiums", "Parking Space", "Exclusive Private Gardens",
      "Running Tracks", "Fitness Centers", "Sports Courts", "Private Beach Access", "Infinity Pool",
      "BBQ and Outdoor Dining Area", "Media Room", "Elevator", "Landscaped Terraces", "Adventure Park",
      "Retail Promenade", "Ripe Market", "Community Clubhouse", "Sports Areas", "Event Lawn & Event Island",
      "Lagoon Clubhouse", "Floating Decks", "Music Room", "Outdoor Swimming Pools",
      "Kids Swimming pool", "Private 1,200m Sandy Beach", "Access to 5-Star Paragraph Resort & Spa",
      "Indoor & Outdoor Swimming Pools", "Flexible Payment Plans", "Cycling & Nature Walking Trails",
      "Family & Kids Play Areas", "Panoramic Sea & Forest Views", "Fully Furnished Turnkey Apartments",
      "Luxury Spa & Wellness Center"
    ],
    "images": [
      "properties_images/e86c6d25f8e84dec8239bdc363d7b8e5.jpg",
      "properties_images/290eedc6a7b74a9bab9c07d8c50a4725.jpg",
      "properties_images/b3890b3d06cf4804821bff67abe5f724.jpg",
      "properties_images/7f0e25e668d8442f95b39512075f5dd7.jpg",
      "properties_images/b7e957626b7e43b2b2a737b5dc16a101.jpg",
      "properties_images/45427f5bc8144bca9b072e56e3e6740a.jpg",
      "properties_images/172bce07fb96430e8ac345f9412c6bc5.jpg"
    ],
    "floor_plans": [
      {
        "title": "Floor Plan",
        "image": "properties_floors/mk7qkxfumqwqc3zxfwd0_suAIlK1.jpg"
      }
    ],
    "slug": "the-pinnacle-of-luxury-living-limited-edition-penthouse-none",
  }
];


    for prop_data in properties:
        p = create_property(prop_data)
        print(f"Imported property: {p.title}")


if __name__ == "__main__":
    run()
