from django import template
from django.contrib import admin
from django.apps import apps
from django.urls import reverse
from NasoBiomeKnowlegeBase.admin_site import admin_site

register = template.Library()

@register.inclusion_tag('admin/includes/sidebar_nav.html', takes_context=True)
def admin_sidebar(context):
    """
    Renders the sidebar navigation with available apps and models,
    mimicking the native Django admin's app_list behavior but for a custom sidebar.
    """
    request = context.get('request')
    if not request:
        return {}

    available_apps = admin_site.get_app_list(request)
    
    active_path = request.path

    return {
        'available_apps': available_apps,
        'request': request,
        'active_path': active_path,
    }
