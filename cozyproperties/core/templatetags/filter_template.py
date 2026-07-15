from django import template
register = template.Library()


@register.filter(name='get_buy_properties')
def get_buy_properties(apptypes):
    try:
        return apptypes.filter(properties__isnull=False, properties__status__icontains='Sale').distinct()
    except Exception:
        return '-'

@register.filter(name='get_rent_properties')
def get_rent_properties(apptypes):
    try:
        return apptypes.filter(properties__isnull=False, properties__status__icontains='Rent').distinct()
    except Exception:
        return '-'

@register.filter(name='split_by_comma')
def split_by_comma(value):
    try:
        return [amenity.strip(" '[]") for amenity in value.split(",")]
    except Exception:
        return '-'
    
    
    


@register.filter(name='get_status')
def get_status(status):
    try:
        if status and len(status):
            return status.split('-')[1]
        return ''
    except Exception:
        return '-'

@register.filter(name='filter_currency')
def filter_currency(num):
    try:
        return "{:,.2f}".format(int(num))
    except Exception:
        return '-'
    
    
@register.filter(name='amenities_list')
def amenities_list(value):
    # value is expected to be a list, but just in case, convert string JSON to list
    if isinstance(value, list):
        return value
    try:
        import json
        return json.loads(value)
    except Exception:
        return []
    

@register.filter(name='filter_pictures')
def filter_pictures(pictures, index=None):
    try:
        pictures = pictures.split('\n')
        if index:
            if index < len(pictures):
                return pictures[index]
        return pictures
    except Exception:
        return '-'

@register.filter(name='clean_geo_points')
def clean_geo_points(str):
    try:
        if str:
            return str.split(',')
    except Exception:
        return '-'

@register.filter(name='filter_phone_number')
def filter_phone_number(str):
    try:
        return str.replace('+', '')
    except Exception:
        return '-'

@register.filter(name='get_feature_details')
def get_feature_details(obj):
    try:
        data = obj.get_feature_details()
        if data:
            return enumerate(data, start=1)  # Start the index from 1
        else:
            return []
    except Exception:
        return '-'

@register.filter(name='get_project_details') 
def get_project_details(obj):
    try:
        data = obj.get_project_details()
        if data:
            return enumerate(data, start=1)  # Start the index from 1
        else:
            return []
    except Exception:
        return '-'

@register.filter(name='lower_str') 
def lower_str(str):
    try:
        return str.replace(' ', '').lower()
    except Exception:
        return '-'

@register.filter(name='clean_str_png')
def clean_str_png(str):
    try:
        return str.replace('/', '').replace('&', '')
    except Exception:
        return '-'
