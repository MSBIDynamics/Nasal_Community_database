from django import forms
from .models import (
    BodySite,
    Disease,
    Species,
    Product,
    SpeciesInteraction,
    MigrationPattern,
    ProductEvent,
)

TEXT_INPUT = {
    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
}

TEXTAREA = {
    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
    'rows': 3,
}

SELECT = {
    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
}

SELECT_MULTIPLE = {
    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
    'size': 6,
}

# BodySite Form
class BodySiteForm(forms.ModelForm):
    class Meta:
        model = BodySite
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={**TEXT_INPUT, 'placeholder': 'Enter body site name'}),
            'description': forms.Textarea(attrs={**TEXTAREA, 'placeholder': 'Describe the body site...'}),
        }

# Disease Form
class DiseaseForm(forms.ModelForm):
    class Meta:
        model = Disease
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={**TEXT_INPUT, 'placeholder': 'e.g. Crohn\'s disease'}),
            'description': forms.Textarea(attrs={**TEXTAREA}),
            'affected_site': forms.Select(attrs=SELECT),
            'mechanism_of_causation': forms.Textarea(attrs={**TEXTAREA}),
        }

# Species Form
class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={**TEXT_INPUT, 'placeholder': 'e.g. Escherichia coli'}),
            'phyla': forms.TextInput(attrs=TEXT_INPUT),
            'genus': forms.TextInput(attrs=TEXT_INPUT),
            'family': forms.TextInput(attrs=TEXT_INPUT),
            'genome_reference_link': forms.URLInput(attrs={**TEXT_INPUT, 'placeholder': 'https://ncbi.nlm.nih.gov/...'}),
            'age_range': forms.TextInput(attrs={**TEXT_INPUT, 'placeholder': 'e.g. infant, adult, elderly'}),
            'description': forms.Textarea(attrs=TEXTAREA),
            'origin_site': forms.Select(attrs=SELECT),
            'body_sites': forms.SelectMultiple(attrs=SELECT_MULTIPLE),
            'diseases': forms.SelectMultiple(attrs=SELECT_MULTIPLE),
            'products': forms.SelectMultiple(attrs=SELECT_MULTIPLE),
        }

# Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={**TEXT_INPUT, 'placeholder': 'e.g. Butyrate'}),
            'description': forms.Textarea(attrs=TEXTAREA),
            'mechanism_of_action': forms.Textarea(attrs=TEXTAREA),
        }

# Species Interaction Form
class SpeciesInteractionForm(forms.ModelForm):
    class Meta:
        model = SpeciesInteraction
        fields = "__all__"
        widgets = {
            'species_1': forms.Select(attrs=SELECT),
            'species_2': forms.Select(attrs=SELECT),
            'site': forms.Select(attrs=SELECT),
            'interaction_type': forms.Select(attrs=SELECT),
            'mechanism': forms.Textarea(attrs={**TEXTAREA, 'rows': 2}),
            'evidence': forms.Textarea(attrs={**TEXTAREA, 'rows': 2}),
            'associated_disease': forms.Select(attrs=SELECT),
        }

# Migration Pattern Form
class MigrationPatternForm(forms.ModelForm):
    class Meta:
        model = MigrationPattern
        fields = "__all__"
        widgets = {
            'species': forms.Select(attrs=SELECT),
            'from_site': forms.Select(attrs=SELECT),
            'to_site': forms.Select(attrs=SELECT),
            'mechanism': forms.TextInput(attrs={**TEXT_INPUT, 'placeholder': 'e.g. aspiration, bloodstream'}),
            'trigger_conditions': forms.Textarea(attrs={**TEXTAREA, 'rows': 2}),
            'evidence': forms.Textarea(attrs={**TEXTAREA, 'rows': 2}),
            'resulting_disease': forms.Select(attrs=SELECT),
        }

# Product Event Form
class ProductEventForm(forms.ModelForm):
    class Meta:
        model = ProductEvent
        fields = "__all__"
        widgets = {
            'species': forms.Select(attrs=SELECT),
            'interacting_species': forms.Select(attrs=SELECT),
            'site': forms.Select(attrs=SELECT),
            'product': forms.Select(attrs=SELECT),
            'disease': forms.Select(attrs=SELECT),
            'migration': forms.Select(attrs=SELECT),
            'interaction': forms.Select(attrs=SELECT),
            'mechanism': forms.Textarea(attrs={**TEXTAREA, 'rows': 2}),
            'evidence': forms.Textarea(attrs={**TEXTAREA, 'rows': 2}),
        }
