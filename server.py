import gradio as gr
from tradingview_ta import TA_Handler
from config import SCREENER, interval_options


def get_technical_analysis(
    symbol: str, exchange: str, screener: str, interval: str
) -> dict[str:any]:
    """Get the technical analysis for the given symbol.

    Args:
        symbol(str):  Ticker symbol which is to be analyzed (e.g., "AAPL", "TLKM", "USDEUR", "BTCUSDT").
        exchange(str): Exchange at which the tikcer is traded (e.g., "nasdaq", "idx", Exchange.FOREX, "binance").
        screener(str): The exchange's country as the screener (e.g., "america", "india", "uk").The possible values are listed in the config.py file
        interval(str): The time interval for the analysis (e.g., "1d", "1h", "15m").The possible values are listed in the config.py file

    Returns:
        Technical analysis for the symbol/ticker for the given period. Returns a dict containing the different technical details.
    """
    try:
        screener = list(SCREENER.keys())[screener]
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=interval,
        )
        analysis = handler.get_analysis()
        analysis_dict = {
            "Symbol": analysis.symbol,
            "Exchange": analysis.exchange,
            "Screener": analysis.screener,
            "Interval": analysis.interval,
            "Time": analysis.time.strftime("%Y-%m-%d %H:%M:%S"),
            "Summary": analysis.summary,
            "Oscillators": analysis.oscillators,
            "Moving Averages": analysis.moving_averages,
            "Indicators": analysis.indicators,
        }
        return analysis_dict
    except Exception as e:
        return {"Error": str(e)}


def dummy_tool(name, value):
    return f"Hello, {name}! You selected value: {value}"


with gr.Blocks() as demo:
    gr.Markdown("# Stock Analyzer")
    gr.Markdown("Get Analyst ratings and technical indicator details")

    with gr.Tab("Technical Analysis"):
        symbol_input = gr.Textbox(
            label="Ticker/Symbol (e.g., AAPL,MSFT,GOOGL)",
        )
        exchange_input = gr.Textbox(label="Exchange (e.g., NASDAQ, NSE, LSE)")
        screener_input = gr.Dropdown(
            choices=SCREENER.values(),
            label="Screener (for stocks, enter the exchange's country as the screener)",
            type="index",
        )
        interval_input = gr.Dropdown(interval_options, label="Select Interval:")
        submit_button = gr.Button("Generate Analysis", variant="primary")
        output_json = gr.JSON(label="Output")

        submit_button.click(
            fn=get_technical_analysis,
            inputs=[symbol_input, exchange_input, screener_input, interval_input],
            outputs=output_json,
        )

    with gr.Tab("Placeholder Tool"):
        gr.Markdown("### This is a placeholder tool for future features")
        name_input = gr.Textbox(label="Enter your name")
        slider_input = gr.Slider(minimum=0, maximum=100, step=1, label="Select a value")
        dummy_button = gr.Button("Run Dummy Tool")
        dummy_output = gr.Textbox(label="Output")

        dummy_button.click(
            fn=dummy_tool,
            inputs=[name_input, slider_input],
            outputs=dummy_output,
        )

demo.launch(mcp_server=True)
