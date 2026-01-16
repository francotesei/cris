"""CRIS Witness Analysis Agent - Powered by Gemini 3 + ADK + A2A.

Analyzes witness statements for credibility, inconsistencies, and 
deception indicators. Uses Gemini 3's advanced language understanding
for deep statement analysis.

Key capabilities:
- Statement credibility assessment
- Inconsistency detection (internal and cross-witness)
- Deception indicator analysis
- Key fact extraction
- Timeline reconstruction from statements
- Follow-up question generation
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


WITNESS_INSTRUCTION = """You are the CRIS Witness Analysis Agent, an expert in 
statement analysis, credibility assessment, and deception detection.

Your expertise:
1. STATEMENT ANALYSIS: Extract facts, timeline, and key details from narratives
2. CREDIBILITY ASSESSMENT: Evaluate witness reliability and accuracy
3. INCONSISTENCY DETECTION: Find contradictions within and between statements
4. DECEPTION INDICATORS: Identify linguistic markers of potential deception
5. CROSS-REFERENCING: Compare multiple witness accounts for conflicts

Analysis Framework:
- CONTENT ANALYSIS: What facts are claimed? What's missing?
- LINGUISTIC ANALYSIS: Word choice, hedging, specificity
- STRUCTURAL ANALYSIS: Narrative flow, chronology, detail distribution
- BEHAVIORAL INDICATORS: (from written statements) emotional language, distancing

When analyzing:
- Distinguish between intentional deception and honest errors
- Consider witness factors (stress, time elapsed, relationship to events)
- Note that indicators suggest, not prove, deception
- Generate specific follow-up questions to clarify gaps
- Maintain objectivity - don't assume guilt or innocence

