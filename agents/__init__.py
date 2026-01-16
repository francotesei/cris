"""CRIS Agents Module - Powered by Gemini 3 + ADK + A2A.

This module contains all the AI agents that power CRIS's
intelligence capabilities. All agents are built on Google's
Agent Development Kit (ADK) and communicate via the A2A protocol.

Architecture:
- OrchestratorAgent: Central coordinator using ADK delegation
- Specialized Agents: Each implements CRISADKAgent with specific tools
- A2A Protocol: Inter-agent communication and task routing
"""

from agents.orchestrator import OrchestratorAgent, create_orchestrator
from agents.link_agent import LinkAgent
from agents.profiler_agent import ProfilerAgent
from agents.geo_intel_agent import GeoIntelAgent
from agents.witness_agent import WitnessAgent
from agents.predictor_agent import PredictorAgent
from agents.osint_agent import OSINTAgent

__all__ = [
    # Main orchestrator
    "OrchestratorAgent",
    "create_orchestrator",
    # Specialized agents
    "LinkAgent",
    "ProfilerAgent",
    "GeoIntelAgent",
    "WitnessAgent",
    "PredictorAgent",
    "OSINTAgent",
]


def create_cris_system():
    """Factory function to create a fully configured CRIS multi-agent system.
    
    Returns:
        OrchestratorAgent with all specialized agents registered.
    """
    # Initialize specialized agents
    link_agent = LinkAgent()
    profiler_agent = ProfilerAgent()
    geo_intel_agent = GeoIntelAgent()
    witness_agent = WitnessAgent()
    predictor_agent = PredictorAgent()
    osint_agent = OSINTAgent()
    
    # Create orchestrator with all agents
    orchestrator = create_orchestrator(
        sub_agents=[
            link_agent,
            profiler_agent,
            geo_intel_agent,
            witness_agent,
            predictor_agent,
            osint_agent,
        ]
    )
    
    return orchestrator
