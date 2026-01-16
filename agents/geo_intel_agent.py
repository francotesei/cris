"""CRIS Geo-Intelligence Agent - Powered by Gemini 3 + ADK + A2A.

Analyzes spatial and temporal patterns in criminal activity using
geospatial intelligence techniques. Combines geographic profiling
with Gemini 3's reasoning for predictive crime mapping.

Key capabilities:
- Crime hotspot detection and mapping
- Geographic profiling (anchor point estimation)
- Journey-to-crime analysis
- Temporal pattern detection
- Spatial clustering and prediction
- Movement pattern analysis
"""

from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple

from core.adk_agent import CRISADKAgent, AgentRole, CRISToolResult
from core.a2a_server import (
    A2AHandler,
    A2AAgentCard,
    A2ASkill,
    A2ARegistry,
    Task,
    Message,
)
from core.registry import ComponentRegistry
from utils.logger import get_logger


GEO_INTEL_INSTRUCTION = """You are the CRIS Geo-Intelligence Agent, an expert in 
geospatial crime analysis and geographic profiling.

Your expertise:
1. HOTSPOT ANALYSIS: Identify and analyze crime concentration areas
2. GEOGRAPHIC PROFILING: Estimate offender anchor points using spatial patterns
3. JOURNEY-TO-CRIME: Analyze travel patterns between offender residence and crime scenes
4. TEMPORAL PATTERNS: Detect time-based patterns in criminal activity
5. PREDICTIVE MAPPING: Forecast likely locations of future crimes

Geographic Profiling Methods:
- Rossmo's Formula: Calculate probability surfaces for offender residence
- Spatial Mean: Center of minimum distance to all crime sites
- Buffer Zone: Account for offender's comfort zone
- Decay Function: Model distance decay in offender behavior

When analyzing:
- Consider both spatial and temporal dimensions
- Account for environmental factors (roads, transit, barriers)
- Distinguish between marauder and commuter patterns
- Provide probability estimates, not certainties
- Note limitations of geographic analysis

Use available tools to analyze locations and generate spatial intelligence."""


