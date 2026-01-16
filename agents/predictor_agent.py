"""CRIS Predictor Agent - Powered by Gemini 3 + ADK + A2A.

Runs simulations and generates forecasts for future criminal behavior.
Uses Gemini 3's reasoning capabilities combined with historical pattern
analysis for predictive intelligence.

Key capabilities:
- Behavioral simulation and forecasting
- Escalation risk prediction
- Scenario modeling ("what-if" analysis)
- Crime trend forecasting
- Resource allocation optimization
- Arrest probability estimation
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


PREDICTOR_INSTRUCTION = """You are the CRIS Predictor Agent, specialized in 
criminal behavior forecasting and predictive analysis.

Your expertise:
1. BEHAVIORAL FORECASTING: Predict future actions based on patterns
2. RISK MODELING: Assess escalation and reoffense probabilities
3. SCENARIO ANALYSIS: Model "what-if" situations
4. TREND PREDICTION: Forecast crime patterns and trends
5. RESOURCE OPTIMIZATION: Recommend optimal deployment strategies

Prediction Framework:
- Historical Pattern Analysis: What has the subject done before?
- Behavioral Indicators: What signals future behavior?
- Environmental Factors: What circumstances affect likelihood?
- Temporal Patterns: When are events most likely?
- Geographic Patterns: Where are events most likely?

When predicting:
- Always provide probability ranges, not certainties
- Explain the factors driving predictions
- Note confidence levels and uncertainty sources
- Consider multiple scenarios
- Acknowledge limitations of predictive modeling
- Emphasize that predictions are tools, not guarantees

