# import anthropic

# client = anthropic.Anthropic(
#     # defaults to os.environ.get("ANTHROPIC_API_KEY")
#     api_key="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",
# )
# message = client.messages.create(
#     model="claude-opus-4-20250514",
#     max_tokens=1024,
#     messages=[{"role": "user", "content": "Hello, Claude"}],
# )
# print(message.content)


from smolagents import (
    LiteLLMModel,
    CodeAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    Tool,
    tool,
)
from pathlib import Path
import yfinance as yf


client = LiteLLMModel(
    model="claude-sonnet-4-20250514",
    api_base="https://api.anthropic.com",
    api_key="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",
)
technical_analysis_tool = Tool.from_space(
    "http://127.0.0.1:7860",
    name="stock_analyzer",
    api_name="/get_technical_analysis",
    description="Get technical analysis for the given symbol for the given period. Country and exchange details are required",
)
stock_comparison_tool = Tool.from_space(
    "http://127.0.0.1:7860",
    name="compare_stocks_and_generate_report",
    api_name="/get_comparison_report",
    description="Compare the provided stocks and generate html report",
)


@tool
def save_report_tool(stream: str) -> str:
    """
    This tool can be used to save the html report on to local machine.
    Returns the local file name.

    Args:
        stream: Html content in string format
    """
    # Set the file name (saved in the same folder as the script)
    file_name = "stock_comparison_report.html"
    file_path = Path.cwd() / file_name

    # Write to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(stream)

    return file_path.resolve()


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
        save_report_tool,
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
agent.run(
    "Use connected mcp server and tools for technical analysis, additionally generate comparison report if asked and save the html reprot to local machine. Use the symbol lookup tool for retrieving symbols",
    additional_args={"user_prompt": "compare apple and microsoft stocks"},
)
