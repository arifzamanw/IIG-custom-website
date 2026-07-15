from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ObjectDoesNotExist
from .models import Country


# class SubdomainMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         host = request.get_host().split('.')
#         subdomain = host[0] if len(host) > 1 else None
#         if not subdomain or subdomain == 'demo' or subdomain == 'investingeorgia' or subdomain=='9055-2a02-8428-efee-ec01-bd48-9ea0-4ae5-5224':
#             subdomain= 'georgia'
#         if subdomain:
#             try:
#                 request.country = Country.objects.get(name__iexact=subdomain.capitalize())
#             except ObjectDoesNotExist:
#                 request.country = 'georgia'
#         else:
#             request.country ='georgia'




