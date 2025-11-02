# regnex
An intelligent nexus for automating and orchestrating daily regulatory reporting operations A sophisticated multi-agent system built with **Agno** framework and **Ai** models that combines financial sentiment analysis with stock market data analysis.

## Features

- **Financial Document Expert Agent**: Analyzes financial sentiment from news and documents
- **CSV Data Agent**: Processes stock price and volume data from CSV files
- **Team Leader Agent**: Orchestrates and synthesizes responses from both agents
- **Coordinated Intelligence**: Combines sentiment analysis with market data insights

## Quick Start

### Prerequisites
- Python 3.12+ installed
- AI API key (get it from [https://aistudio.google.com/](https://aistudio.google.com/))

### Step-by-Step Setup

1. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment**
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```

3. **Install Dependencies from requirements.txt**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install:
   - agno (Agentic AI framework)
   - pandas, numpy (data processing)
   - google-genai (Gemini models)
   - lancedb (vector database)
   - ipykernel (Jupyter integration)

4. **Verify Installation**
   ```bash
   python -c "import agno; import google.genai; print('✓ All packages installed successfully!')"
   ```

5. **Register Jupyter Kernel (Optional)**
   ```bash
   python -m ipykernel install --user --name=venv --display-name="Python (venv)"
   ```

6. **Set AI API Key**
   
   **Option A - Environment Variable (Recommended):**
   ```bash
   export GOOGLE_API_KEY='your-api-key-here'
   ```
   
   **Option B - In the Notebook:**
   ```python
   os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'
   ```

7. **Open the Notebook**
   - Open `Agents.ipynb` in Jupyter, VS Code, or Google Colab
   - Select the Python kernel with your venv
   - Run all cells sequentially

8. **Load Your Data**
   
   The notebook will automatically load:
   - Financial sentiment data from `financeAgent/data/`
   - Stock market CSV files from `csvAgent/data/`

9. **Start Asking Questions**
   ```python
   # Query the multi-agent system
   response = ask_team_sync("Analyze the sentiment trends and their impact on stock prices")
   print(response)
   ```

### Quick Reference Commands

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt

# Verify installation
python -c "import agno; print('Success!')"

# Deactivate venv when done
deactivate
```

## System Architecture

```
User Query
    ↓
Team Leader Agent (Gemini 2.0 Flash)
    ↓
    ├──→ Financial Document Expert Agent (Gemini 2.0 Flash)
    └──→ CSV Data Agent (Gemini 2.0 Flash)
    ↓
Final Integrated Response
```

## Configuration

### Agents Configuration

- **Finance Agent**: Gemini 2.0 Flash for sentiment analysis
- **CSV Agent**: Gemini 2.0 Flash with CSV analysis tools
- **Team Leader**: Gemini 2.0 Flash for response synthesis

### Data Sources

1. **Financial Documents**: Stored in `financeAgent/data/` for sentiment analysis
2. **CSV Data**: Stock market data stored in `csvAgent/data/`

## Project Structure

```
MultiAgentChatBot/
├── Agents.ipynb              # Main notebook
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── .gitignore                # Git ignore rules
├── financeAgent/
│   └── data/                 # Financial sentiment data
├── csvAgent/
│   └── data/                 # Stock market CSV files
└── venv/                     # Virtual environment (gitignored)
```

## Example Queries

```python
# Basic financial sentiment analysis
"What sentiment does the financial news suggest?"

# Stock data analysis
"Analyze the recent trends in stock prices and volume"

# Combined insight
"Correlate financial news sentiment with stock price movements"
```

## 🛠️ Advanced Usage

### Async Queries
```python
import asyncio

async def main():
    response = await ask_team("Your query here")
    print(response)

asyncio.run(main())
```

### Custom CSV Analysis
```python
# The CSV Agent automatically analyzes:
# - Dataset statistics
# - Numeric summaries
# - Date/time trends
# - Column information
```

## Dependencies

- **agno**: Agentic AI framework
- **google-genai**: Gemini models
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **lancedb**: Vector database (for knowledge base)

## API Key Setup

You can set your AI API key in three ways:

1. **Environment Variable** (recommended):
   ```bash
   export GOOGLE_API_KEY='your-key-here'
   ```

2. **In the Notebook**:
   ```python
   os.environ['GOOGLE_API_KEY'] = 'your-key-here'
   ```

3. **In Cell 3**:
   Edit the `GOOGLE_API_KEY` variable directly

## Agent Collaboration

Each agent specializes in different aspects:

- **Finance Agent**: Provides sentiment analysis from financial news
- **CSV Agent**: Offers data-driven insights from market data
- **Team Leader**: Synthesizes both perspectives into actionable insights

## Use Cases

- Financial sentiment analysis
- Market trend correlation
- Investment research
- Risk assessment based on sentiment
- Portfolio optimization with sentiment indicators

## Next Steps

1. Set your `GOOGLE_API_KEY` in the notebook
2. Run the data loading cell
3. Customize agent instructions for your specific needs
4. Start querying the system!

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions:
- Check the Agno documentation: https://github.com/agno-agi/agno
- Review agent responses for error messages
- Ensure all dependencies are installed correctly

---

Built with ❤️ using Agno Framework and AI
