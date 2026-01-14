# MasterThesis - NBREATH_DB - Nasal Bacterial & REspiratory Atlas in Humans DataBase

A comprehensive web application designed to model, visualize, and analyze the complex relationships between nasal microbiome species, their interactions, migration patterns, and contributions to disease pathogenesis.

## Overview

This project serves as a research platform for investigating microbial ecology within the nasal cavity and its systemic effects. It enables researchers to:
- Catalog microbial species, molecular products, and diseases.
- Track species presence and migration across different body sites.
- Visualize complex biological networks using interactive graphs.
- Analyze mechanisms of disease causation and species interactions.

## Technology Stack

- **Backend**: Django 5.0 (Python)
- **Database (Relational)**: PostgreSQL
- **Database (Graph)**: Neo4j
- **Web Server**: Nginx
- **Visualization**: D3.js (Interactive Diagrams)
- **Dependencies**: pandas, openpyxl, django-lucide-icons
- **Infrastructure**: Docker & Docker Compose

## Architecture

The system is containerized and composed of four main services:

1.  **Web (Django)**: The core application logic, API endpoints, and admin interface.
2.  **Postgres**: The primary relational database for storing structured data (Species, Diseases, etc.).
3.  **Neo4j**: A graph database used for visualizing and querying complex relationships.
4.  **Nginx**: A reverse proxy giving access to the application.

## Features

Based on the current implementation, the system supports:

### Data Management (CRUD)
Comprehensive management forms and APIs for:
- **Species**: Microbial organisms with taxonomic details.
- **Body Sites**: Anatomical locations for species definitions.
- **Diseases**: Pathological conditions linked to microbiome activity.
- **Products**: Molecular substances produced by species.
- **Interactions**: Synergistic or antagonistic relationships between species.
- **Migrations**: Movement patterns of species between body sites.
- **Product Events**: Events triggered by products leading to physiological changes.

### Visualization & Analysis
- **Graph View**: Interactive network visualization of species and their relationships.
- **Expanded Graph**: Advanced D3.js visualization allowing dynamic node expansion and exploration.
- **Neo4j Integration**: Automatic synchronization of relational data to Neo4j for graph analysis.

## Installation & Setup

### Prerequisites
- [Docker](https://www.docker.com/) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/) installed.

### Quick Start

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd MasterThesis
    ```

2.  **Start Services**
    Launch the entire stack using Docker Compose:
    ```bash
    docker-compose up -d
    ```

3.  **Initialize the Database**
    Apply migrations to set up the PostgreSQL schema:
    ```bash
    docker exec -it NasoBiomeKnowlegeBase python manage.py migrate
    ```

4.  **Create Admin User**
    Create a superuser to access the Django admin panel:
    ```bash
    docker exec -it NasoBiomeKnowlegeBase python manage.py createsuperuser
    ```

### Accessing the Application

- **Main Application**: [http://localhost](http://localhost)
- **Admin Panel**: [http://localhost/admin](http://localhost/admin)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (Default user/pass: `neo4j` / `neo4jpassword`)

## API Endpoints

The application provides the following key endpoints:

| Feature | Endpoint | Description |
| :--- | :--- | :--- |
| **Species** | `/species/` | List, Add, details, and export species. |
| **Body Sites** | `/bodysites/` | Manage anatomical locations. |
| **Diseases** | `/diseases/` | Manage disease records. |
| **Products** | `/products/` | Manage molecular products. |
| **Interactions** | `/interactions/` | Manage species interactions. |
| **Migrations** | `/migrations/` | Manage migration patterns. |
| **Graph** | `/graph/` | View the standard graph visualization. |
| **Expanded Graph** | `/api/get_expanded_graph_data/` | API for dynamic graph data. |
| **Export** | `/export-all/` | Trigger bulk export to Neo4j. |

## Contributing

This is a Master's Thesis project. Contributions should follow standard pull request workflows.
