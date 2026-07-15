from django.urls import path
from core.views import *


app_name = 'core'
urlpatterns = [
    path('', home),
    path('all-properties', all_properties, name='all-properties'),
    path('all-locations', all_locations, name='all-locations'),
    path('property/<str:property_code>', get_property_by_id, name='get-property-by-code'),

    path('type/<str:type_code>/properties/<str:status>', get_properties_by_type, name='get-properties-by-type'),
    path('properties/location/<str:location_code>', get_properties_by_location, name='get-properties-by-location'),
    path('sell/lease/', sell_lease, name='sell-lease'),
    path('offplan/all/', offplan_all, name='off-plan'),
    path('offplan/<str:offpan_code>', offplan, name='offplan-by-code'),



    path('who-we-are', who_we_are, name='who-we-are'),
    path('team', team, name='team'),
    path('version', our_version, name='our-version'),
    path('mission', our_mission, name='our-mission'),
    path('core-value', core_value, name='core-value'),
    path('join-us', join_us, name='join-us'),
    path('infos/<str:info_code>', infos, name='infos-by-code'),




    path('contact-us', contact_us, name='contact'),
    path('sendmail', send_email, name='send_email'),
    path('sendleadmail', send_lead_email, name='send_lead_email'),
    path('search', search, name='search'),

]
