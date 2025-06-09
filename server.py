import gradio as gr
from tradingview_ta import TA_Handler
from config import SCREENER, interval_options
import quantstats as qs
from io import BytesIO
from PIL import Image

qs.extend_pandas()


def get_technical_analysis(
    symbol: str, exchange: str, screener: str, interval: str
) -> dict[str:any]:
    """Get the technical analysis for the given symbol.

    Args:
        symbol(str):  Ticker symbol which is to be analyzed (e.g., "AAPL","MSFT","VOD").
        exchange(str): Exchange at which the tikcer is traded (e.g., "NASDAQ", "NSE", "LSE").
        screener(str): The exchange's country as the screener (e.g., "america", "india", "uk").The possible values are listed in the config.py file
        interval(str): The time interval for the analysis (e.g., "1d", "1h", "15m").The possible values are listed in the config.py file

    Returns:
       dict: Technical analysis for the symbol/ticker for the given period. Returns a dict containing the analysis.
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


def get_comparison_report(symbol: str, benchmark: str):
    """Get the symbol performance against provided benchmark and return plots and HTML report content.

    Args:
    symbol (str): Ticker symbol to be analyzed (e.g., "AAPL", "TSLA").
    benchmark (str): Benchmark symbol (e.g., "^DJI", "SPY").
    """

    data = qs.utils.download_returns(symbol)

    # Snapshot plot to in-memory image
    snapshot_buf = BytesIO()
    qs.plots.snapshot(data, title="Performance", savefig=snapshot_buf)
    snapshot_buf.seek(0)
    snapshot_img = Image.open(snapshot_buf)

    # Yearly returns plot to in-memory image
    returns_buf = BytesIO()
    qs.plots.yearly_returns(data, benchmark=benchmark, savefig=returns_buf)
    returns_buf.seek(0)
    returns_img = Image.open(returns_buf)

    # Generate and read HTML report
    report_path = "performance_report.html"
    qs.reports.html(
        data,
        benchmark=benchmark,
        output=report_path,
        strategy_title=symbol,
        title="Detailed Comparison",
    )
    with open(report_path, "r", encoding="utf-8") as file:
        report_content = file.read()

    return snapshot_img, returns_img, report_content, report_path


def gradio_interface(symbol: str, benchmark: str):
    """Gradio interface function to generate and display the report and plots."""
    snapshot_img, returns_img, report_content, report_path = get_comparison_report(
        symbol, benchmark
    )
    return snapshot_img, report_content, report_path, returns_img


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

    with gr.Tab("Performance Comparison"):
        with gr.Blocks() as interface:
            gr.Markdown("# Stock Performance Analyzer")
            gr.Markdown(
                "Enter a stock symbol and a benchmark to generate a performance report and snapshot."
            )

            with gr.Row():
                with gr.Column():
                    symbol_input = gr.Textbox(
                        label="Stock Symbol (e.g., TSLA,MSFT,AAPL)",
                        placeholder="Enter stock symbol",
                        info="Some symbols may require a dot(.)suffix of corresponding exchange as TCS.NS",
                    )
                    benchmark_input = gr.Textbox(
                        label="Benchmark Symbol (e.g., ^DJI,^NSEI,^UKX,SPY)",
                        placeholder="Enter benchmark symbol",
                        info="For index use (^) as that is the accepted format. It can also be other valid stocks/symbols too.",
                    )

                    generate_button = gr.Button("Generate Report", variant="primary")
                    returns_output = gr.Image(label="Yearly Returns")

                with gr.Column():
                    download_button = gr.File(label="Download Report")
                    snapshot_output = gr.Image(label="Performance Snapshot")

            with gr.Row():
                report_output = gr.HTML(label="Performance Report")

            def generate_report(symbol, benchmark):
                snapshot_img, report_html, report_path, returns_img = gradio_interface(
                    symbol, benchmark
                )
                return snapshot_img, report_html, report_path, returns_img

            generate_button.click(
                generate_report,
                inputs=[symbol_input, benchmark_input],
                outputs=[
                    snapshot_output,
                    report_output,
                    download_button,
                    returns_output,
                ],
            )


demo.launch(mcp_server=True)
