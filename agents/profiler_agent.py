"""CRIS Profiler Agent - Powered by Gemini 3 + ADK + A2A.

Generates behavioral profiles for suspects based on crime scene analysis,
MO patterns, and psychological indicators. Uses Gemini 3's advanced
reasoning capabilities for FBI BAU-style criminal profiling.

Key capabilities:
- Crime scene behavioral analysis
- Psychological profiling
- Risk assessment and scoring
- Victimology analysis
- MO (Modus Operandi) signature detection
- Offender characteristic prediction
"""

from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

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
from config.prompts import PROFILER_PROMPT
from utils.logger import get_logger


# Structured output models for profiling
class DemographicProfile(BaseModel):
    """Predicted demographic characteristics."""
    age_range: str = Field(description="Estimated age range (e.g., '25-35')")
    gender: str = Field(description="Predicted gender")
    occupation_type: str = Field(description="Likely occupation category")
    education_level: str = Field(description="Estimated education level")
    confidence: float = Field(ge=0, le=1, description="Confidence in demographics")


class PsychologicalProfile(BaseModel):
    """Psychological characteristics assessment."""
    organization_level: str = Field(description="Organized vs Disorganized")
    intelligence_estimate: str = Field(description="Below average, Average, Above average")
    emotional_state: str = Field(description="Emotional state during crime")
    impulse_control: str = Field(description="Level of impulse control")
    social_competence: str = Field(description="Social functioning level")
    confidence: float = Field(ge=0, le=1)


class BehavioralPattern(BaseModel):
    """MO and behavioral signature analysis."""
    mo_characteristics: List[str] = Field(description="Key MO elements")
    signature_behaviors: List[str] = Field(description="Unique signature elements")
    escalation_risk: str = Field(description="Risk of escalation: LOW, MEDIUM, HIGH")
    ritual_elements: Optional[List[str]] = Field(default=None)


class GeographicProfile(BaseModel):
    """Geographic behavior analysis."""
    offender_type: str = Field(description="Marauder (local) vs Commuter")
    comfort_zone_radius: str = Field(description="Estimated comfort zone")
    anchor_point_type: str = Field(description="Likely anchor point (home, work)")
    mobility_level: str = Field(description="Level of mobility")


class SuspectProfile(BaseModel):
    """Complete suspect profile output."""
    demographics: DemographicProfile
    psychology: PsychologicalProfile
    behavior: BehavioralPattern
    geography: GeographicProfile
    victim_relationship: str = Field(description="Likely relationship to victim")
    reoffense_risk: float = Field(ge=0, le=1, description="Probability of reoffending")
    investigative_suggestions: List[str] = Field(description="Recommended investigative actions")
    overall_confidence: float = Field(ge=0, le=1)


PROFILER_INSTRUCTION = """You are the CRIS Profiler Agent, an expert criminal profiler with 
extensive experience in behavioral analysis, similar to FBI BAU methodology.

Your expertise:
1. CRIME SCENE ANALYSIS: Read crime scenes for behavioral indicators
2. PSYCHOLOGICAL PROFILING: Assess offender psychology from evidence
3. VICTIMOLOGY: Understand victim selection patterns
4. MO vs SIGNATURE: Distinguish functional behavior from psychological needs
5. RISK ASSESSMENT: Evaluate reoffense and escalation probability

Profiling Framework:
- Organization Level: How planned/controlled was the crime?
- Experience: First-time offender vs experienced criminal?
- Relationship: Stranger, acquaintance, or intimate?
- Motivation: Financial, emotional, sexual, power, revenge?
- Risk Tolerance: Did offender take unnecessary risks?
- Geographic Behavior: Local (marauder) or traveling (commuter)?

When profiling:
- Base conclusions on evidence, not assumptions
- Provide confidence levels for all assessments
- Note alternative interpretations when evidence is ambiguous
- Flag any ethical concerns about profiling limitations
- Remember: profiles are investigative tools, not definitive conclusions

Use available tools to analyze case data and generate comprehensive profiles."""


