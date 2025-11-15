"""
Multi-Agent Backend System
This module handles the initialization and coordination of finance and CSV agents.
"""

import os
import glob
import pathlib
import re
import json
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

    def __init__(
        self, finance_data_dir="financeAgent/data", csv_data_dir="csvAgent/data"
    ):
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

        # Config
        self.TOP_K_TEXT = 6
        self.CSV_TOP_K = 100

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
                for encoding in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
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
                    print(
                        f"  ✗ Warning: Could not decode file {os.path.basename(file_path)}"
                    )
            except Exception as e:
                print(f"  ✗ Error loading {os.path.basename(file_path)}: {e}")

        print(f"✓ Finance Knowledge Base ready with {loaded_finance} document(s)\n")

        # Initialize CSV Knowledge Base
        self.csv_kb = CSVKnowledgeBase(
            name="csv_kb",
            description="Financial CSV knowledge base from CSV documents",
            path=str(self.csv_data_dir / "csv_kb"),
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
            model=Gemini(id="gemini-2.5-flash"),
            knowledge=self.finance_kb,
            add_context=True,
            instructions=[
                "STRICT RAG MODE: You MUST only answer using the provided documents passed in the context.",
                "Do not use any world knowledge beyond the content explicitly provided to you.",
                "If the information is not present in the provided context, reply exactly: 'Not enough information in the provided documents.'",
                "When you use a fact from a document, include a short citation line like: [source: <filename>]",
            ],
            markdown=True,
            show_tool_calls=True,
        )
        print("  ✓ Finance Document Expert Agent created")

        # CSV Agent
        self.csv_agent = Agent(
            name="CSV_Data_Analyst",
            role="CSV Financial Data Analyst",
            model=Gemini(id="gemini-2.5-flash"),
            knowledge=self.csv_kb,
            add_context=True,
            instructions=[
                "STRICT RAG MODE: Use ONLY the CSV rows / columns provided in the context.",
                "If a requested date/column/value is missing, reply: 'Data not available in files.'",
                "When summarizing numbers, include the source CSV filename and row indices if possible.",
            ],
            markdown=True,
            show_tool_calls=True,
        )
        print("  ✓ CSV Data Analyst Agent created")

        # Team Leader Agent
        self.team_leader = Agent(
            name="Team_Leader",
            role="Multi-Agent Coordinator and Team Leader",
            model=Gemini(id="gemini-2.5-flash"),
            team=[self.finance_agent, self.csv_agent],
            instructions=[
                "You are the Team Leader. Your role is to decompose complex queries into specialized sub-queries.",
                "STEP 1 - ANALYZE: Break down the user query into components that require different expertise.",
                "STEP 2 - DECOMPOSE: Create specialized sub-queries for each agent.",
                "STEP 3 - DELEGATE: Send tailored sub-queries to each agent.",
                "STEP 4 - COLLATE: Combine responses from both agents to answer the original query.",
            ],
            markdown=True,
            show_tool_calls=True,
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

    def retrieve_finance_docs(self, query: str):
        """Retrieve relevant finance documents"""
        try:
            return self.finance_kb.search(query, top_k=self.TOP_K_TEXT)
        except:
            try:
                return self.finance_kb.search(query)
            except:
                return []

    def retrieve_csv_rows(self, query: str):
        """Retrieve relevant CSV rows based on query"""
        matches = {}
        date_like = None
        m = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", query)
        if m:
            date_like = m.group(1)

        for csv_file in glob.glob(os.path.join(self.csv_data_dir, "*.csv")):
            try:
                df = pd.read_csv(csv_file)
            except:
                df = pd.read_csv(csv_file, engine="python", on_bad_lines="skip")

            matched = pd.DataFrame()
            if date_like:
                for col in df.columns:
                    try:
                        parsed = pd.to_datetime(df[col], errors="coerce")
                        mask = parsed.astype(str).str.contains(date_like)
                        if mask.any():
                            matched = df[mask]
                            break
                    except:
                        pass
            else:
                kw = query.lower()
                masks = []
                for col in df.columns:
                    if df[col].dtype == object:
                        masks.append(df[col].str.lower().str.contains(kw, na=False))
                if masks:
                    combined = masks[0]
                    for m in masks[1:]:
                        combined = combined | m
                    matched = df[combined]

            if not matched.empty:
                matches[os.path.basename(csv_file)] = matched.head(self.CSV_TOP_K)

        return matches

    def build_finance_context(self, docs):
        """Build context string from finance documents"""
        parts = []
        for i, d in enumerate(docs):
            txt = getattr(d, "text", "")
            src = (
                d.metadata.get("source", f"doc_{i}")
                if hasattr(d, "metadata")
                else f"doc_{i}"
            )
            snippet = txt[:800].replace("\n", " ")
            parts.append(f"[source: {src}] {snippet}")
        return "\n\n".join(parts)

    def build_csv_context(self, matches):
        """Build context string from CSV data"""
        parts = []
        for fname, df in matches.items():
            preview = df.head(10).to_csv(index=False)
            parts.append(
                f"[CSV: {fname}]\nColumns: {', '.join(df.columns)}\nPreview:\n{preview}"
            )
        return "\n\n".join(parts)

    def decompose_query(self, query: str):
        """Decompose query into sub-queries for each agent"""
        decompose_prompt = f"""Analyze this query and decompose it into two specific sub-queries:
        
Original Query: {query}

Provide EXACTLY in this format:
CSV_SUBQUERY: [specific query for CSV data - focus on dates, prices, volumes, metrics]
FINANCE_SUBQUERY: [specific query for finance documents - focus on sentiment, analysis, concepts]
"""

        try:
            decompose_res = self.team_leader.run(decompose_prompt)
            decompose_txt = getattr(decompose_res, "content", str(decompose_res))

            csv_subquery = ""
            finance_subquery = ""

            for line in decompose_txt.split("\n"):
                if line.startswith("CSV_SUBQUERY:"):
                    csv_subquery = line.replace("CSV_SUBQUERY:", "").strip()
                elif line.startswith("FINANCE_SUBQUERY:"):
                    finance_subquery = line.replace("FINANCE_SUBQUERY:", "").strip()

            return csv_subquery, finance_subquery
        except Exception as e:
            print(f"Error decomposing query: {e}")
            return query, query

    def process_query(self, query: str):
        """Process a user query through the agent system with decomposition and collation"""
        if not self.team_leader:
            return {
                "error": "Error: Agent system not initialized. Please run setup first."
            }

        try:
            # STEP 1: Decompose query into sub-queries
            csv_subquery, finance_subquery = self.decompose_query(query)

            # STEP 2: Retrieve relevant data
            finance_hits = self.retrieve_finance_docs(
                finance_subquery if finance_subquery else query
            )
            csv_hits = self.retrieve_csv_rows(csv_subquery if csv_subquery else query)

            if not finance_hits and not csv_hits:
                return {"error": "No information found in knowledge bases."}

            finance_context = self.build_finance_context(finance_hits)
            csv_context = self.build_csv_context(csv_hits)

            # STEP 3: Send tailored queries to each agent
            finance_prompt = (
                "Use ONLY the context provided.\n\nCONTEXT:\n"
                + finance_context
                + "\n\nQUERY:\n"
                + (finance_subquery if finance_subquery else query)
            )
            csv_prompt = (
                "Use ONLY the context provided.\n\nCONTEXT:\n"
                + csv_context
                + "\n\nQUERY:\n"
                + (csv_subquery if csv_subquery else query)
            )

            f_res = self.finance_agent.run(finance_prompt, context=finance_context)
            c_res = self.csv_agent.run(csv_prompt, context=csv_context)

            f_txt = getattr(f_res, "content", str(f_res))
            c_txt = getattr(c_res, "content", str(c_res))

            # STEP 4: Team Leader collates responses
            collate_prompt = f"""You are the Team Leader. Collate the responses from both agents to answer the original query.

Original Query: {query}

CSV Agent Response:
{c_txt}

Finance Agent Response:
{f_txt}

Now synthesize these into a complete, coherent answer that combines both data and sentiment/analysis insights."""

            l_res = self.team_leader.run(collate_prompt)
            l_txt = getattr(l_res, "content", str(l_res))

            return {
                "query": query,
                "csv_subquery": csv_subquery,
                "finance_subquery": finance_subquery,
                "csv_agent_response": c_txt,
                "finance_agent_response": f_txt,
                "team_leader_final_answer": l_txt,
            }

        except Exception as e:
            return {"error": f"Error processing query: {str(e)}"}


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
