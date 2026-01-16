"""CRIS OSINT Agent - Powered by Gemini 3 + ADK + A2A.

Analyzes open-source intelligence and digital footprints.
Uses Gemini 3's capabilities to process and analyze publicly
available information for investigative purposes.

Key capabilities:
- Social media pattern analysis
- Public records analysis
- Digital behavior profiling
- Communication pattern analysis
- Online presence mapping
- Sentiment and threat analysis
"""

from typing import Any, AsyncIterator, Callable, Dict, List, Optional

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


OSINT_INSTRUCTION = """You are the CRIS OSINT Agent, specialized in open-source 
intelligence gathering and digital footprint analysis.

Your expertise:
1. SOCIAL MEDIA ANALYSIS: Analyze patterns in social media activity
2. DIGITAL PROFILING: Build profiles from online presence
3. PUBLIC RECORDS: Analyze publicly available records and data
4. NETWORK MAPPING: Map online relationships and connections
5. SENTIMENT ANALYSIS: Assess emotional state and intent from posts

OSINT Principles:
- Only analyze publicly available information
- Respect privacy boundaries and legal limitations
- Document sources for all findings
- Assess reliability of each source
- Cross-reference multiple sources when possible

When analyzing:
- Note the source and reliability of each piece of information
- Distinguish between facts and inferences
- Flag any ethical concerns about data usage
- Consider that online personas may differ from reality
- Be aware of potential misinformation

Use available tools to gather and analyze open-source intelligence."""


