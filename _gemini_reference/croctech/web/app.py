"""
Flask Web Dashboard for CrocTech Framework.
Interactive UI for real-time crochet pattern verification, 3D visualization, and export.
"""

import os
from flask import Flask, render_template, request, jsonify, send_file
from croctech.ai.pipeline import PatternSynthesisPipeline
from croctech.visualizer.svg_chart import SvgChartGenerator
from croctech.visualizer.html_report import HtmlReportGenerator
from croctech.exporter.markdown_export import MarkdownExporter
from croctech.exporter.json_export import JsonExporter
from examples.santa_hat_keychain import SANTA_HAT_RAW_TEXT

app = Flask(__name__)
pipeline = PatternSynthesisPipeline()

# In-memory cache of latest verified pattern and report
latest_cache = {
    "pattern": None,
    "report": None,
    "raw_text": SANTA_HAT_RAW_TEXT
}

@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")

@app.route("/api/verify", methods=["POST"])
def verify_api():
    """Verify submitted pattern text and return JSON metrics and SVG."""
    data = request.get_json() or {}
    text = data.get("text", SANTA_HAT_RAW_TEXT)
    title = data.get("title", "Crochet Pattern")

    pattern, report, fixes = pipeline.process_pattern_text(text, title=title)
    latest_cache["pattern"] = pattern
    latest_cache["report"] = report
    latest_cache["raw_text"] = text

    chart_svg = SvgChartGenerator.generate_circular_chart(pattern, report, size=520)
    profile_svg = SvgChartGenerator.generate_3d_profile_svg(report, width=460, height=360)

    dim = report.dimensions
    yarn_data = {
        c: {
            "stitches": u.stitch_count,
            "meters": u.meters_required,
            "grams": u.grams_required,
            "skeins": u.skeins_estimated
        } for c, u in report.yarn_usage.items()
    }

    round_data = [
        {
            "round": s.round_number,
            "prev_sts": s.previous_round_count,
            "consumed": s.consumed_count,
            "produced": s.calculated_count,
            "is_valid": s.is_balanced,
            "color": s.color
        } for s in report.round_summaries
    ]

    return jsonify({
        "is_valid": report.is_valid,
        "error_count": report.error_count,
        "warning_count": report.warning_count,
        "fixes": fixes,
        "dimensions": {
            "finished_height_mm": dim.finished_height_mm,
            "finished_height_cm": dim.finished_height_cm,
            "finished_height_in": dim.finished_height_inches,
            "max_diameter_mm": dim.max_diameter_mm,
            "max_diameter_cm": dim.max_diameter_cm,
            "max_diameter_in": dim.max_diameter_inches,
            "total_stitches": dim.total_stitches,
            "total_rows": dim.total_rows,
            "has_folded_brim": dim.has_folded_brim,
            "folded_rows": dim.folded_rows_count,
            "pompom_height_mm": dim.pompom_height_mm
        },
        "yarn_usage": yarn_data,
        "rounds": round_data,
        "chart_svg": chart_svg,
        "profile_svg": profile_svg
    })

@app.route("/api/sample", methods=["GET"])
def get_sample():
    """Return the user's prompt Santa Hat Keychain pattern text."""
    return jsonify({
        "title": "Santa Hat Keychain",
        "text": SANTA_HAT_RAW_TEXT
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)

