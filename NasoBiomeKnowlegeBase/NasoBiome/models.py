from django.db import models

class BodySite(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    affected_site = models.ForeignKey(
        BodySite, on_delete=models.SET_NULL, null=True, blank=True, related_name="diseases"
    )
    mechanism_of_causation = models.TextField(
        blank=True,
        help_text="Explain how this disease develops (e.g., inflammation, immune response, toxin)."
    )

    def __str__(self):
        return self.name

class Species(models.Model):
    name = models.CharField(max_length=150, unique=True)  # e.g. "Staphylococcus aureus"
    phyla = models.CharField(max_length=100, help_text="Taxonomic phylum")
    genus = models.CharField(max_length=100, blank=True)
    family = models.CharField(max_length=100, blank=True)
    genome_reference_link = models.URLField(blank=True, null=True)
    age_range = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Age range where species is found (e.g., 0-1y, adult)"
    )
    description = models.TextField(blank=True)

    # Main site of origin (nose microbiome)
    origin_site = models.ForeignKey(
        BodySite,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nasal_microbes",
        help_text="Primary site where this species normally resides (typically the nose)."
    )

    # Sites where it can reside or migrate to
    body_sites = models.ManyToManyField(
        BodySite,
        related_name="associated_species",
        blank=True,
        help_text="All sites where this species has been detected or migrated to."
    )

    # Diseases this species can cause (directly or indirectly)
    diseases = models.ManyToManyField(
        Disease,
        related_name="associated_species",
        blank=True,
        help_text="Diseases this species is associated with (directly or through interaction)."
    )

    # Products secreted by this specie
    products = models.ManyToManyField(
        'Product',
        related_name="producing_species",
        blank=True,
        help_text="Molecular products secreted by this species."
    )

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    mechanism_of_action = models.TextField(
        blank=True,
        help_text="Describe how this product contributes to disease (e.g., toxin-mediated damage)."
    )

    def __str__(self):
        return self.name

class SpeciesInteraction(models.Model):
    INTERACTION_TYPES = [
        ("synergistic", "Synergistic (enhance each other)"),
        ("antagonistic", "Antagonistic (inhibit each other)"),
        ("neutral", "Neutral (no effect)"),
    ]

    species_1 = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="interactions_as_source")
    species_2 = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="interactions_as_target")
    site = models.ForeignKey(BodySite, on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    mechanism = models.TextField(blank=True, help_text="Mechanism (e.g., quorum sensing, metabolite competition).")
    evidence = models.TextField(blank=True)
    associated_disease = models.ForeignKey(
        Disease, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="interaction_caused_diseases"
    )

    def __str__(self):
        return f"{self.species_1.name} ↔ {self.species_2.name} ({self.interaction_type})"
#class MigrationPattern(models.Model):
    #species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="migrations")
    #from_site = models.ForeignKey(BodySite, on_delete=models.CASCADE, related_name="migration_from")
    #to_site = models.ForeignKey(BodySite, on_delete=models.CASCADE, related_name="migration_to")
    #mechanism = models.CharField(max_length=400, blank=True, help_text="Mechanism (e.g., aspiration, bloodstream).")
    #trigger_conditions = models.TextField(blank=True, help_text="Conditions enabling migration (e.g., inflammation).")
    #evidence = models.TextField(blank=True)
    #resulting_disease = models.ForeignKey(
    #    Disease, on_delete=models.SET_NULL, null=True, blank=True,
   #     related_name="migration_caused_diseases"
  #  )

 #   def __str__(self):
#        return f"{self.species.name}: {self.from_site.name} → {self.to_site.name}"
class MigrationPattern(models.Model):
    species = models.ForeignKey("Species", on_delete=models.CASCADE, related_name="migrations")
    from_site = models.ForeignKey("BodySite", on_delete=models.CASCADE, related_name="migrations_from")
    to_site = models.ForeignKey("BodySite", on_delete=models.CASCADE, related_name="migrations_to")
    
    mechanism = models.TextField(blank=True, null=True)
    trigger_conditions = models.TextField(blank=True, null=True)
    evidence = models.TextField(blank=True, null=True)

    resulting_disease = models.ForeignKey("Disease", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "Migration Pattern"
        verbose_name_plural = "Migration Patterns"

    def __str__(self):
        return f"{self.species.name} migrates from {self.from_site.name} to {self.to_site.name}"
    


class ProductEvent(models.Model):
    """
    Biological event where one or more species produce a product at a body site
    (possibly during migration or interaction), causing disease.
    """

    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="product_events")
    interacting_species = models.ForeignKey(
        Species, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="partner_product_events", help_text="Optional partner species."
    )

    site = models.ForeignKey(BodySite, on_delete=models.CASCADE, related_name="product_events")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="production_events")
    disease = models.ForeignKey(
        Disease, on_delete=models.SET_NULL, null=True, blank=True, related_name="causing_events"
    )

    migration = models.ForeignKey(
        MigrationPattern, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="product_events", help_text="Linked if produced during migration."
    )
    interaction = models.ForeignKey(
        SpeciesInteraction, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="product_events", help_text="Linked if produced due to interaction."
    )

    mechanism = models.TextField(blank=True, help_text="How the product is produced (trigger mechanism).")
    evidence = models.TextField(blank=True, help_text="Literature or experimental evidence (DOI, PubMed link).")

    def __str__(self):
        text = f"{self.species.name} → {self.product.name} @ {self.site.name}"
        if self.interacting_species:
            text += f" + {self.interacting_species.name}"
        return text
