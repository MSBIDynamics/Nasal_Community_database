from django.contrib import admin
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from NasoBiomeKnowlegeBase.admin_site import admin_site
from .models import Species, BodySite, Disease, Product, MigrationPattern, SpeciesInteraction, ProductEvent

# Register built-in Django models
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("formatted_last_login", "formatted_date_joined")

    # Override fieldsets to remove 'password'
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('formatted_last_login', 'formatted_date_joined')}),
    )

    @admin.display(description="Last login")
    def formatted_last_login(self, obj):
        if not obj.last_login:
            return "—"
        return date_format(localtime(obj.last_login), "DATETIME_FORMAT")

    @admin.display(description="Date joined")
    def formatted_date_joined(self, obj):
        return date_format(localtime(obj.date_joined), "DATETIME_FORMAT")

admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, GroupAdmin)


# Custom Admin Classes

class BodySiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'


class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'affected_site', 'description_preview')
    list_filter = ('affected_site',)
    search_fields = ('name', 'description', 'mechanism_of_causation')
    ordering = ('name',)
    autocomplete_fields = ['affected_site']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Medical Details', {
            'fields': ('affected_site', 'mechanism_of_causation')
        }),
    )
    
    def description_preview(self, obj):
        return obj.description[:80] + '...' if len(obj.description) > 80 else obj.description
    description_preview.short_description = 'Description'


class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'phyla', 'genus', 'family', 'origin_site', 'age_range')
    list_filter = ('phyla', 'genus', 'origin_site')
    search_fields = ('name', 'phyla', 'genus', 'family', 'description')
    ordering = ('name',)
    autocomplete_fields = ['origin_site']
    filter_horizontal = ('body_sites', 'diseases', 'products')
    
    fieldsets = (
        ('Taxonomic Information', {
            'fields': ('name', 'phyla', 'genus', 'family')
        }),
        ('Reference & Description', {
            'fields': ('genome_reference_link', 'age_range', 'description')
        }),
        ('Location & Sites', {
            'fields': ('origin_site', 'body_sites'),
            'description': 'Specify where this species is found'
        }),
        ('Associations', {
            'fields': ('diseases', 'products'),
            'description': 'Related diseases and products'
        }),
    )


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'mechanism_preview')
    search_fields = ('name', 'description', 'mechanism_of_action')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Mechanism', {
            'fields': ('mechanism_of_action',)
        }),
    )
    
    def description_preview(self, obj):
        return obj.description[:60] + '...' if len(obj.description) > 60 else obj.description
    description_preview.short_description = 'Description'
    
    def mechanism_preview(self, obj):
        return obj.mechanism_of_action[:60] + '...' if len(obj.mechanism_of_action) > 60 else obj.mechanism_of_action
    mechanism_preview.short_description = 'Mechanism'


class SpeciesInteractionAdmin(admin.ModelAdmin):
    list_display = ('species_1', 'species_2', 'interaction_type', 'site', 'associated_disease')
    list_filter = ('interaction_type', 'site', 'associated_disease')
    search_fields = ('species_1__name', 'species_2__name', 'mechanism', 'evidence')
    autocomplete_fields = ['species_1', 'species_2', 'site', 'associated_disease']
    ordering = ('species_1__name',)
    
    fieldsets = (
        ('Interacting Species', {
            'fields': ('species_1', 'species_2', 'site')
        }),
        ('Interaction Details', {
            'fields': ('interaction_type', 'mechanism', 'evidence')
        }),
        ('Disease Association', {
            'fields': ('associated_disease',)
        }),
    )


class MigrationPatternAdmin(admin.ModelAdmin):
    list_display = ('species', 'from_site', 'to_site', 'resulting_disease', 'mechanism_preview')
    list_filter = ('from_site', 'to_site', 'resulting_disease')
    search_fields = ('species__name', 'mechanism', 'trigger_conditions', 'evidence')
    autocomplete_fields = ['species', 'from_site', 'to_site', 'resulting_disease']
    ordering = ('species__name',)
    
    fieldsets = (
        ('Migration Path', {
            'fields': ('species', 'from_site', 'to_site')
        }),
        ('Migration Details', {
            'fields': ('mechanism', 'trigger_conditions', 'evidence')
        }),
        ('Disease Outcome', {
            'fields': ('resulting_disease',)
        }),
    )
    
    def mechanism_preview(self, obj):
        return obj.mechanism[:50] + '...' if obj.mechanism and len(obj.mechanism) > 50 else obj.mechanism or '-'
    mechanism_preview.short_description = 'Mechanism'


class ProductEventAdmin(admin.ModelAdmin):
    list_display = ('species', 'product', 'site', 'disease', 'interacting_species', 'has_migration', 'has_interaction')
    list_filter = ('site', 'disease', 'product')
    search_fields = ('species__name', 'product__name', 'mechanism', 'evidence')
    autocomplete_fields = ['species', 'interacting_species', 'site', 'product', 'disease', 'migration', 'interaction']
    ordering = ('species__name',)
    
    fieldsets = (
        ('Primary Information', {
            'fields': ('species', 'product', 'site')
        }),
        ('Interactions & Partnerships', {
            'fields': ('interacting_species', 'interaction', 'migration'),
            'description': 'Optional: Link to related interactions or migrations'
        }),
        ('Disease & Mechanism', {
            'fields': ('disease', 'mechanism', 'evidence')
        }),
    )
    
    def has_migration(self, obj):
        return True if obj.migration else False
    has_migration.short_description = 'Migration'
    has_migration.boolean = True
    
    def has_interaction(self, obj):
        return True if obj.interaction else False
    has_interaction.short_description = 'Interaction'
    has_interaction.boolean = True


# Register all models with the custom admin site
admin_site.register(BodySite, BodySiteAdmin)
admin_site.register(Disease, DiseaseAdmin)
admin_site.register(Species, SpeciesAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(SpeciesInteraction, SpeciesInteractionAdmin)
admin_site.register(MigrationPattern, MigrationPatternAdmin)
admin_site.register(ProductEvent, ProductEventAdmin)