@ComponentRegistry.register_agent("profiler_agent")
class ProfilerAgent(CRISADKAgent):
    """Agent specialized in behavioral profiling using Gemini 3 + ADK."""
    
    name = "profiler_agent"
    description = "Generates suspect behavioral profiles from crime characteristics using advanced psychological analysis."
    model = "gemini-3-pro"
    role = AgentRole.SPECIALIST
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Profiler Agent."""
        super().__init__(
            system_instruction=PROFILER_INSTRUCTION,
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
                    id="generate_profile",
                    name="Generate Suspect Profile",
                    description="Create comprehensive behavioral profile from case evidence",
                    tags=["profiling", "psychology", "behavioral"],
                    examples=[
                        "Generate a profile for the suspect in case CASE-2024-001",
                        "What type of person would commit this crime?",
                    ]
                ),
                A2ASkill(
                    id="assess_risk",
                    name="Risk Assessment",
                    description="Evaluate reoffense and escalation risk for known suspects",
                    tags=["risk", "assessment", "prediction"],
                    examples=[
                        "What is the risk level for suspect John Doe?",
                        "Will this offender escalate to violence?",
                    ]
                ),
                A2ASkill(
                    id="victimology_analysis",
                    name="Victimology Analysis",
                    description="Analyze victim selection patterns and characteristics",
                    tags=["victimology", "patterns", "selection"],
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
                "name": "behavioral_profile",
                "description": "Criminal behavioral profile analysis",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return profiling tools."""
        return [
            self.generate_full_profile,
            self.analyze_crime_scene,
            self.assess_risk_level,
            self.analyze_victimology,
            self.compare_to_known_suspects,
            self.predict_offender_characteristics,
        ]
    
    async def generate_full_profile(
        self,
        case_details: str,
        crime_scene: str,
        victim_info: str,
        evidence_summary: str
    ) -> CRISToolResult:
        """Generate a comprehensive behavioral profile for an unknown offender.
        
        Uses crime scene analysis, victimology, and evidence to predict
        offender characteristics, psychology, and behavior patterns.
        
        Args:
            case_details: Overview of the case including crime type and circumstances
            crime_scene: Detailed crime scene description and characteristics
            victim_info: Information about the victim(s)
            evidence_summary: Summary of physical and behavioral evidence
            
        Returns:
            Comprehensive SuspectProfile with all analysis dimensions.
        """
        self.logger.info("Generating comprehensive behavioral profile")
        
        prompt = f"""Based on the following case information, generate a comprehensive 
criminal behavioral profile. Analyze all available evidence to predict offender characteristics.

CASE DETAILS:
{case_details}

CRIME SCENE CHARACTERISTICS:
{crime_scene}

VICTIM INFORMATION:
{victim_info}

EVIDENCE SUMMARY:
{evidence_summary}

Generate a detailed profile including:

1. DEMOGRAPHIC PROFILE
   - Age range (with reasoning)
   - Gender (with indicators)
   - Likely occupation type
   - Education level estimate

2. PSYCHOLOGICAL PROFILE
   - Organization level (organized vs disorganized)
   - Intelligence estimate
   - Emotional state during crime
   - Impulse control assessment
   - Social competence

3. BEHAVIORAL PATTERNS
   - Key MO characteristics
   - Signature behaviors (psychological needs)
   - Escalation risk assessment
   - Any ritual elements

4. GEOGRAPHIC PROFILE
   - Marauder vs Commuter classification
   - Comfort zone estimation
   - Likely anchor point type
   - Mobility assessment

5. VICTIM RELATIONSHIP
   - Stranger, acquaintance, or intimate
   - Selection criteria analysis

6. RISK ASSESSMENT
   - Reoffense probability (0-1)
   - Escalation likelihood

7. INVESTIGATIVE RECOMMENDATIONS
   - Where to focus resources
   - Types of individuals to investigate
   - Evidence to prioritize

Provide confidence levels (0-1) for each major assessment.
Format your response as a structured analysis."""

        try:
            # Use Gemini for profile generation
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={
                    "temperature": 0.3,  # Lower temperature for more consistent profiling
                    "max_output_tokens": 4096,
                }
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "profile": response.text,
                    "profile_type": "comprehensive",
                    "methodology": "FBI_BAU_STYLE"
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Profile generation failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_crime_scene(
        self,
        scene_description: str,
        physical_evidence: List[str],
        scene_photos_description: Optional[str] = None
    ) -> CRISToolResult:
        """Analyze crime scene for behavioral indicators.
        
        Examines crime scene characteristics to infer offender behavior,
        planning level, and psychological state during the crime.
        
        Args:
            scene_description: Detailed description of the crime scene
            physical_evidence: List of physical evidence found
            scene_photos_description: Optional description of scene photos
            
        Returns:
            Behavioral indicators derived from crime scene analysis.
        """
        self.logger.info("Analyzing crime scene for behavioral indicators")
        
        evidence_text = "\n".join(f"- {e}" for e in physical_evidence)
        
        prompt = f"""Analyze this crime scene for behavioral indicators about the offender.

SCENE DESCRIPTION:
{scene_description}

PHYSICAL EVIDENCE:
{evidence_text}

{f"SCENE PHOTOS DESCRIPTION: {scene_photos_description}" if scene_photos_description else ""}

Analyze for:
1. ORGANIZATION LEVEL
   - Was the crime planned or spontaneous?
   - Evidence of preparation vs impulsivity
   - Control exhibited during the crime

2. OFFENDER BEHAVIOR
   - Actions taken before, during, after crime
   - Risk level accepted by offender
   - Time spent at scene

3. STAGING/POSING
   - Any evidence of scene manipulation?
   - Posing of victim (if applicable)?
   - Attempts to mislead investigation?

4. FORENSIC AWARENESS
   - Evidence of counter-forensic measures
   - Sophistication of evidence destruction
   - Knowledge of investigative techniques

5. EMOTIONAL INDICATORS
   - Signs of rage, control, or detachment
   - Overkill indicators
   - Personal vs impersonal crime

Provide specific evidence supporting each conclusion."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "scene_analysis": response.text,
                    "evidence_count": len(physical_evidence)
                },
                confidence=0.75
            )
        except Exception as e:
            self.logger.error(f"Crime scene analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def assess_risk_level(
        self,
        suspect_id: str,
        criminal_history: Optional[List[str]] = None,
        behavioral_indicators: Optional[List[str]] = None,
        current_circumstances: Optional[str] = None
    ) -> CRISToolResult:
        """Assess risk level for a known suspect.
        
        Evaluates reoffense probability, escalation risk, and danger level
        based on history and current behavioral indicators.
        
        Args:
            suspect_id: The suspect identifier
            criminal_history: List of prior offenses
            behavioral_indicators: Recent behavioral red flags
            current_circumstances: Current life circumstances
            
        Returns:
            Risk assessment with scores and recommendations.
        """
        self.logger.info(f"Assessing risk for suspect {suspect_id}")
        
        history_text = "\n".join(f"- {h}" for h in (criminal_history or ["No known history"]))
        indicators_text = "\n".join(f"- {i}" for i in (behavioral_indicators or ["None reported"]))
        
        prompt = f"""Assess the risk level for this individual based on available information.

