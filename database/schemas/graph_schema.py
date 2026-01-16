"""Neo4j Graph Schema Initialization.

Defines constraints, indexes, and schema types for the CRIS knowledge graph.
"""

from enum import Enum
from typing import List

from database.neo4j_client import Neo4jClient
from utils.logger import get_logger

logger = get_logger("database.schema")


class NodeType(str, Enum):
    """Labels for graph nodes."""
    CASE = "Case"
    PERSON = "Person"
    LOCATION = "Location"
    EVIDENCE = "Evidence"
    EVENT = "Event"
    VEHICLE = "Vehicle"
    ORGANIZATION = "Organization"
    PREDICTION = "Prediction"


class RelationshipType(str, Enum):
    """Types of graph relationships."""
    VICTIM_IN = "VICTIM_IN"
    SUSPECT_IN = "SUSPECT_IN"
    WITNESS_IN = "WITNESS_IN"
    PERSON_OF_INTEREST_IN = "PERSON_OF_INTEREST_IN"
    BELONGS_TO = "BELONGS_TO"
    PART_OF = "PART_OF"
    CRIME_SCENE_FOR = "CRIME_SCENE_FOR"
    KNOWS = "KNOWS"
    RELATED_TO = "RELATED_TO"
    WORKS_WITH = "WORKS_WITH"
    LIVES_AT = "LIVES_AT"
    WORKS_AT = "WORKS_AT"
    FREQUENTS = "FREQUENTS"
    OWNS = "OWNS"
    MEMBER_OF = "MEMBER_OF"
    FOUND_AT = "FOUND_AT"
    IMPLICATES = "IMPLICATES"
    CONNECTS = "CONNECTS"
    MENTIONED_IN = "MENTIONED_IN"
    PARTICIPATED_IN = "PARTICIPATED_IN"
    OCCURRED_AT = "OCCURRED_AT"
    PRECEDED = "PRECEDED"
    CAUSED = "CAUSED"
    PREDICTS_FOR = "PREDICTS_FOR"
    TARGETS = "TARGETS"
    SUGGESTS = "SUGGESTS"
    SIMILAR_TO = "SIMILAR_TO"


# Uniqueness constraints and indexes
SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
    "CREATE CONSTRAINT evidence_id IF NOT EXISTS FOR (e:Evidence) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT vehicle_id IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE",
    "CREATE CONSTRAINT org_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
    "CREATE CONSTRAINT prediction_id IF NOT EXISTS FOR (p:Prediction) REQUIRE p.id IS UNIQUE",
]

SCHEMA_INDEXES = [
    "CREATE INDEX case_title IF NOT EXISTS FOR (c:Case) ON (c.title)",
    "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)",
    "CREATE INDEX location_address IF NOT EXISTS FOR (l:Location) ON (l.address)",
    "CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:Event) ON (e.timestamp)",
]


async def initialize_schema(client: Neo4jClient) -> None:
    """Run all schema setup queries."""
    logger.info("Initializing Neo4j schema constraints and indexes...")
    
    for query in SCHEMA_CONSTRAINTS + SCHEMA_INDEXES:
        try:
            await client.execute_query(query)
            logger.debug(f"Executed: {query}")
        except Exception as e:
            logger.error(f"Failed to execute schema query: {query}. Error: {str(e)}")
            
    logger.info("Schema initialization complete.")
