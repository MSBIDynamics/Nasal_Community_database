from neo4j import GraphDatabase
from .models import Species, BodySite, Disease, Product, SpeciesInteraction, MigrationPattern, ProductEvent


# Neo4j connection

NEO4J_URI = "bolt://neo4j:7687"  # Update if using a different host
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jpassword"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# UTILITY FUNCTION TO RUN CYPHER

def run_cypher(query, parameters=None):
    with driver.session() as session:
        session.run(query, parameters or {})



# BODY SITES

def push_all_body_sites_to_neo4j():
    for site in BodySite.objects.all():
        run_cypher("""
            MERGE (b:BodySite {id: $id})
            SET b.name = $name, b.description = $description
        """, {"id": site.id, "name": site.name, "description": site.description or ""})


# DISEASES

def push_all_diseases_to_neo4j():
    for disease in Disease.objects.all():
        run_cypher("""
            MERGE (d:Disease {id: $id})
            SET d.name = $name, d.description = $description, d.mechanism_of_causation = $mechanism
        """, {
            "id": disease.id,
            "name": disease.name,
            "description": disease.description or "",
            "mechanism": disease.mechanism_of_causation or ""
        })

        # Relationship to affected body site
        if disease.affected_site:
            run_cypher("""
                MATCH (d:Disease {id: $disease_id}), (b:BodySite {id: $bodysite_id})
                MERGE (d)-[:AFFECTS]->(b)
            """, {"disease_id": disease.id, "bodysite_id": disease.affected_site.id})


# PRODUCTS

def push_all_products_to_neo4j():
    for product in Product.objects.all():
        run_cypher("""
            MERGE (p:Product {id: $id})
            SET p.name = $name, p.description = $description, p.mechanism_of_action = $mechanism
        """, {
            "id": product.id,
            "name": product.name,
            "description": product.description or "",
            "mechanism": product.mechanism_of_action or ""
        })



# SPECIES

def push_all_species_to_neo4j():
    for species in Species.objects.all():
        run_cypher("""
            MERGE (s:Species {id: $id})
            SET s.name = $name, s.phyla = $phyla, s.genus = $genus,
                s.family = $family, s.genome_reference_link = $link,
                s.age_range = $age, s.description = $desc
        """, {
            "id": species.id,
            "name": species.name,
            "phyla": species.phyla,
            "genus": species.genus or "",
            "family": species.family or "",
            "link": species.genome_reference_link or "",
            "age": species.age_range or "",
            "desc": species.description or ""
        })

        # Origin site (RESIDES_IN)
        if species.origin_site:
            run_cypher("""
                MATCH (s:Species {id: $species_id}), (b:BodySite {id: $bodysite_id})
                MERGE (s)-[:RESIDES_IN]->(b)
            """, {"species_id": species.id, "bodysite_id": species.origin_site.id})

        # Body sites (PRESENT_IN)
        for site in species.body_sites.all():
            run_cypher("""
                MATCH (s:Species {id: $species_id}), (b:BodySite {id: $bodysite_id})
                MERGE (s)-[:PRESENT_IN]->(b)
            """, {"species_id": species.id, "bodysite_id": site.id})

        # Diseases (ASSOCIATED_WITH)
        for disease in species.diseases.all():
            run_cypher("""
                MATCH (s:Species {id: $species_id}), (d:Disease {id: $disease_id})
                MERGE (s)-[:ASSOCIATED_WITH]->(d)
            """, {"species_id": species.id, "disease_id": disease.id})

        # Products (PRODUCES)
        for product in species.products.all():
            run_cypher("""
                MATCH (s:Species {id: $species_id}), (p:Product {id: $product_id})
                MERGE (s)-[:PRODUCES]->(p)
            """, {"species_id": species.id, "product_id": product.id})



# SPECIES INTERACTIONS

def push_all_interactions_to_neo4j():
    for interaction in SpeciesInteraction.objects.all():
        run_cypher("""
            MERGE (i:Interaction {id: $id})
            SET i.type = $type, i.mechanism = $mechanism, i.evidence = $evidence
        """, {
            "id": interaction.id,
            "type": interaction.interaction_type,
            "mechanism": interaction.mechanism or "",
            "evidence": interaction.evidence or ""
        })

        # Species involved
        run_cypher("""
            MATCH (i:Interaction {id: $id}),
                  (s1:Species {id: $s1_id}),
                  (s2:Species {id: $s2_id})
            MERGE (s1)-[:INTERACTS_WITH {interaction_id: $id}]->(s2)
            MERGE (i)-[:INVOLVES]->(s1)
            MERGE (i)-[:INVOLVES]->(s2)
        """, {"id": interaction.id, "s1_id": interaction.species_1.id, "s2_id": interaction.species_2.id})

        # Body site
        run_cypher("""
            MATCH (i:Interaction {id: $id}), (b:BodySite {id: $body_id})
            MERGE (i)-[:OCCURS_AT]->(b)
        """, {"id": interaction.id, "body_id": interaction.site.id})

        # Associated disease
        if interaction.associated_disease:
            run_cypher("""
                MATCH (i:Interaction {id: $id}), (d:Disease {id: $disease_id})
                MERGE (i)-[:CAUSES]->(d)
            """, {"id": interaction.id, "disease_id": interaction.associated_disease.id})