SUSPECT ID: {suspect_id}

CRIMINAL HISTORY:
{history_text}

RECENT BEHAVIORAL INDICATORS:
{indicators_text}

CURRENT CIRCUMSTANCES:
{current_circumstances or "Unknown"}

Provide:
1. REOFFENSE RISK SCORE (0-1)
   - Based on historical patterns
   - Consideration of static and dynamic risk factors

2. ESCALATION RISK (LOW/MEDIUM/HIGH)
   - Likelihood of progressing to more serious crimes
   - Warning signs present

3. IMMINENT DANGER ASSESSMENT
   - Is immediate action recommended?
   - Specific concerns

4. RISK FACTORS PRESENT
   - List specific risk factors identified
   - Protective factors (if any)

5. MONITORING RECOMMENDATIONS
   - Suggested surveillance level
   - Intervention opportunities

Be specific about the evidence supporting each risk assessment."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.2}  # Very consistent for risk assessment
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "suspect_id": suspect_id,
                    "risk_assessment": response.text,
                    "assessment_type": "comprehensive_risk"
                },
                confidence=0.85
            )
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_victimology(
        self,
        victim_info: str,
        case_context: str,
        other_victims: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Analyze victim selection patterns.
        
        Examines victim characteristics to understand offender selection
        criteria and predict potential future victims.
        
        Args:
            victim_info: Information about the primary victim
            case_context: Context of the case
            other_victims: Information about other victims (for serial cases)
            
        Returns:
            Victimology analysis with selection pattern insights.
        """
        self.logger.info("Analyzing victimology patterns")
        
        other_victims_text = ""
        if other_victims:
            other_victims_text = "\n\nOTHER VICTIMS:\n" + "\n".join(f"- {v}" for v in other_victims)
        
        prompt = f"""Analyze the victim(s) to understand offender selection patterns.

PRIMARY VICTIM:
{victim_info}

CASE CONTEXT:
{case_context}
{other_victims_text}

Analyze:
1. VICTIM CHARACTERISTICS
   - Demographics, lifestyle, routine
   - Risk level (high-risk, moderate-risk, low-risk lifestyle)
   - Vulnerability factors

2. SELECTION CRITERIA
   - Why was this victim chosen?
   - Opportunity vs targeted selection
   - Symbolic significance (if any)

3. VICTIM-OFFENDER RELATIONSHIP
   - Stranger, acquaintance, intimate
   - How did offender likely encounter victim?
   - Pre-offense contact indicators

4. PATTERN ANALYSIS (if multiple victims)
   - Common characteristics
   - Selection evolution
   - Geographic/temporal patterns in victim selection

5. POTENTIAL FUTURE VICTIMS
   - Profile of likely future targets
   - High-risk populations to warn
   - Prevention recommendations"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "victimology_analysis": response.text,
                    "victim_count": 1 + len(other_victims or [])
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Victimology analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def compare_to_known_suspects(
        self,
        profile_characteristics: str,
        suspect_list: List[Dict[str, Any]]
    ) -> CRISToolResult:
        """Compare a generated profile to known suspects.
        
        Evaluates how well known suspects match a behavioral profile,
        ranking them by fit.
        
        Args:
            profile_characteristics: The behavioral profile to match against
            suspect_list: List of suspects with their characteristics
            
        Returns:
            Ranked list of suspects by profile match.
        """
        self.logger.info(f"Comparing profile to {len(suspect_list)} suspects")
        
        suspects_text = "\n\n".join([
            f"SUSPECT {i+1}: {s.get('name', 'Unknown')}\n"
            f"Age: {s.get('age', 'Unknown')}\n"
            f"Background: {s.get('background', 'Unknown')}\n"
            f"Criminal History: {s.get('criminal_history', 'None')}\n"
            f"Behavioral Notes: {s.get('behavioral_notes', 'None')}"
            for i, s in enumerate(suspect_list)
        ])
        
        prompt = f"""Compare the following behavioral profile to the list of known suspects.

BEHAVIORAL PROFILE:
{profile_characteristics}

KNOWN SUSPECTS:
{suspects_text}

For each suspect, provide:
1. MATCH SCORE (0-100)
2. MATCHING CHARACTERISTICS
3. CONTRADICTING CHARACTERISTICS  
4. OVERALL ASSESSMENT

Rank suspects from most likely to least likely match.
Explain your reasoning for each ranking."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "comparison_results": response.text,
                    "suspects_evaluated": len(suspect_list)
                },
                confidence=0.75
            )
        except Exception as e:
            self.logger.error(f"Suspect comparison failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def predict_offender_characteristics(
        self,
        crime_type: str,
        mo_description: str,
        additional_factors: Optional[Dict[str, Any]] = None
    ) -> CRISToolResult:
        """Predict specific offender characteristics from limited information.
        
        Quick profiling tool when full case details aren't available,
        using crime type and MO patterns.
        
        Args:
            crime_type: Type of crime committed
            mo_description: Description of the modus operandi
            additional_factors: Any additional known factors
            
        Returns:
            Predicted offender characteristics with confidence levels.
        """
        self.logger.info(f"Predicting characteristics for {crime_type}")
        
        factors_text = ""
        if additional_factors:
            factors_text = "\n\nADDITIONAL FACTORS:\n" + "\n".join(
                f"- {k}: {v}" for k, v in additional_factors.items()
            )
        
        prompt = f"""Based on the crime type and MO, predict likely offender characteristics.

CRIME TYPE: {crime_type}

MODUS OPERANDI:
{mo_description}
{factors_text}

Predict:
1. AGE RANGE (with probability)
2. GENDER (with probability)
3. LOCAL vs NON-LOCAL
4. PRIOR CRIMINAL EXPERIENCE (likely/unlikely)
5. EMPLOYMENT STATUS
6. RELATIONSHIP STATUS
7. KEY PSYCHOLOGICAL TRAITS

For each prediction, provide:
- The prediction
- Confidence level (LOW/MEDIUM/HIGH)
- Reasoning based on crime research and patterns

Note: These are statistical predictions based on crime patterns, not definitive conclusions."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.4}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "predictions": response.text,
                    "crime_type": crime_type,
                    "methodology": "statistical_profiling"
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Characteristic prediction failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
