"""Geo-Intelligence Agent.

Analyzes spatial patterns, hotspots, and suspect movement.
"""

from typing import Any, List, Optional

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.registry import ComponentRegistry


@ComponentRegistry.register_agent("geo_intel_agent")
class GeoIntelAgent(BaseAgent):
    """Agent specialized in geospatial intelligence and crime mapping."""
    
    name = "geo_intel_agent"
    description = "Analyzes crime locations for spatial patterns and hotspot discovery."
    
    async def process(self, input: AgentInput) -> AgentOutput:
        """Perform geospatial analysis."""
        self.logger.info(f"Running geo-intel for case: {input.case_id}")
        
        # Real implementation would query Neo4j for locations and use GeoPandas
        locations = input.parameters.get("locations", [])
        
        # Mock results
        analysis_result = {
            "hotspots": [
                {"lat": 40.7128, "lon": -74.0060, "intensity": 0.9, "label": "Primary Cluster"},
                {"lat": 40.7200, "lon": -74.0100, "intensity": 0.4, "label": "Secondary Cluster"}
            ],
            "spatial_signature": "Directional bias towards NW, proximity to transit hubs.",
            "journey_to_crime": "Average distance: 2.4 miles. Suggests local resident."
        }
        
        return AgentOutput(
            agent_name=self.name,
            success=True,
            data=analysis_result,
            confidence=0.75
        )

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="hotspot_discovery",
                description="Identify clusters of criminal activity",
                input_types=["locations"],
                output_types=["map_layers"]
            ),
            AgentCapability(
                name="geographic_profiling",
                description="Estimate suspect anchor point (residence)",
                input_types=["crime_series"],
                output_types=["predicted_anchor"]
            )
        ]
