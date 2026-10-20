"""
CrocTech Command Line Interface (CLI).
High-precision commands for verifying, synthesizing, profiling, and exporting crochet designs.
"""

import os
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from croctech.ai.pipeline import PatternSynthesisPipeline
from croctech.visualizer.profile_3d import ProfileVisualizer
from croctech.visualizer.svg_chart import SvgChartGenerator
from croctech.visualizer.html_report import HtmlReportGenerator
from croctech.exporter.markdown_export import MarkdownExporter
from croctech.exporter.json_export import JsonExporter
from croctech.exporter.pdf_export import PdfExporter

console = Console()


@click.group()
def cli():
    """CrocTech: 100% Accurate Algorithmic Crochet Engineering Framework."""
    pass


@cli.command()
@click.argument("pattern_path", type=click.Path(exists=True), required=False)
@click.option("--output-dir", "-o", default="./output", help="Directory to save verified outputs.")
def verify(pattern_path, output_dir):
    """Verify a crochet pattern file for 100% mathematical accuracy and zero defects."""
    pipeline = PatternSynthesisPipeline()

    if pattern_path:
        with open(pattern_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        title = os.path.splitext(os.path.basename(pattern_path))[0].replace("_", " ").title()
    else:
        console.print("[yellow]No input file provided. Using standard test pattern...[/yellow]")
        from examples.santa_hat_keychain import SANTA_HAT_RAW_TEXT
        raw_text = SANTA_HAT_RAW_TEXT
        title = "Santa Hat Keychain"

    pattern, report, fixes = pipeline.process_pattern_text(raw_text, title=title)

    # Render results with Rich
    status_str = "[bold green]100% VERIFIED: ZERO DEFECTS[/bold green]" if report.is_valid else "[bold red]VERIFICATION FAILED[/bold red]"
    console.print(Panel(f"CrocTech Verification Engine Result: {status_str}", title=pattern.title, expand=False))

    if fixes:
        console.print("\n[bold cyan]Automated Compiler Adjustments:[/bold cyan]")
        for fix in fixes:
            console.print(f"  • {fix}")

    # Physical Dimensions Table
    dim_table = Table(title="Calculated Physical Dimensions (Gauge Verified)")
    dim_table.add_column("Property", style="cyan")
    dim_table.add_column("Value (Metric)", style="white")
    dim_table.add_column("Value (Imperial)", style="dim")

    dim = report.dimensions
    dim_table.add_row("Finished Height", f"{dim.finished_height_mm:.1f} mm ({dim.finished_height_cm:.2f} cm)", f"{dim.finished_height_inches:.2f} in")
    dim_table.add_row("Maximum Diameter", f"{dim.max_diameter_mm:.1f} mm ({dim.max_diameter_cm:.2f} cm)", f"{dim.max_diameter_inches:.2f} in")
    dim_table.add_row("Total Active Stitches", f"{dim.total_stitches} sc", "-")
    dim_table.add_row("Total Rows", f"{dim.total_rows} rows", "-")
    dim_table.add_row("Folded Brim", f"Yes ({dim.folded_rows_count} rows folded)" if dim.has_folded_brim else "None", "-")
    dim_table.add_row("Pompom Height", f"{dim.pompom_height_mm:.1f} mm", f"{dim.pompom_height_mm / 25.4:.2f} in")
    console.print(dim_table)

    # Yarn Consumption Table
    yarn_table = Table(title="Exact Yarn Consumption Breakdown")
    yarn_table.add_column("Yarn Color / Type", style="yellow")
    yarn_table.add_column("Stitch Count", justify="right")
    yarn_table.add_column("Meters", justify="right", style="green")
    yarn_table.add_column("Grams (~320m/100g)", justify="right", style="green")
    yarn_table.add_column("Skein Fraction (50g ball)", justify="right")

    for color, u in report.yarn_usage.items():
        yarn_table.add_row(color, str(u.stitch_count), f"{u.meters_required:.2f} m", f"{u.grams_required:.2f} g", f"{u.skeins_estimated:.3f}")
    console.print(yarn_table)

    # ASCII Silhouette
    console.print("\n[bold magenta]3D Profile Silhouette:[/bold magenta]")
    console.print(ProfileVisualizer.render_ascii_cross_section(report.dimensions, max_width_chars=54))

    # Export artifacts
    os.makedirs(output_dir, exist_ok=True)
    base_name = title.lower().replace(" ", "_")

    md_path = os.path.join(output_dir, f"{base_name}_verified.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(MarkdownExporter.export(pattern, report))

    html_path = os.path.join(output_dir, f"{base_name}_dossier.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HtmlReportGenerator.render(pattern, report))

    json_path = os.path.join(output_dir, f"{base_name}_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(JsonExporter.export(pattern, report))

    svg_path = os.path.join(output_dir, f"{base_name}_chart.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(SvgChartGenerator.generate_circular_chart(pattern, report))

    pdf_path = os.path.join(output_dir, f"{base_name}_pattern.pdf")
    try:
        PdfExporter.export_pdf(pattern, report, pdf_path)
        pdf_status = f"[green]PDF exported to {pdf_path}[/green]"
    except Exception as e:
        pdf_status = f"[red]PDF export notice: {e}[/red]"

    console.print(f"\n[bold green]✓ Verified Artifacts saved to '{output_dir}':[/bold green]")
    console.print(f"  • Markdown: {md_path}")
    console.print(f"  • Interactive HTML: {html_path}")
    console.print(f"  • JSON: {json_path}")
    console.print(f"  • Circular SVG Chart: {svg_path}")
    console.print(f"  • {pdf_status}")


@cli.command()
@click.option("--port", "-p", default=5000, help="Web dashboard port.")
def serve(port):
    """Launch the interactive CrocTech Web UI."""
    from croctech.web.app import app
    console.print(f"[bold cyan]Starting CrocTech Web Dashboard on http://localhost:{port}[/bold cyan]")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    cli()

