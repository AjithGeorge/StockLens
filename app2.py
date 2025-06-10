import gradio as gr
from config import SCREENER, interval_options
from tradingview_ta import Interval

def get_technical_analysis_interface(symbol, exchange, country, interval):
    """Interface wrapper for technical analysis"""
    try:
        # This would call your actual get_technical_analysis function
        # For now, returning a placeholder
        return f"Technical Analysis for {symbol} on {exchange} ({country}) at {interval} interval"
    except Exception as e:
        return f"Error: {str(e)}"

def get_performance_snapshot_interface(symbol):
    """Interface wrapper for performance snapshot"""
    try:
        # This would call your actual get_performance_snapshot function
        # For now, returning a placeholder
        return f"Performance snapshot for {symbol}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_comparison_report_interface(symbol, benchmark):
    """Interface wrapper for comparison report"""
    try:
        # This would call your actual get_comparison_report function
        # For now, returning a placeholder
        return f"Comparison report: {symbol} vs {benchmark}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Trading Analysis Agent") as app:
    gr.Markdown("# Trading Analysis Agent")
    gr.Markdown("Get technical analysis, performance snapshots, and comparison reports for stocks.")
    
    with gr.Tab("Technical Analysis"):
        with gr.Row():
            symbol_input = gr.Textbox(label="Symbol", placeholder="Enter stock symbol (e.g., AAPL)")
            exchange_input = gr.Textbox(label="Exchange", placeholder="Enter exchange (e.g., NASDAQ)")
        
        with gr.Row():
            country_dropdown = gr.Dropdown(
                choices=list(SCREENER.keys())[1:],  # Skip "None" option
                label="Country",
                value="america"
            )
            interval_dropdown = gr.Dropdown(
                choices=[str(interval) for interval in interval_options],
                label="Interval",
                value=str(Interval.INTERVAL_1_DAY)
            )
        
        analyze_btn = gr.Button("Get Technical Analysis")
        analysis_output = gr.Textbox(label="Analysis Result", lines=10)
        
        analyze_btn.click(
            get_technical_analysis_interface,
            inputs=[symbol_input, exchange_input, country_dropdown, interval_dropdown],
            outputs=analysis_output
        )
    
    with gr.Tab("Performance Snapshot"):
        perf_symbol_input = gr.Textbox(label="Symbol", placeholder="Enter stock symbol")
        perf_btn = gr.Button("Get Performance Snapshot")
        perf_output = gr.Textbox(label="Performance Result", lines=10)
        
        perf_btn.click(
            get_performance_snapshot_interface,
            inputs=perf_symbol_input,
            outputs=perf_output
        )
    
    with gr.Tab("Comparison Report"):
        with gr.Row():
            comp_symbol_input = gr.Textbox(label="Symbol", placeholder="Enter stock symbol")
            benchmark_input = gr.Textbox(label="Benchmark", placeholder="Enter benchmark symbol")
        
        comp_btn = gr.Button("Get Comparison Report")
        comp_output = gr.Textbox(label="Comparison Result", lines=10)
        
        comp_btn.click(
            get_comparison_report_interface,
            inputs=[comp_symbol_input, benchmark_input],
            outputs=comp_output
        )

if __name__ == "__main__":
    app.launch(share=True)
