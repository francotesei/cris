"""CRIS - Criminal Reasoning Intelligence System.

Main CLI entry point for running tasks from the terminal.
"""

import sys

def main():
    print("CRIS - Criminal Reasoning Intelligence System")
    print("-" * 45)
    print("Available commands:")
    print("  streamlit run app.py     - Start the web dashboard")
    print("  python -m database.init_schema - Initialize database")
    print("-" * 45)

if __name__ == "__main__":
    main()
