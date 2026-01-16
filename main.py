"""CRIS - Criminal Reasoning Intelligence System.

Main CLI entry point for running tasks from the terminal.
Powered by Gemini 3 + ADK + A2A.
"""

import asyncio
import sys
from typing import Optional

from config.settings import get_settings


def print_banner():
    """Print the CRIS banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██████╗██████╗ ██╗███████╗                                     ║
║  ██╔════╝██╔══██╗██║██╔════╝                                     ║
║  ██║     ██████╔╝██║███████╗                                     ║
║  ██║     ██╔══██╗██║╚════██║                                     ║
║  ╚██████╗██║  ██║██║███████║                                     ║
║   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝                                     ║
║                                                                   ║
║   Criminal Reasoning Intelligence System                          ║
║   Powered by Gemini 3 + ADK + A2A                                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help information."""
    print("""
CRIS Commands:
─────────────────────────────────────────────────────────────────────

  Web Dashboard:
    streamlit run app.py              Start the web interface

  Database:
    python -m database.init_schema    Initialize Neo4j schema

  Agent Testing:
    python main.py test-agents        Test all agents
    python main.py query "<query>"    Run a query through orchestrator

  A2A Server:
    python main.py serve              Start A2A server for remote agents

─────────────────────────────────────────────────────────────────────

Architecture:
  • Orchestrator Agent - Central coordinator (ADK)
  • Link Agent - Graph analysis & case connections
  • Profiler Agent - Behavioral profiling (FBI BAU style)
  • Geo-Intel Agent - Spatial pattern analysis
  • Witness Agent - Statement credibility analysis
  • Predictor Agent - Forecasting & risk assessment
  • OSINT Agent - Digital footprint analysis

All agents communicate via A2A (Agent-to-Agent) protocol.
─────────────────────────────────────────────────────────────────────
    """)


async def test_agents():
    """Test all agents are working correctly."""
    print("\n🧪 Testing CRIS Agents...\n")
    
    try:
        from agents import create_cris_system
        
        print("  ✓ Creating CRIS system...")
        orchestrator = create_cris_system()
        
        print("  ✓ Orchestrator initialized")
        print(f"    Model: {orchestrator.model}")
        print(f"    Registered agents: {list(orchestrator._sub_agents.keys())}")
        
        # Test health check
        print("\n  🔍 Running health checks...")
        healthy = await orchestrator.health_check()
        
        if healthy:
            print("  ✓ Orchestrator health check passed")
        else:
            print("  ✗ Orchestrator health check failed")
            print("    Check your GOOGLE_API_KEY environment variable")
        
        # List A2A registered agents
        from core.a2a_server import A2ARegistry
        registry = A2ARegistry()
        a2a_agents = registry.list_agents()
        
        print(f"\n  📡 A2A Registry: {len(a2a_agents)} agents registered")
        for card in a2a_agents:
            print(f"    • {card.name}: {len(card.skills)} skills")
        
        print("\n✅ Agent test complete!")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure all dependencies are installed: uv sync")
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def run_query(query: str, case_id: Optional[str] = None):
    """Run a query through the orchestrator."""
    print(f"\n🔍 Processing query: {query}\n")
    
    try:
        from agents import create_cris_system
        
        orchestrator = create_cris_system()
        
        print("  🤖 Orchestrator analyzing query...")
        result = await orchestrator.process_query(query, case_id=case_id)
        
        print("\n" + "═" * 70)
        print("📋 CRIS Response:")
        print("═" * 70 + "\n")
        print(result.get("response", "No response generated"))
        print("\n" + "═" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    print_banner()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help" or command == "--help" or command == "-h":
        print_help()
        
    elif command == "test-agents":
        asyncio.run(test_agents())
        
    elif command == "query":
        if len(sys.argv) < 3:
            print("❌ Please provide a query: python main.py query \"your query here\"")
            return
        query = sys.argv[2]
        case_id = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(run_query(query, case_id))
        
    elif command == "serve":
        print("\n🚀 Starting A2A Server...")
        print("   This feature requires additional setup.")
        print("   For now, use: streamlit run app.py")
        
    else:
        print(f"❌ Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
