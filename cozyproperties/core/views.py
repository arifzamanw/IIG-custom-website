from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from core.models import Properties, Infos, Appartype, Location, Team, Sublocation, TowerName
from cozyproperties.settings import BASE_URL


def get_common_context(extra_context=None):
    """
    Common context used in many views to avoid repeating queries.
    Add extra_context dict to extend context as needed.
    """
    context = {
        'BASE_URL': BASE_URL,
        'all_properties': Properties.objects.all().distinct(),
        'infos': Infos.objects.all(),
        'apptype': Appartype.objects.all().distinct(),
        'locations': Location.objects.all().distinct(),
        'team': Team.objects.all().distinct(),
        'sub_locations': Sublocation.objects.all().distinct(),
        'towers': TowerName.objects.all().distinct(),
    }
    if extra_context:
        context.update(extra_context)
    return context


def home(request):
    return render(request, 'index.html', get_common_context())


def get_property_by_id(request, property_code):
    property_obj = get_object_or_404(
        Properties.objects.prefetch_related('images'),
        id=property_code
    )
    context = get_common_context({'property': property_obj})
    return render(request, 'property.html', context)


def get_properties_by_location(request, location_code):
    properties = Properties.objects.filter(location__id=location_code).distinct()
    context = get_common_context({'properties': properties})
    return render(request, 'properties.html', context)


def get_properties_by_type(request, type_code, status):
    properties = Properties.objects.filter(
        appartment_type__id=type_code,
        status__icontains=status
    ).distinct()
    context = get_common_context({'properties': properties})
    return render(request, 'properties.html', context)


def all_properties(request):
    properties = Properties.objects.all().distinct()
    context = get_common_context({'properties': properties})
    return render(request, 'properties.html', context)


def all_locations(request):
    # Locations page might not need properties, but you can add if needed
    context = get_common_context()
    return render(request, 'locations.html', context)


def buy(request):
    return render(request, 'index.html')


def rent(request):
    return render(request, 'index.html')


def sell_lease(request):
    return render(request, 'selllease.html', get_common_context())


def offplan_all(request):
    off_plans = Properties.objects.filter(off_plan=True).distinct()
    context = get_common_context({'off_plans': off_plans})
    return render(request, 'properties.html', context)


def offplan(request, offplan_id):
    # You had just a print here, consider implementing or removing this view
    # Or you can show a detail page for offplan if exists:
    offplan_obj = get_object_or_404(Properties, id=offplan_id, off_plan=True)
    context = get_common_context({'property': offplan_obj})
    return render(request, 'property.html', context)


def about(request):
    return render(request, 'index.html', get_common_context())


def contact_us(request):
    return render(request, 'contact.html', get_common_context())


def who_we_are(request):
    return render(request, 'whoweare.html', get_common_context())


def team(request):
    return render(request, 'team.html', get_common_context())


def our_version(request):
    return render(request, 'vision.html', get_common_context())


def our_mission(request):
    return render(request, 'mission.html', get_common_context())


def core_value(request):
    return render(request, 'corevalue.html', get_common_context())


def join_us(request):
    return render(request, 'joinus.html', get_common_context())


def search(request):
    if request.method == 'GET':
        city = request.GET.get('selected_city')
        p_status = request.GET.get('property_status')
        p_type = request.GET.get('property_type')

        filters = {}
        if city:
            filters['sub_location__name__iexact'] = city
        if p_status:
            filters['status__icontains'] = p_status
        if p_type:
            filters['appartment_type__app_type__icontains'] = p_type

        properties = Properties.objects.filter(**filters).distinct() if filters else Properties.objects.all().distinct()

        context = get_common_context({
            'properties': properties,
            "city": city,
            "p_status": p_status,
            "p_type": p_type
        })

        return render(request, 'properties.html', context)

    # Optional: Handle POST or other methods if needed
    return render(request, 'properties.html', get_common_context())


def send_email(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        send_mail(
            'New ContactForm from the website',
            f'Subject: {subject}\nName: {firstname} {lastname}\nEmail: {email}\nMessage: {message}',
            'lead@cozyproperties.ae',
            ['info@cozyproperties.ae'],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def infos(request, info_code):
    info_obj = get_object_or_404(Infos, code=info_code)
    context = get_common_context({'info': info_obj})
    return render(request, 'infos.html', context)


def send_lead_email(request):
    if request.method == 'POST':
        property_type = request.POST.get('radios')
        arrival_date = request.POST.get('arrivalDate')
        firstname = request.POST.get('fname')
        lastname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        send_mail(
            'New lead from the website',
            f'Property Type: {property_type}\nArrival Date: {arrival_date}\nName: {firstname} {lastname}\nEmail: {email}\nPhone: {phone}\nMessage: {message}',
            'lead@cozyproperties.ae',
            ['info@cozyproperties.ae'],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