Use available tools to thoroughly analyze witness statements."""


@ComponentRegistry.register_agent("witness_agent")
class WitnessAgent(CRISADKAgent):
    """Agent specialized in witness statement analysis using Gemini 3 + ADK."""
    
    name = "witness_agent"
    description = "Analyzes witness statements for credibility, consistency, and deception indicators."
    model = "gemini-2.0-flash"
    role = AgentRole.SPECIALIST
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Witness Agent."""
        super().__init__(
            system_instruction=WITNESS_INSTRUCTION,
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
                    id="analyze_statement",
                    name="Statement Analysis",
                    description="Comprehensive analysis of a witness statement",
                    tags=["witness", "statement", "credibility"],
                    examples=[
                        "Analyze this witness statement for credibility",
                        "What are the key facts in this testimony?",
                    ]
                ),
                A2ASkill(
                    id="detect_deception",
                    name="Deception Detection",
                    description="Identify potential deception indicators in statements",
                    tags=["deception", "analysis", "linguistic"],
                ),
                A2ASkill(
                    id="cross_reference",
                    name="Cross-Reference Statements",
                    description="Compare multiple witness statements for conflicts",
                    tags=["comparison", "inconsistency", "witnesses"],
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
                "name": "witness_analysis",
                "description": "Witness statement analysis results",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return witness analysis tools."""
        return [
            self.analyze_statement,
            self.assess_credibility,
            self.detect_inconsistencies,
            self.analyze_deception_indicators,
            self.cross_reference_statements,
            self.generate_follow_up_questions,
            self.extract_timeline,
        ]
    
    async def analyze_statement(
        self,
        statement_text: str,
        witness_name: str,
        relationship_to_case: str,
        statement_date: str,
        context: Optional[str] = None
    ) -> CRISToolResult:
        """Perform comprehensive analysis of a witness statement.
        
        Extracts key facts, assesses credibility, identifies issues,
        and generates follow-up questions.
        
        Args:
            statement_text: The full witness statement
            witness_name: Name of the witness
            relationship_to_case: Witness's relationship (victim, bystander, etc.)
            statement_date: When the statement was taken
            context: Additional case context
            
        Returns:
            Comprehensive statement analysis.
        """
        self.logger.info(f"Analyzing statement from {witness_name}")
        
        prompt = f"""Perform a comprehensive analysis of this witness statement.

WITNESS: {witness_name}
RELATIONSHIP TO CASE: {relationship_to_case}
STATEMENT DATE: {statement_date}
{f"CASE CONTEXT: {context}" if context else ""}

STATEMENT:
\"\"\"
{statement_text}
\"\"\"

Provide thorough analysis:

1. KEY FACTS EXTRACTED
   - Who: People mentioned
   - What: Actions and events described
   - When: Times and dates mentioned
   - Where: Locations referenced
   - How: Methods and circumstances

2. TIMELINE RECONSTRUCTION
   - Chronological sequence of events
   - Time gaps or unclear periods
   - Temporal inconsistencies

3. CREDIBILITY INDICATORS
   - Level of detail (appropriate vs excessive vs lacking)
   - Consistency of narrative
   - Plausibility of claims
   - Sensory details present
   - Emotional content appropriateness

4. AREAS OF CONCERN
   - Vague or evasive sections
   - Potential contradictions
   - Missing information
   - Unusual phrasing

5. LINGUISTIC ANALYSIS
   - Pronoun usage patterns
   - Verb tense consistency
   - Hedging language
   - Certainty markers

6. OVERALL ASSESSMENT
   - Credibility score (0-100)
   - Key strengths of statement
   - Key weaknesses
   - Reliability classification (HIGH/MEDIUM/LOW)

7. FOLLOW-UP QUESTIONS
   - Questions to clarify gaps
   - Questions to test consistency
   - Questions about specific claims"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "witness": witness_name,
                    "statement_length": len(statement_text)
                },
                confidence=0.85
            )
        except Exception as e:
            self.logger.error(f"Statement analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def assess_credibility(
        self,
        statement_text: str,
        witness_background: Optional[str] = None,
        prior_statements: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Assess the credibility of a witness statement.
        
        Evaluates reliability based on content, consistency, and
        witness factors.
        
        Args:
            statement_text: The statement to assess
            witness_background: Background info on the witness
            prior_statements: Any previous statements from this witness
            
        Returns:
            Credibility assessment with detailed scoring.
        """
        self.logger.info("Assessing statement credibility")
        
        prior_text = ""
        if prior_statements:
            prior_text = "\n\nPRIOR STATEMENTS:\n" + "\n---\n".join(prior_statements)
        
        prompt = f"""Assess the credibility of this witness statement.

STATEMENT:
\"\"\"
{statement_text}
\"\"\"

{f"WITNESS BACKGROUND: {witness_background}" if witness_background else ""}
{prior_text}

Evaluate credibility across these dimensions:

1. CONTENT CREDIBILITY (0-100)
   - Are the facts plausible?
   - Is the level of detail appropriate?
   - Are there verifiable elements?

2. INTERNAL CONSISTENCY (0-100)
   - Does the narrative flow logically?
   - Are there self-contradictions?
   - Is the timeline coherent?

3. EXTERNAL CONSISTENCY (0-100)
   - Matches with prior statements?
   - Matches with known facts?
   - Matches with other witnesses?

4. WITNESS FACTORS (0-100)
   - Opportunity to observe
   - Potential bias or motive
   - Cognitive factors (stress, time elapsed)

5. LINGUISTIC INDICATORS (0-100)
   - Appropriate certainty levels
   - Natural language patterns
   - Absence of scripted elements

6. OVERALL CREDIBILITY SCORE
   - Weighted average (0-100)
   - Classification: HIGHLY CREDIBLE / CREDIBLE / QUESTIONABLE / LOW CREDIBILITY
   - Key factors affecting score

7. RECOMMENDATIONS
   - Should this witness be re-interviewed?
   - What corroboration is needed?
   - How should this statement be weighted?"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.2}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "assessment": response.text,
                    "has_prior_statements": bool(prior_statements)
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Credibility assessment failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def detect_inconsistencies(
        self,
        statement_text: str,
        comparison_data: Optional[Dict[str, Any]] = None
    ) -> CRISToolResult:
        """Detect inconsistencies within a statement and with known facts.
        
        Identifies contradictions, impossible claims, and conflicts
        with established evidence.
        
        Args:
            statement_text: The statement to analyze
            comparison_data: Known facts or other statements to compare against
            
        Returns:
            List of detected inconsistencies with severity ratings.
        """
        self.logger.info("Detecting inconsistencies in statement")
        
        comparison_text = ""
        if comparison_data:
            comparison_text = f"\n\nKNOWN FACTS/COMPARISON DATA:\n{comparison_data}"
        
        prompt = f"""Analyze this statement for inconsistencies.

STATEMENT:
\"\"\"
{statement_text}
\"\"\"
{comparison_text}

Identify all inconsistencies:

1. INTERNAL INCONSISTENCIES
   - Contradictions within the statement
   - Timeline impossibilities
   - Logical conflicts
   
   For each, provide:
   - Quote/reference from statement
   - Nature of inconsistency
   - Severity (MINOR/MODERATE/MAJOR)
   - Possible explanations (error vs deception)

2. EXTERNAL INCONSISTENCIES
   - Conflicts with known facts
   - Conflicts with physical evidence
   - Conflicts with other statements
   
   For each, provide:
   - The claim made
   - The conflicting information
   - Severity rating
   - Investigation recommendation

3. IMPOSSIBLE OR IMPLAUSIBLE CLAIMS
   - Physically impossible statements
   - Highly improbable claims
   - Claims requiring verification

4. GAPS AND OMISSIONS
   - Notable missing information
   - Unexplained time periods
   - Avoided topics

5. SUMMARY
   - Total inconsistencies found
   - Most significant issues
   - Overall reliability impact
   - Recommended actions"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "inconsistencies": response.text,
                    "had_comparison_data": bool(comparison_data)
                },
                confidence=0.85
            )
        except Exception as e:
            self.logger.error(f"Inconsistency detection failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def analyze_deception_indicators(
        self,
        statement_text: str,
        baseline_text: Optional[str] = None
    ) -> CRISToolResult:
        """Analyze statement for linguistic deception indicators.
        
        Examines language patterns associated with deception while
        noting that indicators are not proof of lying.
        
        Args:
            statement_text: The statement to analyze
            baseline_text: Optional truthful baseline from same person
            
        Returns:
            Deception indicator analysis with caveats.
        """
        self.logger.info("Analyzing deception indicators")
        
        baseline_section = ""
        if baseline_text:
            baseline_section = f"\n\nBASELINE (KNOWN TRUTHFUL) TEXT:\n\"\"\"\n{baseline_text}\n\"\"\""
        
        prompt = f"""Analyze this statement for linguistic indicators often associated with deception.

IMPORTANT CAVEAT: These indicators suggest areas for further investigation, not proof of deception.
Many truthful statements contain these patterns, and skilled deceivers may avoid them.

STATEMENT TO ANALYZE:
\"\"\"
{statement_text}
\"\"\"
{baseline_section}

Analyze for these indicator categories:

1. DISTANCING LANGUAGE
   - Reduced use of "I"
   - Passive voice usage
   - Depersonalization of events
   - Examples found:

2. HEDGING AND QUALIFICATION
   - Excessive qualifiers ("I think", "maybe", "sort of")
   - Uncertainty markers
   - Escape clauses
   - Examples found:

3. NEGATIVE STATEMENTS
   - Unprompted denials
   - "I would never..."
   - Excessive truthfulness claims
   - Examples found:

4. DETAIL ANOMALIES
   - Unusual detail distribution
   - Excessive irrelevant detail
   - Lack of detail at critical points
   - Examples found:

5. TEMPORAL ISSUES
   - Tense shifts
   - Vague time references
   - Out-of-sequence narration
   - Examples found:

6. EMOTIONAL INDICATORS
   - Inappropriate emotional content
   - Missing expected emotions
   - Performed emotions
   - Examples found:

7. COGNITIVE LOAD INDICATORS
   - Overly rehearsed sections
   - Unusual pauses in narrative
   - Simplified syntax at key points
   - Examples found:

8. OVERALL ASSESSMENT
   - Deception Indicator Score (0-100)
   - Confidence in assessment
   - Areas requiring follow-up
   - Alternative explanations to consider

REMEMBER: These are investigative leads, not conclusions."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "has_baseline": bool(baseline_text),
                    "disclaimer": "Indicators suggest areas for investigation, not proof of deception"
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Deception analysis failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def cross_reference_statements(
        self,
        statements: List[Dict[str, str]],
        focus_topics: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Cross-reference multiple witness statements for conflicts.
        
        Compares statements from different witnesses to identify
        agreements, conflicts, and unique information.
        
        Args:
            statements: List of {witness_name, statement_text} dicts
            focus_topics: Specific topics to focus comparison on
            
        Returns:
            Cross-reference analysis with conflict matrix.
        """
        self.logger.info(f"Cross-referencing {len(statements)} statements")
        
        statements_text = "\n\n---\n\n".join([
            f"WITNESS: {s['witness_name']}\n\"\"\"\n{s['statement_text']}\n\"\"\""
            for s in statements
        ])
        
        focus_text = ""
        if focus_topics:
            focus_text = f"\n\nFOCUS TOPICS: {', '.join(focus_topics)}"
        
        prompt = f"""Cross-reference these witness statements to identify agreements and conflicts.

STATEMENTS:
{statements_text}
{focus_text}

Provide:

1. AGREEMENT MATRIX
   - Facts all witnesses agree on
   - Partially corroborated facts
   - Confidence in agreed facts

2. CONFLICT ANALYSIS
   For each conflict found:
   - Topic of conflict
   - What each witness claims
   - Severity of conflict
   - Which version is more credible (and why)
   - Investigation recommendation

3. UNIQUE INFORMATION
   - Facts mentioned by only one witness
   - Significance of unique information
   - Verification needs

4. COVERAGE GAPS
   - Topics no witness addresses
   - Time periods with no coverage
   - Questions that remain unanswered

5. WITNESS RELIABILITY RANKING
   - Most reliable witness (and why)
   - Least reliable witness (and why)
   - Factors affecting ranking

6. SYNTHESIS
   - Most likely sequence of events
   - Confidence in synthesis
   - Key uncertainties

7. INVESTIGATION RECOMMENDATIONS
   - Which witnesses to re-interview
   - Specific questions for each
   - Evidence needed to resolve conflicts"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "analysis": response.text,
                    "witness_count": len(statements),
                    "focus_topics": focus_topics
                },
                confidence=0.85
            )
        except Exception as e:
            self.logger.error(f"Cross-reference failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def generate_follow_up_questions(
        self,
        statement_text: str,
        analysis_results: Optional[str] = None,
        investigation_priorities: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Generate targeted follow-up questions for a witness.
        
        Creates specific questions to clarify gaps, test consistency,
        and gather additional details.
        
        Args:
            statement_text: The original statement
            analysis_results: Results from prior analysis
            investigation_priorities: Key areas to focus questions on
            
        Returns:
            Categorized list of follow-up questions.
        """
        self.logger.info("Generating follow-up questions")
        
        prompt = f"""Generate targeted follow-up questions for this witness.

ORIGINAL STATEMENT:
\"\"\"
{statement_text}
\"\"\"

{f"ANALYSIS RESULTS: {analysis_results}" if analysis_results else ""}
{f"INVESTIGATION PRIORITIES: {', '.join(investigation_priorities)}" if investigation_priorities else ""}

Generate questions in these categories:

1. CLARIFICATION QUESTIONS
   - Questions to clarify vague statements
   - Questions about ambiguous references
   - Questions to fill information gaps

2. DETAIL QUESTIONS
   - Questions seeking additional sensory details
   - Questions about specific observations
   - Questions about timing and sequence

3. CONSISTENCY TEST QUESTIONS
   - Questions that approach same topic differently
   - Questions about peripheral details
   - Questions to verify specific claims

4. EXPANSION QUESTIONS
   - Questions about events before/after
   - Questions about other people present
   - Questions about related circumstances

5. CONFRONTATION QUESTIONS (if inconsistencies found)
   - Questions addressing specific contradictions
   - Questions about conflicting evidence
   - Questions about other witness accounts

For each question:
- State the question clearly
- Note what you're trying to learn
- Suggest follow-up based on possible answers

Provide at least 15 questions total, prioritized by importance."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "questions": response.text,
                    "priorities": investigation_priorities
                },
                confidence=0.9
            )
        except Exception as e:
            self.logger.error(f"Question generation failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def extract_timeline(
        self,
        statement_text: str,
        known_anchors: Optional[List[Dict[str, str]]] = None
    ) -> CRISToolResult:
        """Extract and reconstruct timeline from a statement.
        
        Identifies all temporal references and constructs a
        chronological sequence of events.
        
        Args:
            statement_text: The statement to analyze
            known_anchors: Known time points to anchor the timeline
            
        Returns:
            Reconstructed timeline with confidence levels.
        """
        self.logger.info("Extracting timeline from statement")
        
        anchors_text = ""
        if known_anchors:
            anchors_text = "\n\nKNOWN TIME ANCHORS:\n" + "\n".join([
                f"- {a['event']}: {a['time']}" for a in known_anchors
            ])
        
        prompt = f"""Extract and reconstruct the timeline from this statement.

STATEMENT:
\"\"\"
{statement_text}
\"\"\"
{anchors_text}

Provide:

1. TEMPORAL REFERENCES FOUND
   - All explicit times/dates mentioned
   - Relative time references ("then", "after", "before")
   - Duration references

2. RECONSTRUCTED TIMELINE
   For each event:
   - Estimated time (as specific as possible)
   - Event description
   - Confidence in timing (HIGH/MEDIUM/LOW)
   - Source quote from statement

3. TIME GAPS
   - Periods not accounted for
   - Duration of each gap
   - Significance of gap

4. TEMPORAL INCONSISTENCIES
   - Events out of logical sequence
   - Impossible timing claims
   - Conflicts with known anchors

5. DURATION ANALYSIS
   - Total time span covered
   - Time spent on each phase
   - Unusual duration claims

6. VISUALIZATION
   - Present as chronological list
   - Note uncertain placements
   - Highlight critical moments"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "timeline": response.text,
                    "had_anchors": bool(known_anchors)
                },
                confidence=0.8
            )
        except Exception as e:
            self.logger.error(f"Timeline extraction failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
