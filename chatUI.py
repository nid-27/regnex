"""
Multi-Agent Financial Analysis System - Gradio UI
This module provides a web interface for interacting with the multi-agent system.
"""

import gradio as gr
from agentProcess import initialize_system, ask_agents, get_agent_system
import os
import time
import threading


# Custom CSS for better UI
custom_css = """
.container {
    max-width: 1200px;
    margin: auto;
}
.header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}
.status-box {
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
.success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}
.error {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}
"""


def setup_system(finance_path, csv_path):
    """Initialize the agent system with provided paths"""
    if not finance_path:
        finance_path = "financeAgent/data"
    if not csv_path:
        csv_path = "csvAgent/data"
    
    success, message = initialize_system(finance_path, csv_path)
    
    if success:
        return f"✅ {message}", gr.update(interactive=True)
    else:
        return f"❌ {message}", gr.update(interactive=False)


def process_query(query, history):
    """Process user query and return response with animated loading"""
    if not query.strip():
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": "Please enter a valid query."})
        return history
    
    # Add user message
    history.append({"role": "user", "content": query})
    
    # Add loading message
    history.append({"role": "assistant", "content": "Processing."})
    yield history
    
    # Animate dots
    for i in range(1, 8):
        dots = "." * ((i % 3) + 1)
        history[-1]["content"] = f"Processing{dots}"
        yield history
        time.sleep(0.3)
    
    # Get response from agents
    try:
        response = ask_agents(query)
        history[-1]["content"] = response
    except Exception as e:
        history[-1]["content"] = f"Error: {str(e)}"
    
    yield history


def clear_chat():
    """Clear chat history"""
    return []


# Create Gradio Interface
with gr.Blocks(css=custom_css, title="Multi-Agent Financial Analysis") as demo:
    
    # Header
    gr.HTML("""
        <div class="header">
            <h1>🤖 Multi-Agent Financial Analysis System</h1>
            <p>Powered by Finance Document Expert & CSV Data Analyst</p>
        </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            # Setup Section
            gr.Markdown("### 🔧 System Setup")
            
            finance_dir = gr.Textbox(
                label="Finance Data Directory",
                value="financeAgent/data",
                placeholder="Path to finance text files",
                info="Directory containing .txt files with financial documents"
            )
            
            csv_dir = gr.Textbox(
                label="CSV Data Directory",
                value="csvAgent/data",
                placeholder="Path to CSV files",
                info="Directory containing .csv files with financial data"
            )
            
            setup_btn = gr.Button("🚀 Initialize System", variant="primary")
            status_output = gr.Textbox(
                label="System Status",
                interactive=False,
                lines=3
            )
            
            # Info Section
            gr.Markdown("""
            ### 📋 How to Use
            1. **Setup**: Click 'Initialize System' to load data
            2. **Query**: Ask questions about financial documents or CSV data
            3. **Analysis**: The team leader coordinates responses from specialized agents
            
            ### 💡 Example Queries
            - "What are the key principles of financial risk management?"
            - "Analyze the revenue trends in the CSV data"
            - "Compare document insights with actual data patterns"
            - "For 2005-03-11 data, can you tell if agreed, neutral or negative"
            """)
        
        with gr.Column(scale=2):
            # Chat Interface
            gr.Markdown("### 💬 Chat with Agents")
            
            chatbot = gr.Chatbot(
                height=500,
                show_label=False,
                show_copy_button=True,
                type="messages"
            )
            
            with gr.Row():
                query_input = gr.Textbox(
                    label="Your Query",
                    placeholder="Ask about financial documents or data analysis...",
                    scale=4,
                    interactive=False
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Chat", size="sm")
                
            gr.Markdown("""
            <div style="text-align: center; margin-top: 20px; color: #666;">
                <small>The agents will analyze your query and provide insights from both documents and CSV data.</small>
            </div>
            """)
    
    # Event Handlers
    setup_btn.click(
        fn=setup_system,
        inputs=[finance_dir, csv_dir],
        outputs=[status_output, query_input]
    )
    
    submit_btn.click(
        fn=process_query,
        inputs=[query_input, chatbot],
        outputs=[chatbot]
    ).then(
        fn=lambda: "",
        outputs=[query_input]
    )
    
    query_input.submit(
        fn=process_query,
        inputs=[query_input, chatbot],
        outputs=[chatbot]
    ).then(
        fn=lambda: "",
        outputs=[query_input]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot]
    )


if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Financial Analysis System...")
    print("📊 Make sure your data directories are properly set up:")
    print("   - financeAgent/data/ for .txt files")
    print("   - csvAgent/data/ for .csv files")
    print("\n🌐 Launching Gradio interface...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )