# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .neo4j_integration import driver

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import (
    Species, BodySite, Disease, Product,
    SpeciesInteraction, MigrationPattern, ProductEvent
)
from .forms import (
    SpeciesForm, BodySiteForm, DiseaseForm,
    ProductForm, SpeciesInteractionForm, MigrationPatternForm, ProductEventForm
)
from .neo4j_integration import (
    push_all_species_to_neo4j,
    push_all_body_sites_to_neo4j,
    push_all_diseases_to_neo4j,
    push_all_products_to_neo4j,
    push_all_interactions_to_neo4j,
    push_all_migrations_to_neo4j,
    push_all_product_events_to_neo4j,
    fetch_initial_graph,
    fetch_neighbors,
    fetch_disease_pathway,
)

# Home Page
def home(request):
    kpi = {
        'species_count': Species.objects.count(),
        'body_sites_count': BodySite.objects.count(),
        'diseases_count': Disease.objects.count(),
        'products_count': Product.objects.count(),
        'interactions_count': SpeciesInteraction.objects.count(),
        'migrations_count': MigrationPattern.objects.count(),
        'product_events_count': ProductEvent.objects.count(),
        # Optional: if track total graph stats elsewhere
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
            # Add other relationship types if needed
        )
    }
    return render(request, 'home.html', {'kpi': kpi})


#Speices
def get_all_species(request):
    species = Species.objects.all()
    return render(request, "species/species_list.html", {"species": species})

