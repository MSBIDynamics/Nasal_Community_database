from decimal import DecimalException
import os
import re
from urllib.parse import urlparse
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from NasoBiome.models import BodySite, Disease, Species, Product, MigrationPattern, SpeciesInteraction, ProductEvent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Command(BaseCommand):
    help = "Import nasal microbiome data from Nasal20Microbiomes.xlsx into Django models"

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help="Path to the Excel file", default="../data/Nasal20Microbiomes.xlsx")

    def handle(self, *args, **options):
        file_path = os.path.join(BASE_DIR, options['file'])
        self.stdout.write(f"Loading data from {file_path}...")

        # Load all relevant sheets
        try:
            sheet1 = pd.read_excel(file_path, sheet_name="Sheet1", header=0)
        except Exception as e:
            self.stderr.write(f"Error reading Sheet1: {e}")
            return

        with transaction.atomic():
            self.import_sheet1(sheet1)

        self.stdout.write(self.style.SUCCESS("✅ Successfully imported all data!"))

    def normalize(self, val):
        if pd.isna(val) or val == "":
            return ""
        return str(val).strip()

    def normalize_url(self, text):
        if not text:
            return None
        urls = re.findall(r'https?://[^\s\)]+', str(text))
        return urls[0] if urls else None

    def normalize_name(self, name):
        return str(name).strip() if pd.notna(name) else ""

    def get_or_create_body_site(self, name):
        if not name:
            return None
        
        full_name = self.normalize_name(name)
        if not full_name:
            return None
            
        # Truncate name if too long (max 100 chars)
        short_name = full_name[:100]
        
        obj, created = BodySite.objects.get_or_create(name=short_name)
        
        # If created or description is empty, update description with full name if different
        if (created or not obj.description) and len(full_name) > 100:
            obj.description = full_name
            obj.save()
            
        return obj

    def get_or_create_disease(self, name, mechanism="", site_name=None, description=""):
        if not name:
            return None
        name = self.normalize_name(name)
        if not name:
            return None

        site = self.get_or_create_body_site(site_name) if site_name else None
        
        # Try to get existing disease
        try:
            obj = Disease.objects.get(name=name)
            # Update description if provided and existing is empty
            if description and not obj.description:
                obj.description = description
                obj.save()
        except Disease.DoesNotExist:
            obj = Disease.objects.create(
                name=name,
                mechanism_of_causation=self.normalize_name(mechanism),
                affected_site=site,
                description=description
            )
            
        return obj

    def get_or_create_product(self, name, mechanism=""):
        if not name:
            return None
        name = self.normalize_name(name)
        if not name:
            return None
        obj, _ = Product.objects.get_or_create(
            name=name,
            defaults={"mechanism_of_action": self.normalize_name(mechanism)}
        )
        return obj

    def extract_list_from_text(self, text, sep=","):
        if pd.isna(text) or not text:
            return []
        items = [x.strip() for x in str(text).split(sep) if x.strip()]
        return items
    def is_phylum_row(self, row):
        species = self.normalize(row["Species"])
        if not species:
            return False
        other_columns = [col for col in row.index if col != "Species"]

        # Check that every other column is empty/NaN after normalization
        return all(self.normalize(row[col]) == "" for col in other_columns)
    def parse_body_site_interactions(self, interaction_str):
        if not interaction_str:
            return [], ""
        [body_sites, description] = interaction_str.split("\n")
        pairs = []
        for part in str(body_sites).split(","):
            sites = [s.strip() for s in part.split("–") if s.strip()]
            if len(sites) == 2:
                pairs.append((sites[0], sites[1]))
        return pairs, description
    def extract_products_from_text(self, text):
        """Extract known products like 'lugdunin', 'pneumolysin', etc."""
        if not text:
            return []
        product_names = []
        # Add more as needed
        known_products = [
            "lugdunin", "pneumolysin", "salivaricin", "phenol-soluble modulins",
            "hemolysins", "proteases", "lipases", "biofilm", "siderophore",
            "bacteriocin", "toxic shock syndrome toxin", "enterotoxins", "exfoliatin",
            "collagenase", "hyaluronidase", "autolysin", "neuraminidase",
            "staphyloxanthin", "catalase", "delta-toxin", "sarcinaxanthin"
        ]
        text_lower = text.lower()
        for prod in known_products:
            if prod in text_lower:
                product_names.append(prod.title().replace(" ", "-"))
        return product_names

    def extract_interactions_from_text(self, text, current_species_name):
        """
        Parse sentences like:
        - 'Inhibits S. aureus'
        - 'Coexists with C. accolens'
        - 'Competes with Haemophilus influenzae'
        Returns list of (target_species_name, interaction_type, mechanism_snippet)
        """
        if not text:
            return []
        interactions = []
        text = str(text)
        sentences = re.split(r'[.\n!;]+', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            sent_lower = sent.lower()

            # Antagonistic patterns
            if any(word in sent_lower for word in ["inhibit", "suppress", "kill", "block", "antagonistic", "reduce growth"]):
                targets = self.extract_species_names_from_text(sent, exclude=[current_species_name])
                for target in targets:
                    interactions.append((target, "antagonistic", sent))

            # Synergistic patterns
            elif any(word in sent_lower for word in ["synergistic", "coexist", "co-aggregate", "enhance", "promote", "support", "cooperate"]):
                targets = self.extract_species_names_from_text(sent, exclude=[current_species_name])
                for target in targets:
                    interactions.append((target, "synergistic", sent))

            # Neutral or unclear → skip or mark neutral if needed
        return interactions

    def extract_species_names_from_text(self, text, exclude=None):
        """Extract likely species names like 'S. aureus', 'Corynebacterium accolens'."""
        exclude = exclude or []
        candidates = set()
        # Pattern: Capital letter + . + space + lowercase word (e.g., S. aureus)
        abbrev_pattern = re.compile(r'\b([A-Z]\.\s+[a-z]\w+)')
        full_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)')

        for match in abbrev_pattern.findall(text):
            name = match.replace(". ", ".")
            if name not in exclude:
                candidates.add(name)

        for match in full_pattern.findall(text):
            if len(match.split()) == 2 and match not in exclude:
                candidates.add(match)

        # Map common abbreviations
        abbrev_map = {
            "S. aureus": "Staphylococcus aureus",
            "S. epidermidis": "Staphylococcus epidermidis",
            "C. accolens": "Corynebacterium accolens",
            "S. pneumoniae": "Streptococcus pneumoniae",
            "H. influenzae": "Haemophilus influenzae",
            "M. catarrhalis": "Moraxella catarrhalis",
            "P. aeruginosa": "Pseudomonas aeruginosa",
            "F. nucleatum": "Fusobacterium nucleatum",
        }
        resolved = set()
        for name in candidates:
            resolved.add(abbrev_map.get(name, name))
        return list(resolved)
    def agg_non_empty(self, series):
        return "\n".join([
            str(x).strip() for x in series
            if pd.notna(x) and str(x).strip() != ""
        ])

    def extract_urls_and_diseases(self, text):
        """
        Extract disease names from text and return (disease_name, description) pairs.
        Intelligently extracts disease keywords from descriptive text.
        """
        if not text:
            return [], ""
        
        # Common disease name patterns and keywords
        disease_keywords = [
            'sepsis', 'pneumonia', 'meningitis', 'endocarditis', 'bacteremia',
            'sinusitis', 'otitis', 'osteomyelitis', 'abscess', 'cellulitis',
            'peritonitis', 'empyema', 'arthritis', 'pyelonephritis',
            'pharyngitis', 'tonsillitis', 'bronchitis', 'gastroenteritis',
            'conjunctivitis', 'mastoiditis', 'pericarditis', 'myocarditis',
            'encephalitis', 'nephritis', 'hepatitis', 'colitis',
            'enteritis', 'urethritis', 'vaginitis', 'folliculitis',
            'impetigo', 'erysipelas', 'necrotizing fasciitis',
            'toxic shock syndrome', 'scarlet fever', 'rheumatic fever',
        ]
        
        lines = [line.strip() for line in str(text).split("\n") if line.strip()]
        urls = []
        disease_results = []  # List of (disease_name, description) tuples
        seen_diseases = set()  # Track to avoid duplicates
        
        for line in lines:
            # Extract URLs
            if line.startswith(("http://", "https://")):
                urls.append(line)
                continue
            elif re.match(r'^\s*www\.', line):
                urls.append("https://" + line)
                continue
            
            # Skip very long descriptive sentences
            if len(line) > 150:
                continue
            
            # Skip obvious non-disease headers/labels
            if re.match(r'^(Virulence|Antibiotic|Important|Usually|Often|Chronic|Migrates|Direct|Hematogenous):',
                       line, re.IGNORECASE):
                continue
            
            # Skip sentences with descriptive verbs
            if re.search(r'\b(causes disease|known for|may allow|can lead|can enter|can cause|producing toxins|inducing|occur in|often occur|resemble)\b',
                        line, re.IGNORECASE):
                continue
            
            line_lower = line.lower()
            
            # Check if line contains disease keywords
            found_in_line = False
            for keyword in disease_keywords:
                if keyword in line_lower:
                    # Try to extract a clean disease name around the keyword
                    # Pattern: up to 5 words before keyword + keyword + up to 3 words after
                    pattern = r'\b(?:[\w-]+\s+){0,5}' + re.escape(keyword) + r'(?:\s+[\w-]+){0,3}\b'
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    
                    for match in matches:
                        disease_name = match.strip()
                        # Clean up
                        disease_name = re.sub(r'\s+', ' ', disease_name)
                        disease_name = re.sub(r'^[^\w\(]+|[^\w\)]+$', '', disease_name)
                        
                        # Additional filtering
                        if (disease_name and 
                            len(disease_name) <= 100 and
                            disease_name.lower() not in ['infections', 'infection', 'common syndromes include'] and
                            not disease_name.lower().startswith(('the ', 'this ', 'these ', 'it ', 'they ')) and
                            disease_name.lower() not in seen_diseases):
                            
                            disease_results.append((disease_name, line))
                            seen_diseases.add(disease_name.lower())
                            found_in_line = True
                            break  # Only take first disease from each line
            
            # If no keyword match, check if line itself looks like a disease name
            if not found_in_line and len(line) <= 100:
                # Check for medical suffixes or disease-related terms
                if (re.search(r'(itis|emia|osis|pathy|oma|syndrome|disease|disorder|infection)(\s|$|\()', line_lower) and
                    line.lower() not in seen_diseases and
                    not re.search(r'\b(include|such as|like|example|note|see|refer)\b', line_lower)):
                    
                    disease_results.append((line, line))
                    seen_diseases.add(line.lower())
        
        return disease_results, "\n".join(urls)


    def normalize_url(self, text):
        if not text:
            return None
        urls = re.findall(r'https?://[^\s\)]+', str(text))
        return urls[0] if urls else None
    
    def import_sheet1(self, df):
        self.stdout.write("Importing Sheet1 with full field parsing...")

        # --- Step 1: Identify phylum rows BEFORE any ffill ---
        phylum_rows = set()
        for idx, row in df.iterrows():
            species_val = row["Species"]
            if pd.notna(species_val):
                # Check if ALL other columns are empty
                other_cols = [col for col in df.columns if col != "Species"]
                if all(pd.isna(row[col]) or (isinstance(row[col], str) and row[col].strip() == "") for col in other_cols):
                    phylum_rows.add(idx)

        # --- Step 2: Forward-fill species column ---
        df = df.copy()
        df["Species"] = df["Species"].ffill()

        # --- Step 3: Build phylum map ---
        current_phylum = "Unknown"
        phylum_map = {}
        for idx, row in df.iterrows():
            if idx in phylum_rows:
                current_phylum = str(row["Species"]).strip()
            else:
                species_name = self.normalize(row["Species"])
                if species_name:
                    phylum_map[species_name] = current_phylum

        # --- Step 4: Remove phylum rows ---
        data_rows = df[~df.index.isin(phylum_rows)].copy()
        data_rows = data_rows.dropna(subset=["Species"], how="all")

        # --- Step 5: Safely extract columns by position ---
        cols = df.columns.tolist()
        col_map = {
            "species": cols[0] if len(cols) > 0 else "Species",
            "functions": cols[1] if len(cols) > 1 else "Functions",
            "body_interaction": cols[2] if len(cols) > 2 else "Body site interaction",
            "migration_mech": cols[3] if len(cols) > 3 else "Migration Mechanism",
            "extra_notes": cols[4] if len(cols) > 4 else "Unnamed: 4",      # may be empty
            "infections": cols[5] if len(cols) > 5 else "infections caused",
            "urls": cols[6] if len(cols) > 6 else "Unnamed: 6",              # may be empty
        }

        # --- Step 6: Group by species with all real columns ---
        agg_fields = {}
        for key, col in col_map.items():
            if key in ["species"]:
                continue
            if col in data_rows.columns:
                agg_fields[col] = self.agg_non_empty

        grouped = data_rows.groupby(col_map["species"], sort=False).agg(agg_fields).reset_index()

        # --- Step 7: Process each species entry ---
        for _, group in grouped.iterrows():
            species_name = self.normalize(group[col_map["species"]])
            if not species_name:
                continue

            functions = self.normalize(group.get(col_map["functions"], ""))
            body_interaction = self.normalize(group.get(col_map["body_interaction"], ""))
            mig_mech = self.normalize(group.get(col_map["migration_mech"], ""))
            extra_notes = self.normalize(group.get(col_map["extra_notes"], ""))
            infections_raw = self.normalize(group.get(col_map["infections"], ""))
            urls_raw = self.normalize(group.get(col_map["urls"], ""))

            full_functions = "\n".join([x for x in [functions, extra_notes] if x]).strip()

            disease_lines, _ = self.extract_urls_and_diseases(infections_raw)
            all_urls = "\n".join([
                urls_raw,
                _
            ]).strip()
            genome_url = self.normalize_url(all_urls)

            phylum = phylum_map.get(species_name, "Unknown")

            # Create Species
            species, created = Species.objects.get_or_create(
                name=species_name,
                defaults={
                    "phyla": phylum,
                    "description": full_functions,
                    "genome_reference_link": genome_url,
                    "origin_site": self.get_or_create_body_site("Nose"),
                }
            )
            if not created:
                if not species.description and full_functions:
                    species.description = full_functions
                if not species.genome_reference_link and genome_url:
                    species.genome_reference_link = genome_url
                species.phyla = phylum
                species.save()

            # Ensure Nose as origin and body site
            nose = self.get_or_create_body_site("Nose")
            if nose:
                species.origin_site = nose
                species.body_sites.add(nose)

            # Parse MigrationPatterns from "Body site interaction"
            if body_interaction:
                for line in body_interaction.split("\n"):
                    line = line.strip()
                    if "–" in line and not any(skip in line for skip in ["detected", "presence", "found"]):
                        sites = [s.strip() for s in line.split("–") if s.strip()]
                        if len(sites) == 2:
                            from_site = self.get_or_create_body_site(sites[0])
                            to_site = self.get_or_create_body_site(sites[1])
                            if from_site and to_site:
                                mp, _ = MigrationPattern.objects.get_or_create(
                                    species=species,
                                    from_site=from_site,
                                    to_site=to_site,
                                    defaults={"mechanism": mig_mech}
                                )
                                species.body_sites.add(from_site, to_site)

            # Parse diseases
            # Parse diseases
            for disease_name, description in disease_lines:
                disease_name = self.normalize(disease_name)
                if disease_name:
                    disease = self.get_or_create_disease(
                        disease_name,
                        mechanism=mig_mech,
                        site_name="Nose",
                        description=description
                    )
                    if disease:
                        species.diseases.add(disease)

            # Parse Products (e.g., lugdunin, pneumolysin) from full_functions
            product_names = self.extract_products_from_text(full_functions)
            for pname in product_names:
                product = self.get_or_create_product(pname, mechanism="")
                if product:
                    species.products.add(product)
                    # Optional: create ProductEvent
                    ProductEvent.objects.get_or_create(
                        species=species,
                        site=nose,
                        product=product,
                        defaults={
                            "mechanism": f"Produced by {species_name} as noted in Functions.",
                            "evidence": genome_url or ""
                        }
                    )

            # Parse SpeciesInteractions (e.g., "Inhibits S. aureus")
            interactions = self.extract_interactions_from_text(full_functions, species_name)
            for target_name, itype, mech in interactions:
                target_species, _ = Species.objects.get_or_create(
                    name=target_name, defaults={"phyla": "Unknown"}
                )
                SpeciesInteraction.objects.get_or_create(
                    species_1=species,
                    species_2=target_species,
                    site=nose,
                    defaults={
                        "interaction_type": itype,
                        "mechanism": mech,
                        "evidence": genome_url or ""
                    }
                )

            species.save()

        self.stdout.write("✅ Finished Sheet1 import with all 7 columns parsed.")
