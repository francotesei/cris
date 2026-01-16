"""CRIS CLI and Schema Initialization.

Entry point for database initialization and system setup.
"""

import asyncio
import sys

from database.neo4j_client import Neo4jClient
from database.schemas.graph_schema import initialize_schema
from core.plugin_loader import PluginLoader
from config.settings import get_settings
from utils.logger import setup_logging, get_logger


async def main():
    """Run system initialization."""
    setup_logging()
    logger = get_logger("cris.init")
    settings = get_settings()
    
    logger.info("CRIS - Starting System Initialization")
    
    # 1. Load Plugins
    loader = PluginLoader(settings.plugins_dir)
    loader.load_all(settings.enabled_plugins)
    
    # 2. Init Neo4j
    logger.info("Connecting to Neo4j...")
    neo4j = Neo4jClient()
    try:
        await neo4j.connect()
        await initialize_schema(neo4j)
        logger.info("Neo4j schema ready.")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j: {str(e)}")
        sys.exit(1)
    finally:
        await neo4j.close()

    logger.info("System initialization complete.")


if __name__ == "__main__":
    asyncio.run(main())