def get_species_by_id(request, id):
    species = get_object_or_404(Species, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            species.delete()
            return redirect('get_all_species')
        else:
            form = SpeciesForm(request.POST, instance=species)
            if form.is_valid():
                form.save()
                return redirect('get_all_species')
    else:
        form = SpeciesForm(instance=species)
    return render(request, "species/species_detail.html", {"species": species, "form": form})

def add_species(request):
    if request.method == "POST":
        form = SpeciesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_species')
    else:
        form = SpeciesForm()
    return render(request, "species/add_species.html", {"form": form})

def export_species_to_neo4j(request):
    push_all_species_to_neo4j()
    return HttpResponse("Species exported to Neo4j!")


#Body sites
def get_all_body_sites(request):
    sites = BodySite.objects.all()
    return render(request, "bodysite/bodysite_list.html", {"sites": sites})

def get_body_site_by_id(request, id):
    site = get_object_or_404(BodySite, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            site.delete()
            return redirect('get_all_body_sites')
        else:
            form = BodySiteForm(request.POST, instance=site)
            if form.is_valid():
                form.save()
                return redirect('get_all_body_sites')
    else:
        form = BodySiteForm(instance=site)
    return render(request, "bodysite/bodysite_detail.html", {"site": site, "form": form})

def add_body_site(request):
    if request.method == "POST":
        form = BodySiteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_body_sites')
    else:
        form = BodySiteForm()
    return render(request, "bodysite/add_bodysite.html", {"form": form})

def export_body_sites_to_neo4j(request):
    push_all_body_sites_to_neo4j()
    return HttpResponse("Body sites exported to Neo4j!")



# Diseases
def get_all_diseases(request):
    diseases = Disease.objects.all()
    return render(request, "disease/disease_list.html", {"diseases": diseases})

def get_disease_by_id(request, id):
    disease = get_object_or_404(Disease, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            disease.delete()
            return redirect('get_all_diseases')
        else:
            form = DiseaseForm(request.POST, instance=disease)
            if form.is_valid():
                form.save()
                return redirect('get_all_diseases')
    else:
        form = DiseaseForm(instance=disease)
    return render(request, "disease/disease_detail.html", {"disease": disease, "form": form})

def add_disease(request):
    if request.method == "POST":
        form = DiseaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_diseases')
    else:
        form = DiseaseForm()
    return render(request, "disease/add_disease.html", {"form": form})

def export_diseases_to_neo4j(request):
    push_all_diseases_to_neo4j()
    return HttpResponse("Diseases exported to Neo4j!")


#Products
def get_all_products(request):
    products = Product.objects.all()
    return render(request, "product/product_list.html", {"products": products})

def get_product_by_id(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            product.delete()
            return redirect('get_all_products')
        else:
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                return redirect('get_all_products')
    else:
        form = ProductForm(instance=product)
    return render(request, "product/product_detail.html", {"product": product, "form": form})

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_products')
    else:
        form = ProductForm()
    return render(request, "product/add_product.html", {"form": form})

def export_products_to_neo4j(request):
    push_all_products_to_neo4j()
    return HttpResponse("✅ Products exported to Neo4j!")


#Species Interactions
def get_all_interactions(request):
    interactions = SpeciesInteraction.objects.all()
    return render(request, "interaction/interaction_list.html", {"interactions": interactions})

def get_interaction_by_id(request, id):
    interaction = get_object_or_404(SpeciesInteraction, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            interaction.delete()
            return redirect('get_all_interactions')
        else:
            form = SpeciesInteractionForm(request.POST, instance=interaction)
            if form.is_valid():
                form.save()
                return redirect('get_all_interactions')
    else:
        form = SpeciesInteractionForm(instance=interaction)
    return render(request, "interaction/interaction_detail.html", {"interaction": interaction, "form": form})

def add_interaction(request):
    if request.method == "POST":
        form = SpeciesInteractionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_interactions')
    else:
        form = SpeciesInteractionForm()
    return render(request, "interaction/add_interaction.html", {"form": form})

def export_interactions_to_neo4j(request):
    push_all_interactions_to_neo4j()
    return HttpResponse("Interactions exported to Neo4j!")


# Migration Patterns

def get_all_migrations(request):
    migrations = MigrationPattern.objects.all()
    return render(request, "migration/migration_list.html", {"migrations": migrations})

def get_migration_by_id(request, id):
    migration = get_object_or_404(MigrationPattern, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            migration.delete()
            return redirect('get_all_migrations')
        else:
            form = MigrationPatternForm(request.POST, instance=migration)
            if form.is_valid():
                form.save()
                return redirect('get_all_migrations')
    else:
        form = MigrationPatternForm(instance=migration)
    return render(request, "migration/migration_detail.html", {"migration": migration, "form": form})

def add_migration(request):
    if request.method == "POST":
        form = MigrationPatternForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_migrations')
    else:
        form = MigrationPatternForm()
    return render(request, "migration/add_migration.html", {"form": form})

def export_migrations_to_neo4j(request):
    push_all_migrations_to_neo4j()
    return HttpResponse("Migration patterns exported to Neo4j!")


# Product events
def get_all_product_events(request):
    events = ProductEvent.objects.all()
    return render(request, "product_event/product_event_list.html", {"events": events})

def get_product_event_by_id(request, id):
    event = get_object_or_404(ProductEvent, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            event.delete()
            return redirect('get_all_product_events')
        else:
            form = ProductEventForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                return redirect('get_all_product_events')
    else:
        form = ProductEventForm(instance=event)
    return render(request, "product_event/product_event_detail.html", {"event": event, "form": form})

def add_product_event(request):
    if request.method == "POST":
        form = ProductEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_product_events')
    else:
        form = ProductEventForm()
    return render(request, "product_event/add_product_event.html", {"form": form})

def export_product_events_to_neo4j(request):
    push_all_product_events_to_neo4j()
    return HttpResponse("Product events exported to Neo4j!")


# Optional: export everything at once
def export_all_to_neo4j(request):
    push_all_species_to_neo4j()
    push_all_body_sites_to_neo4j()
    push_all_diseases_to_neo4j()
    push_all_products_to_neo4j()
    push_all_interactions_to_neo4j()
    push_all_migrations_to_neo4j()
    push_all_product_events_to_neo4j()
    return HttpResponse(" All models exported to Neo4j successfully!")


# Neo4j graph JSON endpoint


import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .neo4j_integration import driver


# Graph visualization page

def view_graph(request):
    """
    Render the page containing the Neo4j graph visualization.
    """
    return render(request, "graph/graph.html")



# Graph data endpoint

@csrf_exempt
def get_graph_data(request):
    """
    Returns nodes and relationships from Neo4j as JSON
    for frontend visualization with vis.js / Neovis.js.
    """
    try:
        cypher = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 1000"
        nodes, edges = {}, []

        with driver.session() as session:
            result = session.run(cypher)
            for record in result:
                # nodes
                for node_key in ["n", "m"]:
                    n_obj = record.get(node_key)
                    if not n_obj:
                        continue
                    if n_obj.id not in nodes:
                        nodes[n_obj.id] = {
                            "id": n_obj.id,
                            "label": n_obj.get("name") or str(n_obj.id),
                            "group": list(n_obj.labels)[0] if n_obj.labels else "Unknown",
                            "title": n_obj.get("description") or n_obj.get("mechanism_of_causation") or ""
                        }

                # edges
                r_obj = record.get("r")
                if r_obj and hasattr(r_obj.start_node, "id") and hasattr(r_obj.end_node, "id"):
                    edges.append({
                        "from": r_obj.start_node.id,
                        "to": r_obj.end_node.id,
                        "label": getattr(r_obj, "type", ""),
                        "arrows": "to"
                    })

        return JsonResponse({"nodes": list(nodes.values()), "edges": edges})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)





# Expanded Graph data endpoint

@csrf_exempt
def get_expanded_graph_data(request):
    """
    Returns nodes and relationships from Neo4j as JSON.
    Supports initial load and expanding neighbors.
    """
    try:
        node_id = request.GET.get('node_id')
        mode = request.GET.get('mode')
        
        if node_id:
            if mode == 'pathway':
                # Traceback mode for diseases
                nodes, links = fetch_disease_pathway(node_id)
            else:
                # Standard expansion for other nodes
                nodes, links = fetch_neighbors(node_id)
            
            return JsonResponse({"nodes": nodes, "links": links})
        else:
            # Fetch initial graph (just nodes)
            nodes = fetch_initial_graph(limit=15)
            return JsonResponse({"nodes": nodes, "links": []})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