@ComponentRegistry.register_agent("geo_intel_agent")
class GeoIntelAgent(CRISADKAgent):
    """Agent specialized in geospatial intelligence using Gemini 3 + ADK."""
    
    name = "geo_intel_agent"
    description = "Analyzes crime locations for spatial patterns, hotspots, and geographic profiling."
    model = "gemini-2.0-flash"
    role = AgentRole.SPECIALIST
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Geo-Intel Agent."""
        super().__init__(
            system_instruction=GEO_INTEL_INSTRUCTION,
            **kwargs
        )
        self._setup_a2a_handler()
    
    def _setup_a2a_handler(self) -> None:
        """Configure A2A handler."""
        agent_card = A2AAgentCard(
            name=self.name,
            description=self.description,
            version="2.0.0",
            skills=[
                A2ASkill(
                    id="hotspot_analysis",
                    name="Crime Hotspot Analysis",
                    description="Identify and analyze crime concentration areas",
                    tags=["spatial", "hotspot", "mapping"],
                    examples=[
                        "Where are the robbery hotspots in the downtown area?",
                        "Generate a crime heatmap for the last 90 days",
                    ]
                ),
                A2ASkill(
                    id="geographic_profile",
                    name="Geographic Profiling",
                    description="Estimate offender anchor point from crime locations",
                    tags=["profiling", "spatial", "prediction"],
                    examples=[
                        "Where does the serial burglar likely live?",
                        "Generate a geographic profile for this crime series",
                    ]
                ),
                A2ASkill(
                    id="predict_location",
                    name="Location Prediction",
                    description="Predict likely locations for future crimes or suspect activity",
                    tags=["prediction", "spatial", "forecast"],
                ),
            ]
        )
        
        handler = A2AHandler(
            agent_card=agent_card,
            task_handler=self._handle_a2a_task
        )
        A2ARegistry().register(handler)
    
    async def _handle_a2a_task(
        self,
        task: Task,
        message: Message
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle A2A tasks."""
        query = "".join(part.text or "" for part in message.parts)
        
        result = await self.run(
            query=query,
            session_id=task.session_id,
            context=task.metadata
        )
        
        yield {
            "type": "artifact",
            "artifact": {
                "name": "geo_analysis",
                "description": "Geospatial intelligence analysis",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return geo-intelligence tools."""
        return [
            self.generate_hotspot_map,
            self.create_geographic_profile,
            self.analyze_journey_to_crime,
            self.detect_temporal_patterns,
            self.predict_next_location,
            self.analyze_spatial_clustering,
        ]
    
    async def generate_hotspot_map(
        self,
        locations: List[Dict[str, Any]],
        crime_type: Optional[str] = None,
        time_range_days: int = 90
    ) -> CRISToolResult:
        """Generate a crime hotspot analysis from location data.
        
        Uses kernel density estimation concepts to identify areas with
        concentrated criminal activity.
        
        Args:
            locations: List of crime locations with lat, lon, and metadata
            crime_type: Optional filter for specific crime types
            time_range_days: Time window for analysis
            
        Returns:
            Hotspot analysis with clusters and intensity scores.
        """
        self.logger.info(f"Generating hotspot analysis for {len(locations)} locations")
        
        if not locations:
            return CRISToolResult(
                success=False,
                data={},
                message="No locations provided for analysis"
            )
        
        # Format locations for analysis
        locations_text = "\n".join([
            f"- ({loc.get('lat', 0)}, {loc.get('lon', 0)}): {loc.get('crime_type', 'Unknown')} "
            f"on {loc.get('date', 'Unknown date')}"
            for loc in locations[:50]  # Limit for prompt size
        ])
        
        prompt = f"""Analyze these crime locations to identify hotspots and patterns.

CRIME LOCATIONS ({len(locations)} total, showing up to 50):
{locations_text}

PARAMETERS:
- Crime Type Filter: {crime_type or 'All types'}
- Time Range: Last {time_range_days} days

Provide:
1. HOTSPOT IDENTIFICATION
   - Primary hotspot (highest concentration)
   - Secondary hotspots
   - Approximate center coordinates for each
   - Intensity rating (HIGH/MEDIUM/LOW)

2. SPATIAL DISTRIBUTION
   - Overall pattern (clustered, dispersed, linear)
   - Coverage area estimation
   - Density analysis

3. ENVIRONMENTAL FACTORS
   - What might explain these concentrations?
   - Nearby features (if inferable from coordinates)
   - Access routes considerations

4. PATROL RECOMMENDATIONS
   - Priority areas for increased presence
   - Optimal patrol routes
   - Time-based deployment suggestions

5. TREND ANALYSIS
   - Is the hotspot expanding or contracting?
   - Movement direction (if any)
   - Emerging areas of concern"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "locations_analyzed": len(locations),
                    "crime_type": crime_type,
                    "time_range_days": time_range_days
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Hotspot analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def create_geographic_profile(
        self,
        crime_locations: List[Tuple[float, float]],
        crime_type: str,
        additional_context: Optional[str] = None
    ) -> CRISToolResult:
        """Create a geographic profile to estimate offender anchor point.
        
        Uses geographic profiling principles to estimate where a serial
        offender likely lives or works based on crime locations.
        
        Args:
            crime_locations: List of (latitude, longitude) tuples
            crime_type: Type of crimes in the series
            additional_context: Additional case context
            
        Returns:
            Geographic profile with anchor point estimation.
        """
        self.logger.info(f"Creating geographic profile from {len(crime_locations)} locations")
        
        if len(crime_locations) < 3:
            return CRISToolResult(
                success=False,
                data={},
                message="Need at least 3 locations for geographic profiling"
            )
        
        # Calculate basic spatial statistics
        lats = [loc[0] for loc in crime_locations]
        lons = [loc[1] for loc in crime_locations]
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Calculate spread
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        
        locations_text = "\n".join([f"- Point {i+1}: ({lat}, {lon})" 
                                    for i, (lat, lon) in enumerate(crime_locations)])
        
        prompt = f"""Perform geographic profiling on this crime series to estimate offender anchor point.

CRIME TYPE: {crime_type}
NUMBER OF CRIMES: {len(crime_locations)}

CRIME LOCATIONS:
{locations_text}

CALCULATED STATISTICS:
- Spatial Mean (Center): ({center_lat:.6f}, {center_lon:.6f})
- Latitude Range: {lat_range:.4f} degrees
- Longitude Range: {lon_range:.4f} degrees

{f"ADDITIONAL CONTEXT: {additional_context}" if additional_context else ""}

Provide:
1. OFFENDER TYPE CLASSIFICATION
   - Marauder (operates from home base) or Commuter (travels to crime area)?
   - Confidence in classification

2. ANCHOR POINT ESTIMATION
   - Most likely anchor point coordinates
   - Secondary possible anchor points
   - Reasoning for estimation

3. BUFFER ZONE ANALYSIS
   - Estimated buffer zone (area offender avoids near home)
   - Implications for search area

4. SEARCH PRIORITY ZONES
   - High priority search area (coordinates/description)
   - Medium priority area
   - Low priority area

5. DISTANCE DECAY ANALYSIS
   - Pattern of distances from estimated anchor
   - Comfort zone radius
   - Maximum travel distance observed

6. RECOMMENDATIONS
   - Canvassing priorities
   - Database search parameters
   - Surveillance suggestions"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            return CRISToolResult(
            success=True,
                data={
                    "profile": response.text,
                    "spatial_mean": (center_lat, center_lon),
                    "crime_count": len(crime_locations),
                    "spread": {"lat_range": lat_range, "lon_range": lon_range}
                },
            confidence=0.75
        )
        except Exception as e:
            self.logger.error(f"Geographic profiling failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_journey_to_crime(
        self,
        suspect_residence: Tuple[float, float],
        crime_locations: List[Tuple[float, float]],
        suspect_info: Optional[str] = None
    ) -> CRISToolResult:
        """Analyze journey-to-crime patterns for a suspect.
        
        Examines the relationship between suspect's known locations
        and crime scenes to understand travel patterns.
        
        Args:
            suspect_residence: (lat, lon) of suspect's residence
            crime_locations: List of crime scene coordinates
            suspect_info: Additional suspect information
            
        Returns:
            Journey-to-crime analysis with pattern insights.
        """
        self.logger.info("Analyzing journey-to-crime patterns")
        
        # Calculate distances (simplified - in production use haversine)
        distances = []
        for lat, lon in crime_locations:
            # Approximate distance in km (very simplified)
            dist = ((lat - suspect_residence[0])**2 + 
                   (lon - suspect_residence[1])**2)**0.5 * 111  # rough km conversion
            distances.append(dist)
        
        avg_distance = sum(distances) / len(distances) if distances else 0
        max_distance = max(distances) if distances else 0
        min_distance = min(distances) if distances else 0
        
        locations_text = "\n".join([
            f"- Crime {i+1}: ({lat}, {lon}) - ~{distances[i]:.1f} km from residence"
            for i, (lat, lon) in enumerate(crime_locations)
        ])
        
        prompt = f"""Analyze journey-to-crime patterns for this suspect.

SUSPECT RESIDENCE: ({suspect_residence[0]}, {suspect_residence[1]})
{f"SUSPECT INFO: {suspect_info}" if suspect_info else ""}

CRIME LOCATIONS AND DISTANCES:
{locations_text}

DISTANCE STATISTICS:
- Average Distance: {avg_distance:.2f} km
- Maximum Distance: {max_distance:.2f} km
- Minimum Distance: {min_distance:.2f} km

Analyze:
1. TRAVEL PATTERN
   - Directional bias (N, S, E, W)?
   - Route preferences
   - Consistency of pattern

2. COMFORT ZONE
   - Does suspect stay within a comfort zone?
   - Buffer zone around residence?

3. DISTANCE DECAY
   - Does frequency decrease with distance?
   - Optimal hunting ground distance

4. ROUTE ANALYSIS
   - Likely travel routes
   - Transportation mode implications
   - Time considerations

5. BEHAVIORAL INSIGHTS
   - What does the pattern reveal about the offender?
   - Risk tolerance indicators
   - Planning vs opportunistic

6. PREDICTIVE VALUE
   - Where might they strike next based on pattern?
   - Areas to monitor"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "distance_stats": {
                        "average": avg_distance,
                        "max": max_distance,
                        "min": min_distance
                    },
                    "crime_count": len(crime_locations)
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Journey analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def detect_temporal_patterns(
        self,
        crime_timestamps: List[str],
        crime_type: Optional[str] = None
    ) -> CRISToolResult:
        """Detect temporal patterns in crime data.
        
        Analyzes time-based patterns including day of week, time of day,
        and seasonal variations.
        
        Args:
            crime_timestamps: List of crime timestamps (ISO format)
            crime_type: Optional crime type filter
            
        Returns:
            Temporal pattern analysis with peak times and cycles.
        """
        self.logger.info(f"Detecting temporal patterns in {len(crime_timestamps)} events")
        
        timestamps_text = "\n".join([f"- {ts}" for ts in crime_timestamps[:50]])
        
        prompt = f"""Analyze temporal patterns in this crime data.

CRIME TYPE: {crime_type or 'Mixed'}
NUMBER OF EVENTS: {len(crime_timestamps)}

TIMESTAMPS (showing up to 50):
{timestamps_text}

Analyze:
1. TIME OF DAY PATTERNS
   - Peak hours
   - Low activity periods
   - Shift patterns (if any)

2. DAY OF WEEK PATTERNS
   - Most active days
   - Weekend vs weekday comparison
   - Pattern consistency

3. MONTHLY/SEASONAL PATTERNS
   - Seasonal variations
   - Monthly trends
   - Holiday effects

4. INTERVAL ANALYSIS
   - Time between crimes
   - Acceleration or deceleration
   - Cooling-off periods

5. PREDICTIVE INSIGHTS
   - When is the next crime most likely?
   - High-risk time windows
   - Patrol scheduling recommendations

6. BEHAVIORAL IMPLICATIONS
   - What do patterns suggest about offender?
   - Employment implications
   - Lifestyle indicators"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "event_count": len(crime_timestamps),
                    "crime_type": crime_type
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Temporal pattern detection failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def predict_next_location(
        self,
        historical_locations: List[Dict[str, Any]],
        suspect_profile: Optional[str] = None,
        environmental_factors: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Predict likely locations for future criminal activity.
        
        Uses historical patterns and geographic profiling to forecast
        where the next crime might occur.
        
        Args:
            historical_locations: Past crime locations with metadata
            suspect_profile: Optional behavioral profile
            environmental_factors: Factors to consider (transit, landmarks, etc.)
            
        Returns:
            Location predictions with probability estimates.
        """
        self.logger.info("Predicting next likely location")
        
        locations_text = "\n".join([
            f"- ({loc.get('lat')}, {loc.get('lon')}): {loc.get('crime_type', 'Unknown')} "
            f"on {loc.get('date', 'Unknown')}"
            for loc in historical_locations[:30]
        ])
        
        factors_text = "\n".join([f"- {f}" for f in (environmental_factors or [])])
        
        prompt = f"""Predict the most likely location(s) for the next crime based on patterns.

HISTORICAL CRIME LOCATIONS:
{locations_text}

{f"SUSPECT PROFILE: {suspect_profile}" if suspect_profile else ""}

{f"ENVIRONMENTAL FACTORS TO CONSIDER:{chr(10)}{factors_text}" if factors_text else ""}

Provide:
1. PRIMARY PREDICTION
   - Most likely area/coordinates
   - Probability estimate (%)
   - Reasoning

2. SECONDARY PREDICTIONS
   - Alternative likely areas
   - Probability estimates

3. TIMING PREDICTION
   - Most likely time window
   - Day of week probability

4. TARGET TYPE PREDICTION
   - Likely target characteristics
   - Vulnerability factors

5. CONFIDENCE ASSESSMENT
   - Overall prediction confidence
   - Key uncertainties
   - Data limitations

6. PREVENTION RECOMMENDATIONS
   - Patrol deployment suggestions
   - Warning dissemination
   - Target hardening priorities"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "predictions": response.text,
                    "based_on_events": len(historical_locations)
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Location prediction failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_spatial_clustering(
        self,
        locations: List[Dict[str, Any]],
        cluster_distance_km: float = 1.0
    ) -> CRISToolResult:
        """Analyze spatial clustering of crime locations.
        
        Groups crimes by geographic proximity to identify patterns
        and potential serial crime clusters.
        
        Args:
            locations: Crime locations with metadata
            cluster_distance_km: Distance threshold for clustering
            
        Returns:
            Cluster analysis with identified groups and patterns.
        """
        self.logger.info(f"Analyzing spatial clustering for {len(locations)} locations")
        
        locations_text = "\n".join([
            f"- ID:{loc.get('id', i)}: ({loc.get('lat')}, {loc.get('lon')}) - "
            f"{loc.get('crime_type', 'Unknown')} on {loc.get('date', 'Unknown')}"
            for i, loc in enumerate(locations[:40])
        ])
        
        prompt = f"""Perform spatial clustering analysis on these crime locations.

LOCATIONS ({len(locations)} total):
{locations_text}

CLUSTERING PARAMETERS:
- Distance Threshold: {cluster_distance_km} km

Analyze:
1. CLUSTER IDENTIFICATION
   - Number of distinct clusters
   - Size of each cluster
   - Center point of each cluster

2. CLUSTER CHARACTERISTICS
   - Crime types in each cluster
   - Temporal span of each cluster
   - Density analysis

3. OUTLIER ANALYSIS
   - Isolated incidents
   - Potential new cluster seeds
   - Anomalies

4. SERIAL CRIME INDICATORS
   - Clusters suggesting serial activity
   - Pattern consistency within clusters
   - Linkage confidence

5. SPATIAL RELATIONSHIPS
   - Distance between clusters
   - Corridor patterns
   - Boundary analysis

6. STRATEGIC IMPLICATIONS
   - Resource allocation recommendations
   - Investigation priorities
   - Prevention strategies per cluster"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "locations_analyzed": len(locations),
                    "cluster_threshold_km": cluster_distance_km
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Spatial clustering failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