# MIGRATION PATTERNS

def push_all_migrations_to_neo4j():
    for migration in MigrationPattern.objects.all():
        run_cypher("""
            MERGE (m:Migration {id: $id})
            SET m.mechanism = $mechanism, 
                m.trigger_conditions = $trigger,
                m.evidence = $evidence
        """, {
            "id": migration.id,
            "mechanism": migration.mechanism or "",
            "trigger": migration.trigger_conditions or "",
            "evidence": migration.evidence or ""
        })

        # Link Species
        run_cypher("""
            MATCH (m:Migration {id: $id}), (s:Species {id: $species_id})
            MERGE (m)-[:INVOLVES_SPECIES]->(s)
        """, {"id": migration.id, "species_id": migration.species.id})

        # Link FROM Site
        run_cypher("""
            MATCH (m:Migration {id: $id}), (from:BodySite {id: $from_id})
            MERGE (m)-[:STARTS_FROM]->(from)
        """, {"id": migration.id, "from_id": migration.from_site.id})

        # Link TO Site
        run_cypher("""
            MATCH (m:Migration {id: $id}), (to:BodySite {id: $to_id})
            MERGE (m)-[:MIGRATES_TO]->(to)
        """, {"id": migration.id, "to_id": migration.to_site.id})

        # Optional: Link resulting disease (if exists)
        if migration.resulting_disease:
            run_cypher("""
                MATCH (m:Migration {id: $id}), (d:Disease {id: $disease_id})
                MERGE (m)-[:CAUSES]->(d)
            """, {
                "id": migration.id,
                "disease_id": migration.resulting_disease.id
            })


# PRODUCT EVENTS

def push_all_product_events_to_neo4j():
    for event in ProductEvent.objects.all():
        run_cypher("""
            MERGE (e:ProductEvent {id: $id})
            SET e.mechanism = $mechanism, e.evidence = $evidence
        """, {
            "id": event.id,
            "mechanism": event.mechanism or "",
            "evidence": event.evidence or ""
        })

        # Species
        run_cypher("""
            MATCH (e:ProductEvent {id: $id}), (s:Species {id: $species_id})
            MERGE (s)-[:PRODUCES_EVENT]->(e)
        """, {"id": event.id, "species_id": event.species.id})

        # Optional interacting species
        if event.interacting_species:
            run_cypher("""
                MATCH (e:ProductEvent {id: $id}), (s:Species {id: $partner_id})
                MERGE (s)-[:PARTICIPATES_IN]->(e)
            """, {"id": event.id, "partner_id": event.interacting_species.id})

        # Body site
        run_cypher("""
            MATCH (e:ProductEvent {id: $id}), (b:BodySite {id: $site_id})
            MERGE (e)-[:AT_SITE]->(b)
        """, {"id": event.id, "site_id": event.site.id})

        # Product
        run_cypher("""
            MATCH (e:ProductEvent {id: $id}), (p:Product {id: $product_id})
            MERGE (e)-[:PRODUCT]->(p)
        """, {"id": event.id, "product_id": event.product.id})

        # Disease
        if event.disease:
            run_cypher("""
                MATCH (e:ProductEvent {id: $id}), (d:Disease {id: $disease_id})
                MERGE (e)-[:CAUSES]->(d)
            """, {"id": event.id, "disease_id": event.disease.id})

        # Migration
        if event.migration:
            run_cypher("""
                MATCH (e:ProductEvent {id: $id}), (m:Migration {id: $migration_id})
                MERGE (e)-[:DURING_MIGRATION]->(m)
            """, {"id": event.id, "migration_id": event.migration.id})

        # Interaction
        if event.interaction:
            run_cypher("""
                MATCH (e:ProductEvent {id: $id}), (i:Interaction {id: $interaction_id})
                MERGE (e)-[:DURING_INTERACTION]->(i)
            """, {"id": event.id, "interaction_id": event.interaction.id})


