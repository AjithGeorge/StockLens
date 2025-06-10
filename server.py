import gradio as gr
from tradingview_ta import TA_Handler
from config import SCREENER, interval_options
import quantstats as qs
from io import BytesIO
from PIL import Image

qs.extend_pandas()


def get_technical_analysis(
    symbol: str, exchange: str, country: str, interval: str
) -> dict[str:any]:
    """Get the technical analysis for the given symbol.

    Args:
        symbol(str):Required:  Ticker symbol which is to be analyzed (e.g., "AAPL","MSFT","VOD").
        exchange(str):Required: Exchange at which the tikcer is traded (e.g., "NASDAQ", "NSE", "LSE").
        country(str):Required: The exchange's country (e.g., "america", "india", "uk").The possible values are listed in the config.py file
        interval(str):Required: The time interval for the analysis (e.g., "1d", "1h", "15m").The possible values are listed in the config.py file

    Returns:
       dict: Technical analysis for the symbol/ticker for the given period. Returns a dict containing the analysis.
    """

    try:
        symbol = symbol.split(".")[0]
        country = list(SCREENER.keys())[country]
        if country == None or country == "None":
            raise ValueError("Country is required!")

        handler = TA_Handler(
            symbol=symbol,
            screener=country,
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


def get_performance_snapshot(symbol) -> Image:
    """Get the symbol performance snapshot and returns plot image.

    Args:
    data (Series:[float])

    Returns:
    Image of the performance snapshot is returned
    """
    _data = qs.utils.download_returns(symbol)

    snapshot_buf = BytesIO()
    qs.plots.snapshot(_data, title="Performance", savefig=snapshot_buf)
    snapshot_buf.seek(0)
    return Image.open(snapshot_buf)


def get_comparison_report(symbol: str, benchmark: str):
    """Get the symbol performance against provided benchmark and return plots and HTML report content.

    Args:
    symbol (str): Ticker symbol to be analyzed (e.g., "AAPL", "TSLA").
    benchmark (str): Benchmark symbol (e.g., "^DJI", "SPY").
    """

    data = qs.utils.download_returns(symbol)

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

    return report_content, report_path


with gr.Blocks() as demo:
    gr.Markdown("# Stock-lens🔎")
    gr.Markdown(
        "Get Analyst ratings and technical indicator details📈. Get Comparison of your favourite stocks 🏆"
    )

    with gr.Tab("Technical Analysis"):

        gr.Markdown("# Analyst Ratings and Technical Indicators")
        gr.Markdown(
            "Enter a stock symbol,exchange,country and interval to see the tecnical indicator details."
        )
        symbol_input = gr.Textbox(
            label="Ticker/Symbol* (e.g., AAPL,MSFT,GOOGL)",
        )
        exchange_input = gr.Textbox(label="Exchange* (e.g., NASDAQ, NSE, LSE)")
        country_input = gr.Dropdown(
            choices=SCREENER.values(),
            label="Country* (e.g.,United States,India)",
            type="index",
            value=None,
        )
        interval_input = gr.Dropdown(interval_options, label="Select Interval:")
        submit_button = gr.Button("Generate Analysis", variant="primary")
        output_json = gr.JSON(label="Output")

        submit_button.click(
            fn=get_technical_analysis,
            inputs=[symbol_input, exchange_input, country_input, interval_input],
            outputs=output_json,
        )

    with gr.Tab("Performance Comparison"):
        with gr.Blocks():
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
                        label="Benchmark Symbol (e.g., ^DJI,^NSEI,^FTSE,SPY)",
                        placeholder="Enter benchmark symbol",
                        info="For index use (^) as that is the accepted format. It can also be other valid stocks/symbols too.",
                    )

                    generate_button = gr.Button("Generate Report", variant="primary")

                    download_button = gr.File(label="Download Report")

            with gr.Row():
                report_output = gr.HTML(label="Performance Report")

            generate_button.click(
                fn=get_comparison_report,
                inputs=[symbol_input, benchmark_input],
                outputs=[
                    report_output,
                    download_button,
                ],
            )


demo.launch(mcp_server=True)
