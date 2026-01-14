from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from NasoBiome.models import (
    Species, BodySite, Disease, Product,
    SpeciesInteraction, MigrationPattern, ProductEvent
)

class ThesisAdminSite(AdminSite):
    site_header = "Microbiome Knowledgebase Admin"
    site_title = "Microbiome Admin"
    index_title = "Dashboard"

    @method_decorator(never_cache)
    def index(self, request, extra_context=None):
        # Calculate KPIs
        kpi = {
            'species_count': Species.objects.count(),
            'body_sites_count': BodySite.objects.count(),
            'diseases_count': Disease.objects.count(),
            'products_count': Product.objects.count(),
            'interactions_count': SpeciesInteraction.objects.count(),
            'migrations_count': MigrationPattern.objects.count(),
            'product_events_count': ProductEvent.objects.count(),
            'total_nodes': (
                Species.objects.count() +
                BodySite.objects.count() +
                Disease.objects.count() +
                Product.objects.count()
            ),
            'total_relationships': (
                SpeciesInteraction.objects.count() +
                MigrationPattern.objects.count() +
                ProductEvent.objects.count()
            )
        }
        
        # Fetch recent activities
        recent_activities = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:10]

        extra_context = extra_context or {}
        extra_context['kpi'] = kpi
        extra_context['recent_activities'] = recent_activities
        
        return super().index(request, extra_context=extra_context)
    
    def logout(self, request, extra_context=None):
        """
        Passes admin site context variables to the logged_out.html template.
        """
        extra_context = extra_context or {}
        # Pass the same context variables as the base class does
        extra_context.update(self.each_context(request))
        return super().logout(request, extra_context)

admin_site = ThesisAdminSite(name='thesis_admin')