Use available tools to generate evidence-based forecasts."""


@ComponentRegistry.register_agent("predictor_agent")
class PredictorAgent(CRISADKAgent):
    """Agent specialized in predictive modeling using Gemini 3 + ADK."""
    
    name = "predictor_agent"
    description = "Generates forecasts and risk simulations for criminal behavior patterns."
    model = "gemini-2.0-flash"
    role = AgentRole.SPECIALIST
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Predictor Agent."""
        super().__init__(
            system_instruction=PREDICTOR_INSTRUCTION,
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
                    id="predict_behavior",
                    name="Behavioral Prediction",
                    description="Forecast future criminal behavior based on patterns",
                    tags=["prediction", "behavior", "forecast"],
                    examples=[
                        "What is the suspect likely to do next?",
                        "Predict the next crime in this series",
                    ]
                ),
                A2ASkill(
                    id="assess_escalation",
                    name="Escalation Assessment",
                    description="Predict likelihood of escalation to more serious crimes",
                    tags=["escalation", "risk", "violence"],
                ),
                A2ASkill(
                    id="scenario_modeling",
                    name="Scenario Modeling",
                    description="Model different scenarios and their outcomes",
                    tags=["scenarios", "what-if", "simulation"],
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
                "name": "prediction_analysis",
                "description": "Predictive analysis results",
                "parts": [{"type": "text", "text": result["response"]}],
                "index": 0,
                "last_chunk": True
            }
        }
    
    def get_tools(self) -> List[Callable]:
        """Return prediction tools."""
        return [
            self.predict_next_action,
            self.assess_escalation_risk,
            self.model_scenarios,
            self.forecast_crime_trends,
            self.estimate_arrest_probability,
            self.optimize_resource_allocation,
            self.simulate_behavior_patterns,
        ]
    
    async def predict_next_action(
        self,
        subject_profile: str,
        behavioral_history: List[str],
        current_circumstances: str,
        time_horizon_days: int = 30
    ) -> CRISToolResult:
        """Predict the most likely next actions of a subject.
        
        Uses behavioral patterns and current circumstances to forecast
        probable future actions within a specified time horizon.
        
        Args:
            subject_profile: Profile of the subject (suspect/offender)
            behavioral_history: List of past behaviors/crimes
            current_circumstances: Current situation and known factors
            time_horizon_days: How far ahead to predict
            
        Returns:
            Ranked list of predicted actions with probabilities.
        """
        self.logger.info(f"Predicting next action for {time_horizon_days} day horizon")
        
        history_text = "\n".join([f"- {h}" for h in behavioral_history])
        
        prompt = f"""Predict the most likely next actions for this subject.

SUBJECT PROFILE:
{subject_profile}

BEHAVIORAL HISTORY:
{history_text}

CURRENT CIRCUMSTANCES:
{current_circumstances}

TIME HORIZON: Next {time_horizon_days} days

Provide:

1. MOST LIKELY ACTIONS (ranked by probability)
   For each predicted action:
   - Description of action
   - Probability estimate (%)
   - Likely timing within horizon
   - Key factors driving this prediction
   - Warning signs to watch for

2. TRIGGER ANALYSIS
   - What events might trigger action?
   - Accelerating factors
   - Inhibiting factors

3. LOCATION PREDICTIONS
   - Where is action most likely?
   - Alternative locations
   - Factors affecting location choice

4. VICTIM/TARGET PREDICTIONS
   - Likely target characteristics
   - Selection criteria
   - Vulnerability factors

5. METHOD PREDICTIONS
   - Likely MO elements
   - Evolution from past behavior
   - New elements to expect

6. TIMELINE SCENARIOS
   - Best case (no action)
   - Most likely timeline
   - Worst case (immediate action)

7. INTERVENTION OPPORTUNITIES
   - Points where intervention could prevent action
   - Recommended preventive measures
   - Monitoring priorities

CONFIDENCE ASSESSMENT:
- Overall prediction confidence
- Key uncertainties
- Data limitations"""

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
                    "time_horizon_days": time_horizon_days,
                    "history_events": len(behavioral_history)
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Action prediction failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def assess_escalation_risk(
        self,
        subject_id: str,
        crime_history: List[Dict[str, Any]],
        psychological_factors: Optional[str] = None,
        environmental_stressors: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Assess the risk of escalation to more serious crimes.
        
        Evaluates whether a subject is likely to progress to more
        violent or serious criminal behavior.
        
        Args:
            subject_id: Identifier for the subject
            crime_history: List of past crimes with details
            psychological_factors: Known psychological factors
            environmental_stressors: Current life stressors
            
        Returns:
            Escalation risk assessment with timeline estimates.
        """
        self.logger.info(f"Assessing escalation risk for subject {subject_id}")
        
        history_text = "\n".join([
            f"- {c.get('date', 'Unknown')}: {c.get('crime_type', 'Unknown')} - {c.get('details', 'No details')}"
            for c in crime_history
        ])
        
        stressors_text = "\n".join([f"- {s}" for s in (environmental_stressors or [])])
        
        prompt = f"""Assess the escalation risk for this subject.

SUBJECT ID: {subject_id}

CRIME HISTORY (chronological):
{history_text}

{f"PSYCHOLOGICAL FACTORS: {psychological_factors}" if psychological_factors else ""}

{f"ENVIRONMENTAL STRESSORS:{chr(10)}{stressors_text}" if stressors_text else ""}

Analyze:

1. ESCALATION PATTERN ANALYSIS
   - Has there been progression in severity?
   - Violence trajectory
   - Frequency changes
   - Sophistication evolution

2. ESCALATION RISK SCORE (0-100)
   - Current risk level
   - Risk classification (LOW/MODERATE/HIGH/CRITICAL)
   - Confidence in assessment

3. ESCALATION INDICATORS PRESENT
   - Warning signs observed
   - Risk factors identified
   - Protective factors present

4. LIKELY ESCALATION PATH
   - What type of escalation is most likely?
   - Probable next level of offense
   - Timeline estimate

5. TRIGGER ANALYSIS
   - What could trigger escalation?
   - Imminent triggers present?
   - Seasonal/temporal factors

6. VIOLENCE RISK SPECIFICALLY
   - Risk of violence (0-100)
   - Type of violence most likely
   - Potential victims

7. PREVENTION OPPORTUNITIES
   - Intervention points
   - De-escalation strategies
   - Monitoring recommendations

8. URGENCY ASSESSMENT
   - Is immediate action needed?
   - Recommended response level
   - Timeline for intervention"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "assessment": response.text,
                    "subject_id": subject_id,
                    "crimes_analyzed": len(crime_history)
                },
                confidence=0.75
            )
        except Exception as e:
            self.logger.error(f"Escalation assessment failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def model_scenarios(
        self,
        case_context: str,
        scenarios_to_model: List[str],
        current_evidence: Optional[str] = None
    ) -> CRISToolResult:
        """Model different scenarios and their likely outcomes.
        
        Performs "what-if" analysis to explore how different situations
        might develop.
        
        Args:
            case_context: Background on the case
            scenarios_to_model: List of scenarios to analyze
            current_evidence: Current evidence and known facts
            
        Returns:
            Detailed analysis of each scenario with probabilities.
        """
        self.logger.info(f"Modeling {len(scenarios_to_model)} scenarios")
        
        scenarios_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(scenarios_to_model)])
        
        prompt = f"""Model these scenarios and predict their likely outcomes.

CASE CONTEXT:
{case_context}

{f"CURRENT EVIDENCE: {current_evidence}" if current_evidence else ""}

SCENARIOS TO MODEL:
{scenarios_text}

For each scenario, provide:

1. SCENARIO ANALYSIS
   - Detailed description
   - Key assumptions
   - Probability of this scenario (%)

2. LIKELY OUTCOMES
   - Most probable outcome
   - Alternative outcomes
   - Timeline to outcome

3. EVIDENCE IMPLICATIONS
   - What evidence would support this scenario?
   - What evidence would contradict it?
   - Key indicators to watch

4. INVESTIGATION IMPLICATIONS
   - How should investigation proceed if true?
   - Resource requirements
   - Priority actions

5. RISK ASSESSMENT
   - Risks if this scenario is true
   - Risks of acting on this assumption
   - Risks of ignoring this scenario

After analyzing all scenarios:

6. COMPARATIVE ANALYSIS
   - Most likely scenario overall
   - Ranking by probability
   - Key differentiating factors

7. RECOMMENDED APPROACH
   - How to investigate across scenarios
   - Decision points
   - Contingency planning"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "scenario_analysis": response.text,
                    "scenarios_modeled": len(scenarios_to_model)
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Scenario modeling failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def forecast_crime_trends(
        self,
        historical_data: List[Dict[str, Any]],
        area: str,
        crime_types: Optional[List[str]] = None,
        forecast_days: int = 30
    ) -> CRISToolResult:
        """Forecast crime trends for an area.
        
        Analyzes historical patterns to predict future crime levels
        and patterns.
        
        Args:
            historical_data: Past crime data with dates and types
            area: Geographic area for forecast
            crime_types: Specific crime types to forecast
            forecast_days: How far ahead to forecast
            
        Returns:
            Crime trend forecast with confidence intervals.
        """
        self.logger.info(f"Forecasting crime trends for {area}")
        
        data_text = "\n".join([
            f"- {d.get('date')}: {d.get('crime_type')} at {d.get('location', 'Unknown')}"
            for d in historical_data[:100]
        ])
        
        types_text = ", ".join(crime_types) if crime_types else "All types"
        
        prompt = f"""Forecast crime trends based on historical data.

