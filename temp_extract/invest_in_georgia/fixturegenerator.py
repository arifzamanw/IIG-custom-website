import json
import random
from datetime import datetime

fixture = []
now = datetime.now().isoformat()

# ---------------------------
# Helper functions
# ---------------------------
def add_model(model_name, pk, fields):
    fixture.append({
        "model": f"app.{model_name.lower()}",
        "pk": pk,
        "fields": fields
    })

def random_price():
    return round(random.uniform(50000, 2000000), 2)

def random_size():
    return round(random.uniform(50, 500), 2)

# ---------------------------
# Cities
# ---------------------------
cities = ["Tbilisi", "Gudauri", "Batumi"]
for idx, city in enumerate(cities, start=1):
    add_model("City", idx, {
        "name": city,
        "translations": {}
    })

# ---------------------------
# Amenities
# ---------------------------
amenities_list = ["Swimming Pool", "Gym", "Parking", "WiFi", "Garden", "Security", "Sauna", "Elevator"]
for idx, name in enumerate(amenities_list, start=1):
    add_model("Amenity", idx, {
        "name": name,
        "translations": {}
    })

# ---------------------------
# Team Members
# ---------------------------
team_members = [
    {"name": "John Doe", "position": "Agent", "caption": "Top real estate agent", "email": "john@example.com"},
    {"name": "Jane Smith", "position": "Agent", "caption": "Luxury property specialist", "email": "jane@example.com"},
]
for idx, member in enumerate(team_members, start=1):
    add_model("Team", idx, {
        "name": member["name"],
        "position": member["position"],
        "caption": member["caption"],
        "socials": "{}",
        "phone": "123456789",
        "email": member["email"],
        "license_no": "{}",
        "picture": None,
        "translations": {},
        "bitrix_id": None
    })

# ---------------------------
# Properties
# ---------------------------
property_pk = 1
for city_idx, city_name in enumerate(cities, start=1):
    for i in range(4):  # 4 properties per city
        prop_title = f"{city_name} Property {i+1}"
        price = random_price()
        size = random_size()
        amenity_ids = random.sample(range(1, len(amenities_list)+1), k=4)
        add_model("Property", property_pk, {
            "title": prop_title,
            "slug": prop_title.lower().replace(" ", "-"),
            "description": f"Beautiful {prop_title} in {city_name}",
            "price": price,
            "city": city_idx,
            "location": f"{city_name}, District {i+1}",
            "featured": random.choice([True, False]),
            "property_type": random.choice(["apartment","house","villa"]),
            "sale_type": random.choice(["buy","rent"]),
            "location_latitude": "",
            "location_longitude": "",
            "size": size,
            "status": "available",
            "amenities": amenity_ids,
            "amenities_description": "Includes all modern amenities",
            "image": None,
            "created_at": now,
            "agent": random.choice([1,2]),
            "ref": None,
            "furnished": None,
            "bedrooms": str(random.randint(1,5)),
            "bathroom": str(random.randint(1,3)),
            "completion_date": None,
            "parking": None,
            "is_imported": False,
            "youtube_video": None,
            "is_popular": random.choice([True, False]),
            "translations": {},
            "keywords": f"{city_name}, property, real estate"
        })
        property_pk += 1

# ---------------------------
# Projects
# ---------------------------
projects = [
    {"title": "Luxury Living", "description": "Premium residential project", "location": "Tbilisi", "price_range": "100000-500000"},
    {"title": "Mountain Escape", "description": "Cozy villas in Gudauri", "location": "Gudauri", "price_range": "80000-300000"},
]
for idx, project in enumerate(projects, start=1):
    property_ids = random.sample(range(1, property_pk), k=4)
    add_model("Project", idx, {
        "title": project["title"],
        "description": project["description"],
        "location": project["location"],
        "price_range": project["price_range"],
        "start_date": now.split("T")[0],
        "end_date": now.split("T")[0],
        "featured": random.choice([True, False]),
        "properties": property_ids,
        "translations": {}
    })

# ---------------------------
# BlogPosts
# ---------------------------
blog_posts = [
    {"title": "Market Trends 2025", "content": "Insights on real estate market trends."},
    {"title": "Buying Tips", "content": "How to buy your dream property easily."},
    {"title": "Luxury Homes", "content": "Top luxury homes available now."},
]
for idx, blog in enumerate(blog_posts, start=1):
    add_model("BlogPost", idx, {
        "title": blog["title"],
        "slug": blog["title"].lower().replace(" ","-"),
        "content": blog["content"],
        "author": random.choice([1,2]),
        "created_at": now,
        "updated_at": now,
        "image": None,
        "translations": {}
    })

# ---------------------------
# Subscribers
# ---------------------------
subscribers = ["alice@example.com", "bob@example.com", "charlie@example.com"]
for idx, email in enumerate(subscribers, start=1):
    add_model("Subscriber", idx, {
        "email": email,
        "date_subscribed": now
    })

# ---------------------------
# Save fixture
# ---------------------------
with open("full_fixture.json", "w") as f:
    json.dump(fixture, f, indent=2)

print("Fixture generated: full_fixture.json")
