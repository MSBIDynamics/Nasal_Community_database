# serializers.py
from .models import Species

def species_to_dict(species: Species) -> dict:
    """
    Convert a single Species instance to a dictionary
    """
    return {
        "id": species.id,
        "name": species.name,
        "phyla": species.phyla,
        "genus": species.genus,
        "family": species.family,
        "genome_reference_link": species.genome_reference_link,
        "age_range": species.age_range,
        "description": species.description,
    }

def species_list_to_dict(species_list) -> list:
    """
    Convert a queryset or list of Species instances to a list of dictionaries
    """
    return [species_to_dict(s) for s in species_list]