AREA: {area}
CRIME TYPES: {types_text}
FORECAST HORIZON: {forecast_days} days

HISTORICAL DATA ({len(historical_data)} records, showing up to 100):
{data_text}

Provide:

1. TREND ANALYSIS
   - Overall trend direction
   - Rate of change
   - Seasonality patterns
   - Day-of-week patterns

2. VOLUME FORECAST
   - Expected crime count (range)
   - Comparison to historical average
   - Confidence interval

3. TYPE-SPECIFIC FORECASTS
   For each crime type:
   - Expected trend
   - Volume prediction
   - Key drivers

4. HOTSPOT PREDICTIONS
   - Areas likely to see increases
   - Areas likely to see decreases
   - Emerging hotspots

5. TEMPORAL PREDICTIONS
   - High-risk days/times
   - Low-risk periods
   - Special dates to watch

6. RISK FACTORS
   - External factors that could affect forecast
   - Events to monitor
   - Uncertainty sources

7. RESOURCE RECOMMENDATIONS
   - Staffing suggestions
   - Patrol focus areas
   - Special operations timing

8. CONFIDENCE ASSESSMENT
   - Overall forecast confidence
   - Most reliable predictions
   - Highest uncertainty areas"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "forecast": response.text,
                    "area": area,
                    "forecast_days": forecast_days,
                    "data_points": len(historical_data)
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Trend forecasting failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def estimate_arrest_probability(
        self,
        case_id: str,
        case_details: str,
        evidence_strength: str,
        suspect_info: Optional[str] = None,
        time_since_crime_days: int = 0
    ) -> CRISToolResult:
        """Estimate the probability of making an arrest.
        
        Evaluates case factors to predict likelihood of successful
        arrest within various timeframes.
        
        Args:
            case_id: Case identifier
            case_details: Details of the case
            evidence_strength: Assessment of current evidence
            suspect_info: Information about suspects (if any)
            time_since_crime_days: Days since crime occurred
            
        Returns:
            Arrest probability estimates with recommendations.
        """
        self.logger.info(f"Estimating arrest probability for case {case_id}")
        
        prompt = f"""Estimate the probability of making an arrest in this case.

CASE ID: {case_id}
TIME SINCE CRIME: {time_since_crime_days} days

CASE DETAILS:
{case_details}

EVIDENCE STRENGTH:
{evidence_strength}

{f"SUSPECT INFORMATION: {suspect_info}" if suspect_info else "No suspects identified"}

Provide:

1. OVERALL ARREST PROBABILITY
   - Current probability (%)
   - Classification (HIGH/MEDIUM/LOW)
   - Key factors affecting probability

2. TIME-BASED PROBABILITIES
   - Within 48 hours: %
   - Within 1 week: %
   - Within 1 month: %
   - Within 6 months: %
   - Case going cold probability: %

3. SOLVABILITY FACTORS
   Present factors:
   - Witness availability
   - Physical evidence quality
   - Suspect identification status
   - Forensic evidence
   - Video/digital evidence
   - MO matches to known offenders

4. PROBABILITY BOOSTERS
   - Actions that could increase probability
   - Evidence to prioritize
   - Leads to pursue

5. RISK FACTORS
   - Factors decreasing probability
   - Time-sensitive concerns
   - Evidence degradation risks

6. RESOURCE RECOMMENDATIONS
   - Recommended investigation intensity
   - Specialist resources needed
   - Priority level

7. COMPARISON TO SIMILAR CASES
   - How does this compare to typical cases?
   - Unique advantages
   - Unique challenges

8. DECISION SUPPORT
   - Recommended resource allocation
   - Go/no-go recommendations
   - Escalation criteria"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "assessment": response.text,
                    "case_id": case_id,
                    "days_since_crime": time_since_crime_days
                },
                confidence=0.7
            )
        except Exception as e:
            self.logger.error(f"Arrest probability estimation failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def optimize_resource_allocation(
        self,
        predictions: List[Dict[str, Any]],
        available_resources: Dict[str, int],
        constraints: Optional[List[str]] = None
    ) -> CRISToolResult:
        """Optimize resource allocation based on predictions.
        
        Recommends how to deploy resources to maximize crime
        prevention and investigation effectiveness.
        
        Args:
            predictions: Crime predictions and risk assessments
            available_resources: Available personnel and equipment
            constraints: Operational constraints
            
        Returns:
            Optimized resource allocation plan.
        """
        self.logger.info("Optimizing resource allocation")
        
        predictions_text = "\n".join([
            f"- {p.get('area', 'Unknown')}: {p.get('crime_type', 'Unknown')} - "
            f"Risk: {p.get('risk_level', 'Unknown')}, Probability: {p.get('probability', 'Unknown')}"
            for p in predictions
        ])
        
        resources_text = "\n".join([f"- {k}: {v}" for k, v in available_resources.items()])
        constraints_text = "\n".join([f"- {c}" for c in (constraints or [])])
        
        prompt = f"""Optimize resource allocation based on these predictions and constraints.

