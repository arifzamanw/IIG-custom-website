"""
real_estate/urls.py

Root URL configuration for the Invest In Georgia platform.

URL structure:
  /              → redirects to /en/
  /i18n/         → Django language switching
  /{lang}/       → all main app routes (language-prefixed)
  /{lang}/admin/ → Django admin
  /{lang}/career/    → careers app
  /{lang}/chaining/  → smart_selects (chained dropdowns)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect


def redirect_to_default_language(request):
    """Redirect bare root URL to the default language prefix (/en/)."""
    return redirect("/en/")


# ── Base patterns (no language prefix) ───────────────────────────────────────
urlpatterns = [
    path('',      redirect_to_default_language),
    path('i18n/', include('django.conf.urls.i18n')),
]

# ── Language-prefixed patterns ────────────────────────────────────────────────
urlpatterns += i18n_patterns(
    path('admin/',    admin.site.urls),
    path('career/',   include('careers.urls')),
    path('chaining/', include('smart_selects.urls')),
    path('',          include('main.urls')),
    prefix_default_language=True,
)

# ── Media files (development only) ───────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)