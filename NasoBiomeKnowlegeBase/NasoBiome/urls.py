from django.urls import path
from . import views

urlpatterns = [
    
    # Home
    
    path('', views.home, name='home'),


    # Species

    path('species/', views.get_all_species, name='get_all_species'),
    path('species/add/', views.add_species, name='add_species'),
    path('species/<int:id>/', views.get_species_by_id, name='get_species_by_id'),
    path('species/export/', views.export_species_to_neo4j, name='export_species_to_neo4j'),

    
    # Body Sites

    path('bodysites/', views.get_all_body_sites, name='get_all_body_sites'),
    path('bodysites/add/', views.add_body_site, name='add_body_site'),
    path('bodysites/<int:id>/', views.get_body_site_by_id, name='get_body_site_by_id'),
    path('bodysites/export/', views.export_body_sites_to_neo4j, name='export_body_sites_to_neo4j'),

   
    # Diseases
    
    path('diseases/', views.get_all_diseases, name='get_all_diseases'),
    path('diseases/add/', views.add_disease, name='add_disease'),
    path('diseases/<int:id>/', views.get_disease_by_id, name='get_disease_by_id'),
    path('diseases/export/', views.export_diseases_to_neo4j, name='export_diseases_to_neo4j'),

   
    # Products
    
    path('products/', views.get_all_products, name='get_all_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:id>/', views.get_product_by_id, name='get_product_by_id'),
    path('products/export/', views.export_products_to_neo4j, name='export_products_to_neo4j'),

    
    # Species Interactions
    
    path('interactions/', views.get_all_interactions, name='get_all_interactions'),
    path('interactions/add/', views.add_interaction, name='add_interaction'),
    path('interactions/<int:id>/', views.get_interaction_by_id, name='get_interaction_by_id'),
    path('interactions/export/', views.export_interactions_to_neo4j, name='export_interactions_to_neo4j'),

   
    # Migration Patterns
   
    path('migrations/', views.get_all_migrations, name='get_all_migrations'),
    path('migrations/add/', views.add_migration, name='add_migration'),
    path('migrations/<int:id>/', views.get_migration_by_id, name='get_migration_by_id'),
    path('migrations/export/', views.export_migrations_to_neo4j, name='export_migrations_to_neo4j'),

    
    # Product Events
   
    path('product-events/', views.get_all_product_events, name='get_all_product_events'),
    path('product-events/add/', views.add_product_event, name='add_product_event'),
    path('product-events/<int:id>/', views.get_product_event_by_id, name='get_product_event_by_id'),
    path('product-events/export/', views.export_product_events_to_neo4j, name='export_product_events_to_neo4j'),


    # Export All
   
    path('export-all/', views.export_all_to_neo4j, name='export_all_to_neo4j'),

    path('graph/', views.view_graph, name='view_graph'),
    path('api/get_graph_data/', views.get_graph_data, name='get_graph_data'),
    
    # Expanded Graph (D3.js)
    path('api/get_expanded_graph_data/', views.get_expanded_graph_data, name='get_expanded_graph_data'),
]