# EXPORT EVERYTHING

def export_all_to_neo4j():
    push_all_body_sites_to_neo4j()
    push_all_diseases_to_neo4j()
    push_all_products_to_neo4j()
    push_all_species_to_neo4j()
    push_all_interactions_to_neo4j()
    push_all_migrations_to_neo4j()
    push_all_product_events_to_neo4j()


# GRAPH FETCHING

def _serialize_neo4j_value(value):
    """Helper to serialize Neo4j values"""
    if hasattr(value, 'iso_format'):
        return value.iso_format()
    return value

def fetch_initial_graph(limit: int = 15) -> list:
    """Fetch initial graph data - random nodes of any type"""
    try:
        with driver.session() as session:
            # Modified query to fetch ANY node, properly returning label and group
            query = """
                MATCH (n)
                WHERE n:Disease OR n:Species OR n:BodySite
                RETURN collect({
                        id: elementId(n),
                        label: n.name,
                        group: CASE 
                            WHEN n:Disease THEN 'Disease'
                            WHEN n:Species THEN 'Species'
                            WHEN n:BodySite THEN 'BodySite'
                            ELSE 'Other'
                        END,
                        properties: properties(n)
                    }) AS nodes
            """
            record = session.run(query, limit=limit).single()
            nodes = record["nodes"] if record else []
            
            # Serialize properties
            for node in nodes:
                serialized_props = {}
                for k, v in node.get('properties', {}).items():
                    try:
                        serialized_props[k] = _serialize_neo4j_value(v)
                    except:
                        serialized_props[k] = str(v)
                node['properties'] = serialized_props
            return nodes
    except Exception as e:
        print(f"Error fetching initial graph data: {str(e)}")
        raise

def fetch_neighbors(node_id: str) -> tuple[list, list]:
    """Fetch direct neighbors (1 hop) of a node"""
    try:
        with driver.session() as session:
            try:
                node_id_val = int(node_id)
            except ValueError:
                node_id_val = node_id

            # Updated query to return consistent structure (label, group)
            query = """
            MATCH (n)
            WHERE elementId(n) = $node_id
            MATCH (n)-[r]-(m)
            WITH collect(DISTINCT n) + collect(DISTINCT m) AS allNodes, collect(r) AS rels
            UNWIND allNodes AS node
            WITH DISTINCT node, rels
            RETURN collect({
                id: elementId(node),
                label: COALESCE(node.name, node.type, head(labels(node))),
                group: head(labels(node)),
                properties: properties(node)
            }) AS nodes,
            collect([
                rel IN rels | {
                    from: elementId(startNode(rel)),
                    to: elementId(endNode(rel)),
                    label: type(rel)
                }
            ]) AS links
            """
            
            record = session.run(query, node_id=node_id).single()
            if not record:
                return [], []

            nodes = record["nodes"]
            for node in nodes:
                serialized_props = {}
                for k, v in node.get('properties', {}).items():
                    try:
                        serialized_props[k] = _serialize_neo4j_value(v)
                    except:
                        serialized_props[k] = str(v)
                node['properties'] = serialized_props

            links = [link for sublist in record["links"] for link in sublist]
            return nodes, links
    except Exception as e:
        print(f"Error fetching neighbors: {str(e)}")
        raise

