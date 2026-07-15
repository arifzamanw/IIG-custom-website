from django.urls import path
from . import views

urlpatterns = [

    # ── Home ──────────────────────────────────────────────────────────────
    path('', views.home, name='home'),

    # ── Properties ────────────────────────────────────────────────────────
    path('properties/',                         views.properties_and_projects, name='properties_and_projects'),
    path('property/<slug:slug>/<str:status>/',  views.property_detail,         name='property_detail'),
    path('search/',                             views.property_search,         name='property_search'),
    path('advanced-search/',                    views.advanced_search,         name='advanced_search'),
    path('popular/',                            views.popular_properties,      name='popular_properties'),

    # ── Search helpers (JSON) ──────────────────────────────────────────────
    path('get-cities/',                         views.get_cities,                  name='get_cities'),
    path('ajax/search-suggestions/',            views.search_suggestions,          name='search_suggestions'),
    path('fetch-featured-properties/',          views.fetch_featured_properties,   name='fetch_featured_properties'),

    # ── Blog & News ────────────────────────────────────────────────────────
    path('blogs/',              views.blogs,       name='blogs'),
    path('blog/<slug:slug>/',   views.blog_detail, name='blog_detail'),
    path('news/',               views.news,        name='news'),

    # ── Static pages ──────────────────────────────────────────────────────
    path('who-we-are/',  views.who_we_are,  name='who_we_are'),
    path('services/',    views.services,    name='services'),
    path('contact-us/',  views.contact_us,  name='contact_us'),
    path('privacy/',     views.privacy,     name='privacy'),
    path('about/',       views.about,       name='about'),

    # ── Lead capture / CRM ────────────────────────────────────────────────
    path('subscribe/',              views.subscribe,            name='subscribe'),
    path('consultation-booking/',   views.consultation_booking, name='consultation_booking'),
    path('submit-call-request/',    views.submit_call_request,  name='submit_call_request'),

    # ── Language ──────────────────────────────────────────────────────────
    path('set-language/',   views.set_language_ajax, name='set_language_ajax'),

]