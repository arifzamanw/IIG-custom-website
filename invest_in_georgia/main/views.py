"""
main/views.py

Views for the Invest In Georgia real estate platform.
Covers: home, property listing/search/detail, blog, news,
        static pages, language switching, and lead capture.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.core.cache import cache
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils import translation
from django.urls import reverse
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from decimal import Decimal, InvalidOperation
import json
import re

from .models import (
    Property, City, Amenity, Team, BlogPost,
    FeaturedPropertySection, MarketinsightSection,
    InvestmentSection, OverviewKeyBlog, OverviewKeySection,
    WhoWeArePage, ServicesPage, ContactPage,
    Subscriber, CallRequest, ConsultationBooking,
)
from main.utils.bitrix_api import create_bitrix_lead, create_bitrix_base_lead


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

# Shared sorting map reused across listing views
SORTING_OPTIONS = {
    "newest":       "-created_at",
    "min_price":    "price",
    "max_price":    "-price",
    "min_bed":      "bedrooms",
    "max_bed":      "-bedrooms",
    "min_bathroom": "bathroom",
    "max_bathroom": "-bathroom",
}


def _apply_sorting(properties, sort_by):
    """
    Apply sorting to a queryset based on the `sort_by` string.
    Handles the special 'featured' case and all standard sort keys.

    Args:
        properties: A Property queryset.
        sort_by (str): The sort key from the request GET params.

    Returns:
        Sorted queryset.
    """
    if sort_by == "featured":
        featured = properties.filter(featured=True).order_by("-created_at")
        return featured if featured.exists() else properties
    if sort_by in SORTING_OPTIONS:
        return properties.order_by(SORTING_OPTIONS[sort_by])
    return properties


def _group_by_city(properties):
    """
    Group a property queryset by city in Python (avoids N+1 queries).

    Args:
        properties: An iterable of Property objects.

    Returns:
        dict: {city_instance: [property, ...]}
    """
    result = {}
    for prop in properties:
        result.setdefault(prop.city, []).append(prop)
    return result


def _paginate(properties, request, per_page=9):
    """
    Paginate a queryset and return pagination context.

    Args:
        properties: A queryset to paginate.
        request: The current request (used to read ?page=).
        per_page (int): Number of items per page.

    Returns:
        tuple: (page_obj, start_index, end_index, total_count)
    """
    paginator = Paginator(properties, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    total = paginator.count
    start = (page_obj.number - 1) * per_page + 1
    end = min(page_obj.number * per_page, total)
    return page_obj, start, end, total


# ─────────────────────────────────────────────────────────────────────────────
# Home
# ─────────────────────────────────────────────────────────────────────────────

def home(request):
    """
    Homepage view.

    Loads all data needed for the homepage (agents, featured sections,
    blog posts, properties grouped by type). Heavy use of cache to
    avoid repeated DB hits on a high-traffic landing page.
    """
    # Cached lookups (10 min TTL)
    agents           = cache.get_or_set("agents",           lambda: Team.objects.all(),                          timeout=600)
    featured_property = cache.get_or_set("featured_property", lambda: FeaturedPropertySection.objects.first(),   timeout=600)
    marker_insight   = cache.get_or_set("marker_insight",   lambda: MarketinsightSection.objects.first(),        timeout=600)
    amenities        = cache.get_or_set("amenities",        lambda: Amenity.objects.prefetch_related("property_set"), timeout=600)
    blog_posts       = cache.get_or_set(
        "blog_posts",
        lambda: list(BlogPost.objects.all().order_by('-created_at')[:3]),
        timeout=600
    )

    # Load all properties with related data in a single query
    properties = Property.objects.all().select_related("city").prefetch_related("images", "floor_plans")
    property_types = properties.values('property_type').distinct()

    # Group by type in Python to avoid N+1
    properties_by_type = {}
    for prop in properties:
        properties_by_type.setdefault(prop.property_type, []).append(prop)

    return render(request, 'main/index.html', {
        'properties_by_type':  properties_by_type,
        'property_cities':     City.objects.all().distinct(),
        'blog_posts':          blog_posts,
        'property_types':      property_types,
        'Amenities':           amenities,
        'featured_property':   featured_property,
        'marker_insight':      marker_insight,
        'agents':              agents,
        'sub_cities':          None,
        'featured_section':    FeaturedPropertySection.objects.first(),
        'inevestment_section': InvestmentSection.objects.first(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Property listing
# ─────────────────────────────────────────────────────────────────────────────

def properties_and_projects(request):
    """
    General property listing page.

    Supports sorting via ?shorted_by= and pagination.
    Returns 9 properties per page.
    """
    properties     = Property.objects.all().only("title", "slug", "price", "location", "status", "image")
    property_types = properties.values_list('property_type', flat=True).distinct()
    property_cities = _group_by_city(properties)

    sort_by    = request.GET.get('shorted_by')
    properties = _apply_sorting(properties, sort_by)

    page_obj, start, end, total = _paginate(properties, request)

    return render(request, 'property/properties_and_projects.html', {
        'based_amenities':  Amenity.objects.all(),
        'property_types':   property_types,
        'property_cities':  property_cities,
        'properties':       page_obj,
        'start_index':      start,
        'end_index':        end,
        'total_properties': total,
    })


def popular_properties(request):
    """
    Listing page filtered to properties marked as popular (is_popular=True).

    Supports the same sorting options as the main listing.
    """
    properties = (
        Property.objects
        .filter(is_popular=True)
        .select_related("city")
        .prefetch_related("images", "floor_plans")
    )
    property_types  = properties.values_list('property_type', flat=True).distinct()
    property_cities = _group_by_city(properties)

    properties = _apply_sorting(properties, request.GET.get('shorted_by'))
    page_obj, start, end, total = _paginate(properties, request, per_page=8)

    return render(request, 'property/properties_and_projects.html', {
        'based_amenities':  Amenity.objects.all(),
        'property_types':   property_types,
        'property_cities':  property_cities,
        'properties':       page_obj,
        'start_index':      start,
        'end_index':        end,
        'total_properties': total,
        'is_popular':       True,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Property detail
# ─────────────────────────────────────────────────────────────────────────────

def property_detail(request, slug, status):
    """
    Property detail page (SEO-friendly slug URL).

    Fetches a single property by slug + status. Returns a 404-style
    not-found page if the property doesn't exist.

    Args:
        slug (str): URL slug of the property.
        status (str): Property status (e.g. 'available', 'sold').
    """
    try:
        chosen_property = Property.objects.get(slug=slug, status=status)
    except Property.DoesNotExist:
        return render(request, 'property/not_found.html')

    properties      = Property.objects.all()
    property_types  = properties.values_list('property_type', flat=True).distinct()
    property_cities = _group_by_city(properties)

    return render(request, 'property/detail.html', {
        'property':       chosen_property,
        'property_types': property_types,
        'property_cities': property_cities,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Property search
# ─────────────────────────────────────────────────────────────────────────────

def property_search(request):
    """
    Simple property search view.

    Filters by: free-text query, city, category, max price,
    bedrooms, and bathrooms. Supports sorting and pagination.
    """
    query     = request.GET.get('q', '').strip()
    city_id   = request.GET.get('city_selector', '')
    category  = request.GET.get('category_selector', '')
    max_price = request.GET.get('max_price_selector')
    bedroom   = request.GET.get('bedrooms', '')
    bathroom  = request.GET.get('bathrooms')
    sort_by   = request.GET.get('shorted_by')

    properties      = Property.objects.all()
    property_types  = properties.values_list('property_type', flat=True).distinct()
    property_cities = _group_by_city(properties)

    q_objects = Q()

    # Full-text search across key fields
    if query:
        terms = [t for t in re.findall(r'\w+', query) if len(t) > 1]
        for term in terms:
            q_objects |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(location__icontains=term) |
                Q(city__name__icontains=term) |
                Q(property_type__icontains=term) |
                Q(sale_type__icontains=term) |
                Q(status__icontains=term) |
                Q(amenities_description__icontains=term)
            )

    if city_id:
        q_objects &= Q(city_id=city_id)

    if category:
        q_objects &= Q(property_type=category)

    if max_price:
        try:
            q_objects &= Q(price__lte=int(max_price))
        except ValueError:
            pass

    if bedroom:
        try:
            b = int(bedroom)
            q_objects &= Q(bedrooms__gte=str(b)) if b >= 6 else Q(bedrooms=str(b))
        except ValueError:
            pass

    if bathroom:
        try:
            b = int(bathroom)
            q_objects &= Q(bathroom__gte=str(b)) if b >= 6 else Q(bathroom=str(b))
        except ValueError:
            pass

    properties = _apply_sorting(properties.filter(q_objects), sort_by)
    page_obj, start, end, total = _paginate(properties.only("id"), request)

    return render(request, 'property/properties_and_projects.html', {
        'based_amenities':  Amenity.objects.all(),
        'property_types':   property_types,
        'property_cities':  property_cities,
        'properties':       page_obj,
        'start_index':      start,
        'end_index':        end,
        'total_properties': total,
    })


def advanced_search(request):
    """
    Advanced property search with extended filters.

    Supports: multi-select cities, categories, bedrooms, bathrooms,
    price range, size range, furnishing, and amenities.
    Returns JSON on AJAX requests, HTML otherwise.
    """
    query      = request.GET.get('query', '').strip()
    city_ids   = request.GET.getlist('city_selector')
    categories = request.GET.getlist('category_selector')
    min_price  = request.GET.get('min_price')
    max_price  = request.GET.get('max_price')
    min_size   = request.GET.get('min_size')
    max_size   = request.GET.get('max_size')
    bedrooms   = request.GET.getlist('bedrooms')
    bathrooms  = request.GET.getlist('bathrooms')
    sort_by    = request.GET.get('shorted_by')
    amenities  = request.GET.getlist('amenities')
    furnishing = request.GET.get('furnishing', 'all')

    properties      = Property.objects.all()
    property_types  = properties.values_list('property_type', flat=True).distinct()
    property_cities = _group_by_city(properties)

    q_objects = Q()

    # Full-text search
    if query:
        for term in query.split():
            q_objects |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(location__icontains=term) |
                Q(city__name__icontains=term) |
                Q(property_type__icontains=term) |
                Q(sale_type__icontains=term) |
                Q(status__icontains=term) |
                Q(amenities_description__icontains=term)
            )

    if city_ids:
        q_objects &= Q(city_id__in=city_ids)

    if categories:
        q_objects &= Q(property_type__in=categories)

    if min_price:
        try:
            q_objects &= Q(price__gte=int(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            q_objects &= Q(price__lte=int(max_price))
        except ValueError:
            pass

    if furnishing and furnishing != "all":
        q_objects &= Q(furnished__iexact=furnishing)

    if min_size:
        try:
            q_objects &= Q(size__gte=Decimal(min_size))
        except (ValueError, InvalidOperation):
            pass

    if max_size:
        try:
            q_objects &= Q(size__lte=Decimal(max_size))
        except (ValueError, InvalidOperation):
            pass

    # Bedroom filter: exact match for < 6, gte for 6+
    if bedrooms:
        try:
            vals = [int(b) for b in bedrooms if b.isdigit()]
            exact = [str(b) for b in vals if b < 6]
            if exact:
                q_objects &= Q(bedrooms__in=exact)
            if any(b >= 6 for b in vals):
                q_objects |= Q(bedrooms__gte='6')
        except ValueError:
            pass

    # Bathroom filter: same logic as bedrooms
    if bathrooms:
        try:
            vals = [int(b) for b in bathrooms if b.isdigit()]
            exact = [str(b) for b in vals if b < 6]
            if exact:
                q_objects &= Q(bathroom__in=exact)
            if any(b >= 6 for b in vals):
                q_objects |= Q(bathroom__gte='6')
        except ValueError:
            pass

    if amenities:
        q_objects &= Q(amenities__id__in=[int(a) for a in amenities])

    properties = _apply_sorting(properties.filter(q_objects), sort_by)
    page_obj, start, end, total = _paginate(properties.only("id"), request)

    # Fetch full data only for the current page
    paginated_ids  = [p.id for p in page_obj]
    paginated_full = properties.filter(id__in=paginated_ids)

    # AJAX response (used by the frontend filter panel)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'properties': list(paginated_full.values(
                'id', 'title', 'price', 'size', 'city_id', 'image',
                'bathroom', 'city__name', 'property_type', 'bedrooms',
                'location', 'slug', 'status'
            )),
            'start_index':   start,
            'end_index':     end,
            'total_properties': total,
            'has_next':      page_obj.has_next(),
            'has_previous':  page_obj.has_previous(),
            'next_page':     page_obj.next_page_number() if page_obj.has_next() else None,
            'prev_page':     page_obj.previous_page_number() if page_obj.has_previous() else None,
            'current_page':  page_obj.number,
            'total_pages':   page_obj.paginator.num_pages,
        }, safe=False)

    return render(request, 'property/properties_and_projects.html', {
        'based_amenities':  Amenity.objects.all(),
        'property_types':   property_types,
        'property_cities':  property_cities,
        'properties':       page_obj,
        'start_index':      start,
        'end_index':        end,
        'total_properties': total,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Search helpers (JSON endpoints)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_featured_properties(request):
    """
    JSON endpoint that returns the HTML fragment for featured properties.
    Used by frontend widgets to lazy-load featured listings.
    """
    featured = Property.objects.filter(featured=True).only(
        "title", "slug", "price", "location", "status", "image"
    )
    html = render_to_string('property/properties_and_projects.html', {
        "featured_properties": featured
    })
    return JsonResponse({"html": html})


def get_cities(request):
    """
    JSON endpoint returning all cities as {id, name} pairs.
    Used to populate city dropdowns dynamically.
    """
    cities = City.objects.all().values("id", "name")
    return JsonResponse({"cities": list(cities)})


def search_suggestions(request):
    """
    JSON endpoint for search autocomplete suggestions.

    Returns matching properties (city, location, title) for a given
    query string. Falls back to all cities if no query is provided.
    """
    query   = request.GET.get('q', '').strip()
    results = []

    if query:
        properties = Property.objects.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(city__name__icontains=query)
        ).select_related('city')[:10]

        for prop in properties:
            results.append({
                "city":     prop.city.name if prop.city else "",
                "location": prop.location or "",
                "building": prop.title or "",
            })
    else:
        # No query → return all city names as suggestions
        results = [{"city": c.name} for c in City.objects.all()]

    return JsonResponse(results, safe=False)


# ─────────────────────────────────────────────────────────────────────────────
# Blog & News
# ─────────────────────────────────────────────────────────────────────────────

def blogs(request):
    """
    Blog listing page. Ordered by most recent first."""
    blog_posts = BlogPost.objects.only(
        'title', 'slug', 'image', 'content', 'created_at'
    ).order_by('-created_at')

    return render(request, 'main/blogs.html', {'blog_posts': blog_posts})


def blog_detail(request, slug):
    """
    Blog post detail page.

    Also loads up to 3 related posts sharing any of the same tags.

    Args:
        slug (str): URL slug of the blog post.
    """
    blog      = get_object_or_404(BlogPost, slug=slug)
    blog_tags = [t.strip() for t in (blog.tags or "").split(",") if t.strip()]

    related_posts = []
    if blog_tags:
        # Match any post that contains at least one of the same tags
        tag_pattern   = r"(" + "|".join(re.escape(t) for t in blog_tags) + ")"
        related_posts = BlogPost.objects.filter(
            tags__iregex=tag_pattern
        ).exclude(id=blog.id)[:3]

    return render(request, 'main/blog-single.html', {
        'blog':          blog,
        'related_posts': related_posts,
    })


def news(request):
    """
    News/overview page. Loads overview section and key blog entries from cache.
    """
    overview_services = cache.get_or_set(
        "overview_services",
        lambda: OverviewKeyBlog.objects.all(),
        timeout=600
    )
    overview = cache.get_or_set(
        "overview",
        lambda: OverviewKeySection.objects.first(),
        timeout=600
    )
    return render(request, 'main/news.html', {
        'overview_services': overview_services,
        'overview':          overview,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Static / info pages
# ─────────────────────────────────────────────────────────────────────────────

def who_we_are(request):
    """About us page with team members."""
    page   = cache.get_or_set('who_we_are_page', lambda: WhoWeArePage.objects.first(), timeout=600)
    agents = cache.get_or_set('agents',           lambda: Team.objects.all(),           timeout=600)
    return render(request, 'main/who_we_are.html', {'page': page, 'agents': agents})


def services(request):
    """Services page with ordered content blocks."""
    services_page   = ServicesPage.objects.first()
    services_blocks = services_page.blocks.all().order_by('order') if services_page else []
    return render(request, 'main/services.html', {
        'services_page':   services_page,
        'services_blocks': services_blocks,
    })


def contact_us(request):
    """Contact page."""
    return render(request, 'main/contact.html', {
        'contact_page': ContactPage.objects.first(),
    })


def privacy(request):
    """Privacy policy page."""
    return render(request, 'main/privacy.html')


def about(request):
    """About page."""
    return render(request, 'main/about.html')


# ─────────────────────────────────────────────────────────────────────────────
# Language switching
# ─────────────────────────────────────────────────────────────────────────────

def set_language_ajax(request):
    """
    AJAX endpoint to switch the active language.

    Expects POST with:
        lang_code (str): Target language code (e.g. 'en', 'ar').
        next (str):      URL to redirect to after switching.

    Returns JSON with redirect_url on success.
    """
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    lang_code  = request.POST.get('lang_code')
    next_url   = request.POST.get('next', '/')
    valid_langs = dict(settings.LANGUAGES).keys()

    if lang_code not in valid_langs:
        return JsonResponse({'status': 'error', 'message': 'Invalid language'}, status=400)

    translation.activate(lang_code)
    request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code

    response = JsonResponse({'status': 'ok', 'lang': lang_code, 'redirect_url': next_url})
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Lead capture / CRM
# ─────────────────────────────────────────────────────────────────────────────

def subscribe(request):
    """
    Newsletter subscription endpoint.

    Expects POST with a JSON body: {"email": "..."}
    Creates a Subscriber record if the email is new.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data  = json.loads(request.body)
        email = data.get("email", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not email:
        return JsonResponse({"error": "Email is required!"}, status=400)

    if Subscriber.objects.filter(email=email).exists():
        return JsonResponse({"error": "You are already subscribed!"}, status=400)

    try:
        Subscriber.objects.create(email=email, date_subscribed=now())
        return JsonResponse({"message": "Successfully subscribed!"}, status=200)
    except IntegrityError:
        return JsonResponse({"error": "Subscription error occurred."}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def submit_call_request(request):
    """
    Call-back request endpoint (AJAX only).

    Saves the request locally and pushes a lead to Bitrix24.
    Expects POST form data: name, phone, email, branch, way-of-contact.
    """
    if not (request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
        return JsonResponse({"success": False, "error": "Invalid request."})

    try:
        name        = request.POST.get('name')
        phone       = request.POST.get('phone')
        email       = request.POST.get('email')
        branch      = request.POST.get('branch')
        contact_way = request.POST.get('way-of-contact')

        if not all([name, phone, email, branch, contact_way]):
            raise ValueError("All fields are required.")

        # Persist locally
        CallRequest.objects.create(
            name=name, phone=phone, email=email,
            branch=branch, contact_way=contact_way
        )

        # Push to Bitrix24 CRM
        bitrix_response = create_bitrix_base_lead(
            full_name=name, email=email, phone=phone,
            branch=branch, contact_way=contact_way
        )

        if bitrix_response["success"]:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": bitrix_response["error"]})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def consultation_booking(request):
    """
    Consultation booking endpoint.

    Saves the booking locally and creates a Bitrix24 lead with
    optional agent and property context.

    Note: @csrf_exempt used here to support direct form POSTs
    from the property detail page (consider switching to AJAX + token).

    Expects POST form data:
        full_name, email, phone, message,
        agent_bitrix_id (optional),
        property_url (optional),
        property_name (optional).
    """
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    full_name       = request.POST.get('full_name')
    email           = request.POST.get('email')
    phone           = request.POST.get('phone')
    message         = request.POST.get('message')
    agent_bitrix_id = request.POST.get('agent_bitrix_id')
    property_url    = request.POST.get('property_url')
    property_name   = request.POST.get('property_name')

    if not all([full_name, email, phone, message]):
        return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

    # Prevent duplicate bookings from the same email
    if ConsultationBooking.objects.filter(email=email).exists():
        return JsonResponse({
            'status': 'error',
            'message': 'We already received your request. Our team will contact you soon.'
        })

    try:
        ConsultationBooking.objects.create(
            full_name=full_name, email=email,
            phone=phone, message=message,
            date_subscribed=now()
        )

        create_bitrix_lead(
            full_name, email, phone, message,
            agent_bitrix_id, property_name, property_url
        )

        return JsonResponse({'status': 'success', 'message': 'Booking successfully created!'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong. Please try again later.'})