def fetch_disease_pathway(disease_id: str) -> tuple[list, list]:
    """
    Fetch complete pathway for a disease including:
    - Species that contribute to the disease
    - Interactions between species
    - ProductEvents
    - Products produced
    - Body sites involved
    - Migration patterns
    """
    try:
        with driver.session() as session:
            query = """
            // Start with the disease
            MATCH (d:Disease)
            WHERE elementId(d) = $disease_id
            
            // --- Existing disease pathway components ---
            OPTIONAL MATCH (s_direct:Species)-[:ASSOCIATED_WITH]->(d)

            // Interaction + Location
            OPTIONAL MATCH (i:Interaction)-[:CAUSES]->(d)
            OPTIONAL MATCH (i)-[:INVOLVES]->(s_interact:Species)
            OPTIONAL MATCH (i)-[:OCCURS_AT]->(site_interact:BodySite)

            // Product Event + Context
            OPTIONAL MATCH (pe:ProductEvent)-[:CAUSES]->(d)
            OPTIONAL MATCH (pe)-[:PRODUCT]->(prod:Product)
            OPTIONAL MATCH (pe)<-[:PRODUCES_EVENT]-(s_produce:Species)
            OPTIONAL MATCH (pe)-[:AT_SITE]->(site_event:BodySite)
            OPTIONAL MATCH (pe)-[:DURING_MIGRATION]->(context_mig:Migration)
            OPTIONAL MATCH (pe)-[:DURING_INTERACTION]->(context_int:Interaction)

            OPTIONAL MATCH (d)-[:AFFECTS]->(site_affected:BodySite)

            // --- Migration-related components ---
            // Find Migration nodes that cause this disease
            OPTIONAL MATCH (mig:Migration)-[:CAUSES]->(d)
            
            // Find connected entities to the migration
            OPTIONAL MATCH (mig)-[:INVOLVES_SPECIES]->(s_mig:Species)
            OPTIONAL MATCH (mig)-[:STARTS_FROM]->(from_site_mig:BodySite)
            OPTIONAL MATCH (mig)-[:MIGRATES_TO]->(to_site_mig:BodySite)

            // Collect everything
            WITH d,
                collect(DISTINCT s_direct) AS direct_species,
                collect(DISTINCT i) AS interactions,
                collect(DISTINCT s_interact) AS interaction_species,
                collect(DISTINCT site_interact) AS interaction_sites,
                collect(DISTINCT pe) AS product_events,
                collect(DISTINCT prod) AS products,
                collect(DISTINCT s_produce) AS producing_species,
                collect(DISTINCT site_event) AS event_sites,
                collect(DISTINCT context_mig) AS pe_context_migs,
                collect(DISTINCT context_int) AS pe_context_ints,
                collect(DISTINCT site_affected) AS affected_sites,
                collect(DISTINCT mig) AS migration_events,
                collect(DISTINCT s_mig) AS migration_species,
                collect(DISTINCT to_site_mig) AS migration_to_sites,
                collect(DISTINCT from_site_mig) AS migration_from_sites

            // Flatten all nodes
            WITH [n IN 
                [d] +
                direct_species + 
                interactions + 
                interaction_species +
                interaction_sites +
                product_events + 
                products + 
                producing_species +
                event_sites + 
                pe_context_migs +
                pe_context_ints +
                affected_sites +
                migration_events +
                migration_species + 
                migration_to_sites + 
                migration_from_sites 
                WHERE n IS NOT NULL
            ] AS allNodesList

            // Get unique nodes
            UNWIND allNodesList AS node
            WITH collect(DISTINCT node) AS allNodes
            WHERE size(allNodes) > 0

            // Get all relationships between these nodes
            UNWIND allNodes AS n1
            UNWIND allNodes AS n2
            WITH allNodes, n1, n2
            WHERE n1 <> n2
            
            OPTIONAL MATCH (n1)-[r]->(n2)
            
            WITH allNodes,
                 collect(DISTINCT r) AS baseRels
            
            // Combine relationships (filter nulls)
            WITH allNodes, 
                 [rel IN baseRels WHERE rel IS NOT NULL] AS allRelsList
            
            // Deduplicate relationships
            UNWIND allRelsList AS rel
            WITH allNodes, 
                 collect(DISTINCT rel) AS relationships

            // Serialize nodes
            UNWIND allNodes AS n
            WITH collect({
                id: elementId(n),
                label: COALESCE(n.name, n.type, head(labels(n))),
                group: head(labels(n)),
                properties: properties(n)
            }) AS nodes, relationships

            // Serialize relationships
            UNWIND relationships AS rel
            WITH nodes,
                 collect({
                    from: elementId(startNode(rel)),
                    to: elementId(endNode(rel)),
                    label: type(rel),
                    properties: properties(rel)
                }) AS links

            RETURN nodes, links
            """
            
            record = session.run(query, disease_id=str(disease_id)).single()
            
            if not record:
                return [], []
            
            nodes = record["nodes"] or []
            links = record["links"] or []
            
            # Remove nulls
            nodes = [n for n in nodes if n is not None]
            links = [l for l in links if l is not None]
            
            # Serialize properties
            for node in nodes:
                serialized_props = {}
                for k, v in node.get('properties', {}).items():
                    try:
                        serialized_props[k] = _serialize_neo4j_value(v)
                    except:
                        serialized_props[k] = str(v)
                node['properties'] = serialized_props
            
            # Serialize link properties
            for link in links:
                if 'properties' in link:
                    serialized_props = {}
                    for k, v in link.get('properties', {}).items():
                        try:
                            serialized_props[k] = _serialize_neo4j_value(v)
                        except:
                            serialized_props[k] = str(v)
                    link['properties'] = serialized_props
            
            print(f"Found {len(nodes)} nodes and {len(links)} links for disease {disease_id}")
            
            return nodes, links
            
    except Exception as e:
        print(f"Error fetching disease pathway: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
