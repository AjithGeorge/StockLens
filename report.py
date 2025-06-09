import quantstats as qs
import gradio as gr
import os

qs.extend_pandas()


def get_comparison_report(symbol: str, benchmark: str):
    """Get the symbol performance against provided benchmark and return paths to the report and plot.

    Args:
        symbol (str): Ticker symbol to be analyzed (e.g., "AAPL", "TSLA").
        benchmark (str): Benchmark symbol (e.g., "^DJI", "SPY").

    Returns:
        tuple: Paths to the generated HTML report and snapshot plot.
    """
    data = qs.utils.download_returns(symbol)

    # Generate and save the snapshot plot
    snapshot_path = "performance_snapshot.png"
    qs.plots.snapshot(data, title=" Performance", savefig=snapshot_path)

    returns_path = "returns.png"
    qs.plots.yearly_returns(data, benchmark=benchmark, savefig=returns_path)

    # Generate and save the HTML report
    report_path = "performance_report.html"
    qs.reports.html(
        data,
        benchmark=benchmark,
        output=report_path,
        strategy_title=symbol,
    )

    return snapshot_path, report_path, returns_path


def gradio_interface(symbol: str, benchmark: str):
    """Gradio interface function to generate and display the report and plot."""
    snapshot_path, report_path, returns_path = get_comparison_report(symbol, benchmark)

    # Read the HTML report content
    with open(report_path, "r", encoding="utf-8") as file:
        report_content = file.read()

    return (
        snapshot_path,
        report_content,
        report_path,
        returns_path,
    )


# Create the Gradio interface
with gr.Blocks() as interface:
    gr.Markdown("# Stock Performance Analyzer")
    gr.Markdown(
        "Enter a stock symbol and a benchmark to generate a performance report and snapshot."
    )

    with gr.Row():
        with gr.Column():
            symbol_input = gr.Textbox(
                label="Stock Symbol (e.g., TSLA,NSFT,AAPL)",
                placeholder="Enter stock symbol",
                info="Some symbols may require a dot(.)suffix of corresponding exchange as TCS.NS",
            )
            benchmark_input = gr.Textbox(
                label="Benchmark Symbol (e.g., ^DJI,^NSEI,^UKX,SPY)",
                placeholder="Enter benchmark symbol",
                info="For index use (^) as that is the accepted format.It can also be other valid stocks/symbols too.",
            )

            generate_button = gr.Button("Generate Report", variant="primary")
            returns_output = gr.Image(label="Yearly Returns")

        with gr.Column():
            download_button = gr.File(label="Download Report")
            snapshot_output = gr.Image(label="Performance Snapshot")

    with gr.Row():
        report_output = gr.HTML(label="Performance Report")

    def generate_report(symbol, benchmark):
        snapshot_path, report_content, report_path, returns_path = gradio_interface(
            symbol, benchmark
        )
        return (
            snapshot_path,
            report_content,
            report_path,
            returns_path,
        )

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

# Launch the Gradio app
if __name__ == "__main__":
    interface.launch()