CRIME PREDICTIONS:
{predictions_text}

AVAILABLE RESOURCES:
{resources_text}

{f"CONSTRAINTS:{chr(10)}{constraints_text}" if constraints_text else ""}

Provide:

1. PRIORITY RANKING
   - Rank areas/predictions by priority
   - Justification for ranking
   - Critical vs important vs routine

2. RESOURCE ALLOCATION PLAN
   For each resource type:
   - Recommended deployment
   - Location assignments
   - Timing recommendations

3. PATROL OPTIMIZATION
   - Recommended patrol routes
   - Timing of patrols
   - Coverage gaps to address

4. INVESTIGATION PRIORITIES
   - Cases to prioritize
   - Resource assignment per case
   - Expected outcomes

5. SURGE CAPACITY PLAN
   - When to deploy additional resources
   - Trigger criteria
   - Rapid response protocols

6. EFFICIENCY ANALYSIS
   - Expected coverage achieved
   - Risk reduction estimate
   - Cost-effectiveness assessment

7. CONTINGENCY PLANS
   - If predictions change
   - If resources become unavailable
   - Emergency reallocation procedures

8. MONITORING METRICS
   - KPIs to track
   - Adjustment triggers
   - Review schedule"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "allocation_plan": response.text,
                    "predictions_considered": len(predictions),
                    "resources_available": available_resources
                },
                confidence=0.75
            )
        except Exception as e:
            self.logger.error(f"Resource optimization failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
    
    async def simulate_behavior_patterns(
        self,
        subject_profile: str,
        simulation_parameters: Dict[str, Any],
        num_simulations: int = 100
    ) -> CRISToolResult:
        """Run behavioral simulations for a subject.
        
        Uses Monte Carlo-style thinking to explore possible
        behavioral outcomes and their probabilities.
        
        Args:
            subject_profile: Profile of the subject
            simulation_parameters: Parameters for simulation
            num_simulations: Conceptual number of scenarios to consider
            
        Returns:
            Simulation results with probability distributions.
        """
        self.logger.info(f"Running behavioral simulation")
        
        params_text = "\n".join([f"- {k}: {v}" for k, v in simulation_parameters.items()])
        
        prompt = f"""Simulate possible behavioral outcomes for this subject.

SUBJECT PROFILE:
{subject_profile}

SIMULATION PARAMETERS:
{params_text}

SIMULATION SCOPE: Consider {num_simulations} possible outcome scenarios

Provide:

1. OUTCOME DISTRIBUTION
   - Most likely outcomes (top 5)
   - Probability for each
   - Key differentiating factors

2. BEHAVIORAL TRAJECTORIES
   - Best case trajectory
   - Most likely trajectory
   - Worst case trajectory
   - Probability of each

3. CRITICAL DECISION POINTS
   - Points where outcomes diverge
   - Factors that determine path
   - Intervention opportunities

4. RISK DISTRIBUTION
   - Low risk outcomes: % probability
   - Medium risk outcomes: % probability
   - High risk outcomes: % probability
   - Critical risk outcomes: % probability

5. TEMPORAL ANALYSIS
   - Short-term (1 week) likely outcomes
   - Medium-term (1 month) likely outcomes
   - Long-term (6 months) likely outcomes

6. SENSITIVITY ANALYSIS
   - Which factors most affect outcomes?
   - Small changes with big impacts
   - Robust predictions vs sensitive ones

7. CONFIDENCE INTERVALS
   - 50% confidence range
   - 90% confidence range
   - Extreme outcomes to prepare for

8. ACTIONABLE INSIGHTS
   - How to shift distribution toward better outcomes
   - Early warning indicators
   - Monitoring recommendations"""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            
            return CRISToolResult(
                success=True,
                data={
                    "simulation_results": response.text,
                    "conceptual_simulations": num_simulations
                },
                confidence=0.65
            )
        except Exception as e:
            self.logger.error(f"Behavioral simulation failed: {e}")
            return CRISToolResult(success=False, data={}, message=str(e))
