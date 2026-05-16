# /devpulse/backend/app/services/export_service.py
from __future__ import annotations

from pathlib import Path

import markdown2
from weasyprint import HTML


def export_markdown(content: str, output_path: Path) -> None:
    output_path.write_text(content, encoding="utf-8")


def export_pdf(markdown_content: str, output_path: Path) -> None:
    html = markdown2.markdown(markdown_content)
    HTML(string=html).write_pdf(target=str(output_path))
