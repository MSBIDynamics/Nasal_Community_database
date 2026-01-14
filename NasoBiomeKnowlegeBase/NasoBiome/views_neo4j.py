from django.http import HttpResponse
from .neo4j_integration import (
    push_all_body_sites_to_neo4j,
    push_all_diseases_to_neo4j,
    push_all_species_to_neo4j,
    push_all_products_to_neo4j,
    push_all_migrations_to_neo4j,
    push_all_interactions_to_neo4j,
    push_all_product_events_to_neo4j
)

def export_all_to_neo4j(request):
    """
    Export all models and relationships to Neo4j in correct order
    """
    # Push nodes and edges in dependency order
    push_all_body_sites_to_neo4j()
    push_all_diseases_to_neo4j()
    push_all_species_to_neo4j()
    push_all_products_to_neo4j()
    push_all_migrations_to_neo4j()
    push_all_interactions_to_neo4j()
    push_all_product_events_to_neo4j()

    return HttpResponse("All models have been exported to Neo4j successfully!")
