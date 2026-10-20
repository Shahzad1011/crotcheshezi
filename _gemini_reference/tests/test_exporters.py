"""
Unit Tests for Markdown, JSON, SVG, and HTML Exporters.
"""

import os
from croctech.ai.pipeline import PatternSynthesisPipeline
from croctech.exporter.markdown_export import MarkdownExporter
from croctech.exporter.json_export import JsonExporter
from croctech.visualizer.svg_chart import SvgChartGenerator
from croctech.visualizer.html_report import HtmlReportGenerator
from examples.santa_hat_keychain import SANTA_HAT_RAW_TEXT


def test_exporters():
    """Verify that all exporters generate valid output strings."""
    pipeline = PatternSynthesisPipeline()
    pattern, report, fixes = pipeline.process_pattern_text(SANTA_HAT_RAW_TEXT, title="Santa Hat")

    md = MarkdownExporter.export(pattern, report)
    assert "# Santa Hat" in md
    assert "Verification Status" in md
    assert "252" in md

    js = JsonExporter.export(pattern, report)
    assert '"schema_version": "croctech-v1.0"' in js
    assert '"is_valid": true' in js

    svg = SvgChartGenerator.generate_circular_chart(pattern, report)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Santa Hat" in svg

    html = HtmlReportGenerator.render(pattern, report)
    assert "<!DOCTYPE html>" in html
    assert "100% ACCURATE" in html

