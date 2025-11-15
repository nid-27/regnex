"""
Multi-Agent Backend System
This module handles the initialization and coordination of finance and CSV agents.
"""

import os
import glob
import pathlib
import pandas as pd
from dotenv import load_dotenv
from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.agent import Agent
from agno.models.google import Gemini

# Load environment variables from .env file
load_dotenv()


class AgentSystem:
    """Manages the multi-agent system for financial analysis"""
    
    def __init__(self, finance_data_dir="financeAgent/data", csv_data_dir="csvAgent/data"):
        # Check if API key is available
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please create a .env file with: GOOGLE_API_KEY=your-api-key-here"
            )
        
        self.finance_data_dir = pathlib.Path(finance_data_dir)
        self.csv_data_dir = pathlib.Path(csv_data_dir)
        
        # Create directories if they don't exist
        self.finance_data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.finance_kb = None
        self.csv_kb = None
        self.finance_agent = None
        self.csv_agent = None
        self.team_leader = None
        
    def initialize_knowledge_bases(self):
        """Initialize and load knowledge bases"""
        print("📚 Initializing Knowledge Bases...")
        
        # Initialize Finance Knowledge Base
        self.finance_kb = TextKnowledgeBase(
            name="finance_kb",
            description="Financial sentiment and document knowledge base",
        )
        print("✓ Finance Knowledge Base created")
        
        # Load finance documents with better encoding handling
        finance_files = glob.glob(os.path.join(self.finance_data_dir, "*.txt"))
        loaded_finance = 0
        print(f"📄 Found {len(finance_files)} text file(s) to load...")
        
        for file_path in finance_files:
            try:
                # Try multiple encodings
                content = None
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, "r", encoding=encoding) as file:
                            content = file.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content:
                    # TextKnowledgeBase uses load_documents method with file paths
                    self.finance_kb.load_documents([file_path])
                    loaded_finance += 1
                    print(f"  ✓ Loaded: {os.path.basename(file_path)}")
                else:
                    print(f"  ✗ Warning: Could not decode file {os.path.basename(file_path)}")
            except Exception as e:
                print(f"  ✗ Error loading {os.path.basename(file_path)}: {e}")
        
        print(f"✓ Finance Knowledge Base ready with {loaded_finance} document(s)\n")
        
        # Initialize CSV Knowledge Base
        self.csv_kb = CSVKnowledgeBase(
            name="csv_kb",
            description="Financial CSV knowledge base from CSV documents",
            path=str(self.csv_data_dir / "csv_kb")
        )
        print("✓ CSV Knowledge Base created")
        
        # Load CSV files - CSVKnowledgeBase loads them differently
        csv_files = glob.glob(os.path.join(self.csv_data_dir, "*.csv"))
        loaded_csv = 0
        print(f"📊 Found {len(csv_files)} CSV file(s) to load...")
        
        for file_path in csv_files:
            try:
                # CSVKnowledgeBase uses load_documents method
                self.csv_kb.load_documents([file_path])
                loaded_csv += 1
                print(f"  ✓ Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"  ✗ Error loading {os.path.basename(file_path)}: {e}")
        
        print(f"✓ CSV Knowledge Base ready with {loaded_csv} file(s)\n")
        
        return loaded_finance, loaded_csv
    
    def initialize_agents(self):
        """Initialize all agents"""
        print("🤖 Initializing Agents...")
        
        # Finance Agent
        self.finance_agent = Agent(
            name="Finance_Document_Expert",
            role="Financial Document Knowledge Base Specialist",
            model=Gemini(id="gemini-2.5-pro"),
            tools=[self.finance_kb] if self.finance_kb else [],
            instructions=[
                "Analyze financial documents thoroughly and provide detailed insights",
                "Reference specific sections of documents when making claims",
                "Provide context and explanations for financial terms and concepts",
                "Be precise with numbers, dates, and financial calculations",
                "When uncertain, clearly state what information is missing",
            ],
            markdown=True,
        )
        print("  ✓ Finance Document Expert Agent created")
        
        # CSV Agent
        self.csv_agent = Agent(
            name="CSV_Data_Analyst",
            role="Real-Time CSV Data Analyst",
            model=Gemini(id="gemini-2.5-pro"),
            tools=[self.csv_kb] if self.csv_kb else [],
            instructions=[
                "Analyze CSV data to extract relevant insights based on queries",
                "Provide statistical summaries and key findings",
                "Highlight trends and patterns in the data",
                "Be specific with numbers and percentages",
                "Mention data quality limitations if present"
            ],
            markdown=True,
        )
        print("  ✓ CSV Data Analyst Agent created")
        
        # Team Leader Agent
        self.team_leader = Agent(
            name="Team_Leader",
            role="Multi-Agent Coordinator and Team Leader",
            model=Gemini(id="gemini-2.5-pro"),
            team=[self.finance_agent, self.csv_agent],
            instructions=[
                "Understand the user's query and determine what information is needed",
                "Coordinate with both Finance and CSV agents to gather insights",
                "Synthesize responses from multiple agents into a coherent answer",
                "Highlight synergies and contradictions between document knowledge and real data",
                "Provide a balanced perspective that combines both sources",
                "Clearly structure the final response with sections and proper formatting",
                "If agents provide conflicting information, present both views with context"
            ],
            tools=[self.finance_agent, self.csv_agent],
            markdown=True,
        )
        print("  ✓ Team Leader Agent created")
        print("✓ All agents initialized successfully!\n")
    
    def setup(self):
        """Complete setup of the agent system"""
        try:
            print("=" * 60)
            print("🚀 MULTI-AGENT SYSTEM INITIALIZATION")
            print("=" * 60 + "\n")
            
            finance_count, csv_count = self.initialize_knowledge_bases()
            self.initialize_agents()
            
            print("=" * 60)
            print("✅ SYSTEM READY!")
            print("=" * 60)
            summary = f"""
📊 Summary:
   • Finance Documents Loaded: {finance_count}
   • CSV Files Loaded: {csv_count}
   • Total Agents: 3 (Finance Expert + CSV Analyst + Team Leader)

💡 You can now start asking questions!
"""
            print(summary)
            return True, summary.strip()
        except Exception as e:
            error_msg = f"✗ Error during setup: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def process_query(self, query: str):
        """Process a user query through the agent system"""
        if not self.team_leader:
            return "Error: Agent system not initialized. Please run setup first."
        
        try:
            result = self.team_leader.run(query)
            return result.content
        except Exception as e:
            return f"Error processing query: {str(e)}"


# Global instance
_agent_system = None


def get_agent_system():
    """Get or create the global agent system instance"""
    global _agent_system
    if _agent_system is None:
        _agent_system = AgentSystem()
    return _agent_system


def initialize_system(finance_dir="financeAgent/data", csv_dir="csvAgent/data"):
    """Initialize the agent system"""
    global _agent_system
    _agent_system = AgentSystem(finance_dir, csv_dir)
    return _agent_system.setup()


def ask_agents(query: str):
    """Process a query through the agent system"""
    system = get_agent_system()
    return system.process_query(query)