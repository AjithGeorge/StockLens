import gradio as gr
from pathlib import Path
import yfinance as yf
import os
from dotenv import load_dotenv
from smolagents import (
    LiteLLMModel,
    CodeAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    Tool,
    tool,
)

# Load environment variables
load_dotenv()

client = LiteLLMModel(
    model="claude-sonnet-4-20250514",
    api_base="https://api.anthropic.com",
    api_key=os.getenv("ANTHROPIC_KEY"),
)
technical_analysis_tool = Tool.from_space(
    "Agents-MCP-Hackathon/stock-lens",
    name="stock_analyzer",
    api_name="/get_technical_analysis",
    description="Get technical analysis for the given symbol for the given period. Country and exchange details are required",
)
stock_comparison_tool = Tool.from_space(
    "Agents-MCP-Hackathon/stock-lens",
    name="compare_stocks_and_generate_report",
    api_name="/get_comparison_report",
    description="Compare the provided stocks and generate html report",
)


@tool
def symbol_lookup(query: str, type: str) -> list[str]:
    """
    This tool can be used to find the exact symbols to be used in stock comparison tool.
    Returns data frame with the symbol details

    Args:
        query(str): Company/Index search term
        type(str): accepts "stock"/"index" as values
    """

    if type == "index":
        results = yf.Lookup(query).get_index(count=10)
        return results.index.tolist()
    else:
        results = yf.Lookup(query).get_stock(count=10)
        return results.index.tolist()


agent = CodeAgent(
    tools=[
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        technical_analysis_tool,
        stock_comparison_tool,
        symbol_lookup,
    ],
    model=client,
    additional_authorized_imports=[
        "yfinance",
        "pandas",
        "numpy",
        "requests",
        "pandas_ta",
        "matplotlib",
        "os",
    ],
)


def infer(prompt):
    """
    Process the user prompt and return HTML content from stock comparison tool
    """
    try:
        response = agent.run(
            prompt,
            additional_args={
                "steps": """Follow these steps:
                1. Use symbol_lookup tool to get correct symbols
                2. Use stock_comparison_tool with the symbols
                3. Return the HTML content from stock_comparison_tool
                4. Do not modify or summarize the response"""
            },
        )

        # If response is a tuple, extract just the HTML content
        if isinstance(response, tuple) and len(response) == 2:
            html_content, _ = response
            return html_content

        # If response is HTML string
        elif isinstance(response, str):
            if "<!DOCTYPE html>" in response or "<html>" in response:
                return response
            else:
                return (
                    f"<p style='color: red'>Unexpected response format: {response}</p>"
                )

        else:
            return "<p style='color: red'>Invalid response format</p>"

    except Exception as e:
        return f"<p style='color: red'>Error processing request: {str(e)}</p>"


# Update the Gradio interface
with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown(
            f"""# Stock Performance Comparison Agent
            Using mcp tools from [[stock-lens]](https://huggingface.co/spaces/a-ge/stock-lens)]
        """
        )

        with gr.Row():
            prompt = gr.Text(
                label="Prompt",
                show_label=False,
                max_lines=5,
                placeholder="Enter your prompt for stock comparison (e.g., 'Compare Apple and Microsoft stocks')",
                container=False,
            )
            run_button = gr.Button("Generate Report", scale=0, variant="primary")

        examples = [
            "Compare Apple and Microsoft stocks",
            "Compare Tesla and Ford performance",
            "Analyze Google and Amazon stocks",
            "Analyze Google stock against ^DJI index",
        ]
        with gr.Row():
            gr.Examples(
                examples=examples,
                inputs=[prompt],
            )

        with gr.Row():
            # Simplified output - just the HTML report
            html = gr.HTML(
                label="Performance Report",
                value="<div>Waiting...</div>",
                container=True,
            )

        # Add event handlers
        run_button.click(
            fn=infer,
            inputs=[prompt],
            outputs=html,
        )
        prompt.submit(
            fn=infer,
            inputs=[prompt],
            outputs=html,
        )

demo.launch()