@ComponentRegistry.register_agent("osint_agent")
class OSINTAgent(CRISADKAgent):
    """Agent specialized in OSINT analysis using Gemini 3 + ADK."""
    
    name = "osint_agent"
    description = "Analyzes digital footprints and open-source intelligence for investigations."
    model = "gemini-2.0-flash"
    role = AgentRole.SPECIALIST
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the OSINT Agent."""
        super().__init__(
            system_instruction=OSINT_INSTRUCTION,
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
                    id="analyze_digital_footprint",
                    name="Digital Footprint Analysis",
                    description="Analyze a person's online presence and digital footprint",
                    tags=["osint", "digital", "footprint"],
                    examples=[
                        "What is the digital footprint of John Doe?",
                        "Analyze online presence for this suspect",
                    ]
                ),
                A2ASkill(
                    id="social_media_analysis",
                    name="Social Media Analysis",
                    description="Analyze social media activity patterns and content",
                    tags=["social", "media", "analysis"],
                ),
                A2ASkill(
                    id="threat_assessment",
                    name="Online Threat Assessment",
                    description="Assess potential threats from online activity",
                    tags=["threat", "assessment", "online"],
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
                "name": "osint_analysis",
                "description": "Open-source intelligence analysis",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return OSINT analysis tools."""
        return [
            self.analyze_digital_footprint,
            self.analyze_social_media_content,
            self.map_online_network,
            self.assess_online_threat,
            self.analyze_communication_patterns,
            self.search_public_records,
            self.analyze_sentiment_timeline,
        ]
    
    async def analyze_digital_footprint(
        self,
        subject_identifiers: Dict[str, str],
        known_platforms: Optional[List[str]] = None,
        time_range: Optional[str] = None
    ) -> CRISToolResult:
        """Analyze the digital footprint of a subject.
        
        Examines online presence across platforms to build a
        comprehensive digital profile.
        
        Args:
            subject_identifiers: Known identifiers (name, email, handles, etc.)
            known_platforms: Platforms where subject is known to be active
            time_range: Time period to focus analysis on
            
        Returns:
            Digital footprint analysis with platform presence and patterns.
        """
        self.logger.info("Analyzing digital footprint")
        
        identifiers_text = "\n".join([f"- {k}: {v}" for k, v in subject_identifiers.items()])
        platforms_text = ", ".join(known_platforms) if known_platforms else "Unknown"
        
        prompt = f"""Analyze the digital footprint for this subject based on provided identifiers.

KNOWN IDENTIFIERS:
{identifiers_text}

KNOWN PLATFORMS: {platforms_text}
TIME RANGE: {time_range or "All available"}

NOTE: This is a simulated analysis. In production, this would integrate with 
actual OSINT tools and APIs.

Provide a framework analysis for:

1. PLATFORM PRESENCE ASSESSMENT
   - Likely platforms based on demographics
   - Priority platforms to investigate
   - Expected content types

2. IDENTITY CORRELATION
   - How identifiers might connect across platforms
   - Username patterns to search
   - Email variations to check

3. DIGITAL BEHAVIOR PROFILE
   - Expected posting patterns
   - Content themes likely
   - Engagement style

4. PRIVACY ASSESSMENT
   - Likely privacy settings
   - Information exposure risk
   - Vulnerability points

5. INVESTIGATION STRATEGY
   - Priority search targets
   - Tools to use
   - Legal considerations

6. RED FLAGS TO WATCH
   - Concerning patterns to look for
   - Deception indicators
   - Multiple identity signs

7. DOCUMENTATION NEEDS
   - What to preserve
   - Chain of custody considerations
   - Screenshot priorities

This framework guides the actual OSINT investigation."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "identifiers_provided": list(subject_identifiers.keys()),
                    "note": "Framework analysis - integrate with actual OSINT tools for live data"
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Digital footprint analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_social_media_content(
        self,
        posts: List[Dict[str, Any]],
        platform: str,
        analysis_focus: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Analyze social media posts for investigative insights.
        
        Examines content, patterns, and metadata from social media
        posts to extract intelligence.
        
        Args:
            posts: List of posts with content, timestamps, engagement
            platform: Social media platform
            analysis_focus: Specific aspects to focus on
            
        Returns:
            Content analysis with behavioral insights.
        """
        self.logger.info(f"Analyzing {len(posts)} posts from {platform}")
        
        posts_text = "\n\n".join([
            f"POST {i+1} ({p.get('timestamp', 'Unknown time')}):\n"
            f"Content: {p.get('content', 'No content')}\n"
            f"Engagement: {p.get('engagement', 'Unknown')}"
            for i, p in enumerate(posts[:20])
        ])
        
        focus_text = ", ".join(analysis_focus) if analysis_focus else "General analysis"
        
        prompt = f"""Analyze these social media posts for investigative intelligence.

PLATFORM: {platform}
ANALYSIS FOCUS: {focus_text}
NUMBER OF POSTS: {len(posts)}

POSTS (showing up to 20):
{posts_text}

Analyze:

1. CONTENT THEMES
   - Primary topics discussed
   - Recurring themes
   - Unusual or concerning content

2. BEHAVIORAL PATTERNS
   - Posting frequency and timing
   - Engagement patterns
   - Response behaviors

3. EMOTIONAL ANALYSIS
   - Dominant emotional tone
   - Emotional trajectory over time
   - Concerning emotional indicators

4. RELATIONSHIP INDICATORS
   - People frequently mentioned
   - Interaction patterns
   - Relationship dynamics

5. LOCATION INDICATORS
   - Places mentioned
   - Check-ins or location tags
   - Travel patterns

6. LIFESTYLE INDICATORS
   - Activities and interests
   - Work/schedule patterns
   - Financial indicators

7. CONCERNING CONTENT
   - Threats or violent language
   - Illegal activity references
   - Mental health concerns

8. INTELLIGENCE VALUE
   - Key findings for investigation
   - Leads to pursue
   - Corroboration opportunities"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "platform": platform,
                    "posts_analyzed": len(posts)
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Social media analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def map_online_network(
        self,
        subject_identifier: str,
        connections: List[Dict[str, Any]],
        interaction_data: Optional[List[Dict[str, Any]]] = None
    ) -> CRISToolResult:
        """Map the online social network of a subject.
        
        Analyzes connections and interactions to understand the
        subject's online social network.
        
        Args:
            subject_identifier: Primary identifier for the subject
            connections: List of known connections with metadata
            interaction_data: Data about interactions between connections
            
        Returns:
            Network map with relationship analysis.
        """
        self.logger.info(f"Mapping online network for {subject_identifier}")
        
        connections_text = "\n".join([
            f"- {c.get('name', 'Unknown')}: {c.get('relationship', 'Unknown')} "
            f"(Platform: {c.get('platform', 'Unknown')})"
            for c in connections[:30]
        ])
        
        interactions_text = ""
        if interaction_data:
            interactions_text = "\n\nINTERACTION DATA:\n" + "\n".join([
                f"- {i.get('from')} -> {i.get('to')}: {i.get('type', 'interaction')}"
                for i in interaction_data[:20]
            ])
        
        prompt = f"""Map and analyze the online social network for this subject.

SUBJECT: {subject_identifier}

KNOWN CONNECTIONS ({len(connections)} total):
{connections_text}
{interactions_text}

Analyze:

1. NETWORK STRUCTURE
   - Network size and density
   - Key clusters identified
   - Central figures

2. RELATIONSHIP CLASSIFICATION
   - Close associates
   - Casual connections
   - Professional contacts
   - Suspicious connections

3. INFLUENCE ANALYSIS
   - Most influential connections
   - Information flow patterns
   - Opinion leaders in network

4. CONCERNING CONNECTIONS
   - Connections to persons of interest
   - Criminal associations
   - High-risk individuals

5. NETWORK DYNAMICS
   - Recent additions to network
   - Dropped connections
   - Changing relationship patterns

6. COMMUNICATION PATTERNS
   - Frequent communication partners
   - Communication timing patterns
   - Platform preferences

7. INVESTIGATIVE VALUE
   - Connections to interview
   - Surveillance priorities
   - Information sources

8. NETWORK VISUALIZATION NOTES
   - Suggested groupings
   - Relationship strength indicators
   - Key nodes to highlight"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "network_analysis": response.text,
                    "subject": subject_identifier,
                    "connections_analyzed": len(connections)
                },
                confidence=0.75
            )
        except Exception as e:
            self.logger.error(f"Network mapping failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def assess_online_threat(
        self,
        content_samples: List[str],
        subject_context: str,
        threat_indicators: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Assess potential threats from online content.
        
        Analyzes online content for threat indicators and
        assesses risk level.
        
        Args:
            content_samples: Samples of concerning content
            subject_context: Context about the subject
            threat_indicators: Specific indicators to look for
            
        Returns:
            Threat assessment with risk level and recommendations.
        """
        self.logger.info("Assessing online threat level")
        
        content_text = "\n\n---\n\n".join([
            f"SAMPLE {i+1}:\n{c}" for i, c in enumerate(content_samples)
        ])
        
        indicators_text = ", ".join(threat_indicators) if threat_indicators else "General threat assessment"
        
        prompt = f"""Assess the threat level from this online content.

SUBJECT CONTEXT:
{subject_context}

THREAT INDICATORS TO ASSESS: {indicators_text}

CONTENT SAMPLES:
{content_text}

Provide:

1. THREAT CLASSIFICATION
   - Threat type (violence, harassment, terrorism, etc.)
   - Specificity (vague vs specific)
   - Credibility assessment

2. THREAT LEVEL (1-10)
   - Overall threat score
   - Classification (LOW/MODERATE/HIGH/CRITICAL)
   - Confidence in assessment

3. TARGET ANALYSIS
   - Identified or implied targets
   - Target specificity
   - Target vulnerability

4. CAPABILITY ASSESSMENT
   - Indicators of capability
   - Access to means
   - Planning indicators

5. INTENT INDICATORS
   - Direct statements of intent
   - Indirect indicators
   - Escalation patterns

6. TIMELINE ASSESSMENT
   - Imminent threat indicators
   - Timing references
   - Urgency level

7. RISK FACTORS
   - Aggravating factors
   - Mitigating factors
   - Triggering events

8. RECOMMENDED ACTIONS
   - Immediate actions needed
   - Notification requirements
   - Monitoring recommendations
   - Intervention options

IMPORTANT: If this assessment identifies an imminent threat, 
immediate law enforcement notification is required."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.2}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "threat_assessment": response.text,
                    "samples_analyzed": len(content_samples),
                    "disclaimer": "Assessment requires human review before action"
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Threat assessment failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_communication_patterns(
        self,
        communications: List[Dict[str, Any]],
        time_range: str,
        focus_contacts: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Analyze communication patterns from available data.
        
        Examines timing, frequency, and patterns in communications
        to extract intelligence.
        
        Args:
            communications: List of communication records
            time_range: Time period covered
            focus_contacts: Specific contacts to focus on
            
        Returns:
            Communication pattern analysis.
        """
        self.logger.info(f"Analyzing {len(communications)} communication records")
        
        comms_text = "\n".join([
            f"- {c.get('timestamp', 'Unknown')}: {c.get('type', 'message')} "
            f"with {c.get('contact', 'Unknown')} ({c.get('direction', 'unknown')})"
            for c in communications[:50]
        ])
        
        focus_text = ", ".join(focus_contacts) if focus_contacts else "All contacts"
        
        prompt = f"""Analyze communication patterns from this data.

TIME RANGE: {time_range}
FOCUS CONTACTS: {focus_text}
TOTAL RECORDS: {len(communications)}

COMMUNICATION RECORDS (showing up to 50):
{comms_text}

Analyze:

1. VOLUME PATTERNS
   - Overall communication volume
   - Trends over time
   - Unusual spikes or drops

2. TIMING PATTERNS
   - Peak communication times
   - Day-of-week patterns
   - Unusual timing (late night, etc.)

3. CONTACT ANALYSIS
   - Most frequent contacts
   - New contacts
   - Dropped contacts

4. COMMUNICATION TYPE PATTERNS
   - Preferred communication methods
   - Method by contact
   - Changes in method

5. BEHAVIORAL INDICATORS
   - Communication style changes
   - Urgency indicators
   - Secrecy indicators

6. NETWORK INSIGHTS
   - Communication clusters
   - Intermediaries
   - Isolated contacts

7. ANOMALIES
   - Unusual patterns
   - Breaks from routine
   - Concerning changes

8. INVESTIGATIVE LEADS
   - Contacts to investigate
   - Time periods of interest
   - Communication gaps to explain"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "records_analyzed": len(communications),
                    "time_range": time_range
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Communication analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def search_public_records(
        self,
        search_criteria: Dict[str, str],
        record_types: List[str],
        jurisdictions: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Search and analyze public records.
        
        Provides framework for public records search and analysis.
        
        Args:
            search_criteria: Criteria to search for (name, address, etc.)
            record_types: Types of records to search
            jurisdictions: Geographic jurisdictions to search
            
        Returns:
            Public records search framework and analysis guidance.
        """
        self.logger.info("Searching public records")
        
        criteria_text = "\n".join([f"- {k}: {v}" for k, v in search_criteria.items()])
        records_text = ", ".join(record_types)
        jurisdictions_text = ", ".join(jurisdictions) if jurisdictions else "All available"
        
        prompt = f"""Provide a framework for searching public records with these criteria.

SEARCH CRITERIA:
{criteria_text}

RECORD TYPES: {records_text}
JURISDICTIONS: {jurisdictions_text}

NOTE: This provides guidance for public records search. 
Actual searches require integration with records databases.

Provide:

1. SEARCH STRATEGY
   - Priority record types
   - Search sequence
   - Cross-reference approach

2. RECORD SOURCES
   - Federal records to check
   - State records to check
   - Local records to check
   - Online databases

3. SEARCH VARIATIONS
   - Name variations to try
   - Address history considerations
   - Alias possibilities

4. EXPECTED FINDINGS
   - Information typically available
   - Privacy limitations
   - Access restrictions

5. VERIFICATION APPROACH
   - How to verify findings
   - Cross-reference methods
   - Reliability assessment

6. LEGAL CONSIDERATIONS
   - Access requirements
   - FOIA considerations
   - Privacy laws

7. DOCUMENTATION
   - What to document
   - Source citation format
   - Chain of custody

8. FOLLOW-UP SEARCHES
   - Secondary searches based on findings
   - Related records to check
   - Expanded search criteria"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "search_framework": response.text,
                    "criteria": search_criteria,
                    "record_types": record_types,
                    "note": "Framework for search - integrate with actual records databases"
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Public records search failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_sentiment_timeline(
        self,
        content_timeline: List[Dict[str, Any]],
        subject_identifier: str,
        events_of_interest: Optional[List[Dict[str, str]]] = None
    ) -> CRISToolResult:
        """Analyze sentiment changes over time.
        
        Tracks emotional and sentiment changes in online content
        to identify concerning patterns.
        
        Args:
            content_timeline: Chronological content with timestamps
            subject_identifier: Who the content is from
            events_of_interest: Events to correlate with sentiment
            
        Returns:
            Sentiment timeline analysis with trend identification.
        """
        self.logger.info(f"Analyzing sentiment timeline for {subject_identifier}")
        
        timeline_text = "\n".join([
            f"- {c.get('timestamp', 'Unknown')}: \"{c.get('content', '')[:200]}...\""
            for c in content_timeline[:30]
        ])
        
        events_text = ""
        if events_of_interest:
            events_text = "\n\nEVENTS OF INTEREST:\n" + "\n".join([
                f"- {e.get('date', 'Unknown')}: {e.get('event', 'Unknown event')}"
                for e in events_of_interest
            ])
        
        prompt = f"""Analyze sentiment changes over time for this subject.

SUBJECT: {subject_identifier}

CONTENT TIMELINE ({len(content_timeline)} items, showing up to 30):
{timeline_text}
{events_text}

Analyze:

1. OVERALL SENTIMENT TRAJECTORY
   - Starting sentiment
   - Current sentiment
   - Direction of change

2. SENTIMENT PHASES
   - Identify distinct phases
   - Transitions between phases
   - Duration of each phase

3. EMOTIONAL INDICATORS
   - Dominant emotions over time
   - Emotional volatility
   - Concerning emotional patterns

4. EVENT CORRELATION
   - Sentiment changes around events
   - Trigger identification
   - Response patterns

5. WARNING SIGNS
   - Concerning sentiment shifts
   - Escalation indicators
   - Crisis indicators

6. LANGUAGE CHANGES
   - Vocabulary shifts
   - Tone changes
   - Communication style evolution

7. PREDICTIVE INDICATORS
   - Where is sentiment heading?
   - Risk of negative trajectory
   - Intervention opportunities

8. RECOMMENDATIONS
   - Monitoring priorities
   - Intervention timing
   - Support resources if applicable"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "subject": subject_identifier,
                    "timeline_length": len(content_timeline)
                },
                confidence=0.75
            )
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
