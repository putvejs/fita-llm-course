"""
Step 3: Combine all charts and insights into a self-contained HTML report and PDF.
Outputs: output/report.html, output/report.pdf
"""
import base64
import json
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT_DIR = "output"


def _img_to_base64(path: str) -> str | None:
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _insights_to_html(text: str) -> str:
    lines = [l.lstrip("-•* ").strip() for l in text.split("\n") if l.strip().lstrip("-•* ")]
    items = "".join(f"<li>{l}</li>" for l in lines if l)
    return f'<ul class="insights">{items}</ul>' if items else f'<p class="insights-text">{text}</p>'


def generate_report() -> str:
    with open(os.path.join(OUTPUT_DIR, "results.json"), encoding="utf-8") as f:
        results = json.load(f)

    sections = ""
    for i, r in enumerate(results, 1):
        b64 = _img_to_base64(r.get("chart_path"))

        if r.get("error") and not b64:
            chart_html = f'<div class="chart-error">⚠ {r["error"]}</div>'
        elif b64:
            chart_html = f'<img src="data:image/png;base64,{b64}" alt="{r["title"]}">'
        else:
            chart_html = '<div class="chart-error">Chart not available</div>'

        insights_html = _insights_to_html(r["insights"]) if r.get("insights") else ""

        sql_html = ""
        if r.get("sql"):
            sql_html = (
                f'<details><summary>SQL</summary>'
                f'<pre><code>{r["sql"]}</code></pre></details>'
            )

        badge = f'<span class="badge badge-{r["chart_type"]}">{r["chart_type"]}</span>'
        rows_note = f'<span class="rows-note">{r["rows_count"]} rows</span>' if r["rows_count"] else ""

        sections += f"""
<section class="card">
  <div class="card-header">
    <div class="card-num">{i}</div>
    <div class="card-meta">
      <h2>{r["title"]} {badge} {rows_note}</h2>
      <p class="card-desc">{r.get("description", "")}</p>
    </div>
  </div>
  <div class="card-body">
    <div class="chart-wrap">{chart_html}</div>
    <div class="insights-wrap">{insights_html}</div>
  </div>
  {sql_html}
</section>"""

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_ok = sum(1 for r in results if not r.get("error"))

    badge_css = "\n".join(
        f'.badge-{t} {{ background: {c}; }}'
        for t, c in [
            ("bar", "#4C72B0"), ("horizontal_bar", "#DD8452"), ("line", "#55A868"),
            ("pie", "#8172B3"), ("scatter", "#C44E52"),
        ]
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Data Visualization Report</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
      background:#eef0f4;color:#1a1a2e;line-height:1.6}}

header{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
        color:#fff;padding:36px 48px}}
header h1{{font-size:1.9rem;font-weight:700;margin-bottom:6px}}
.meta{{opacity:.65;font-size:.85rem;margin-bottom:20px}}
.stats{{display:flex;gap:24px;flex-wrap:wrap}}
.stat{{background:rgba(255,255,255,.1);border-radius:8px;padding:12px 22px}}
.stat-num{{font-size:1.7rem;font-weight:700}}
.stat-label{{font-size:.75rem;opacity:.75}}

main{{max-width:1120px;margin:28px auto;padding:0 20px 56px}}

.card{{background:#fff;border-radius:12px;margin-bottom:24px;
       box-shadow:0 2px 10px rgba(0,0,0,.07);overflow:hidden}}
.card-header{{display:flex;align-items:flex-start;gap:14px;
              padding:18px 22px;border-bottom:1px solid #f0f0f0}}
.card-num{{background:#4C72B0;color:#fff;border-radius:50%;
           width:34px;height:34px;display:flex;align-items:center;
           justify-content:center;font-weight:700;flex-shrink:0;font-size:.9rem}}
.card-meta h2{{font-size:1.05rem;font-weight:600;display:flex;
               align-items:center;gap:8px;flex-wrap:wrap}}
.card-desc{{color:#666;font-size:.85rem;margin-top:3px}}

.badge{{display:inline-block;color:#fff;font-size:.7rem;font-weight:600;
        border-radius:4px;padding:2px 7px;text-transform:uppercase;letter-spacing:.04em}}
{badge_css}
.rows-note{{font-size:.75rem;color:#999;font-weight:400}}

.card-body{{display:grid;grid-template-columns:1fr 300px}}
.chart-wrap{{padding:18px;border-right:1px solid #f0f0f0}}
.chart-wrap img{{width:100%;height:auto;border-radius:6px}}
.chart-error{{padding:16px;color:#c0392b;background:#fdf2f2;
              border-radius:6px;font-size:.85rem}}
.insights-wrap{{padding:20px;overflow-y:auto}}

ul.insights{{list-style:none}}
ul.insights li{{padding:7px 0 7px 16px;border-bottom:1px solid #f5f5f5;
                font-size:.84rem;color:#333;position:relative}}
ul.insights li::before{{content:"▸";position:absolute;left:0;color:#4C72B0;font-size:.9rem}}
ul.insights li:last-child{{border-bottom:none}}
.insights-text{{font-size:.84rem;color:#444}}

details{{border-top:1px solid #f0f0f0}}
summary{{padding:9px 22px;font-size:.78rem;color:#999;cursor:pointer;user-select:none}}
summary:hover{{color:#4C72B0}}
pre{{margin:0;padding:10px 22px 18px;background:#f8f9fa;font-size:.76rem;overflow-x:auto}}
code{{color:#2d6a9f}}

@media(max-width:700px){{
  .card-body{{grid-template-columns:1fr}}
  .chart-wrap{{border-right:none;border-bottom:1px solid #f0f0f0}}
  header{{padding:24px}}
  .stats{{gap:12px}}
}}
</style>
</head>
<body>
<header>
  <h1>Data Visualization Report</h1>
  <p class="meta">Generated: {generated_at}</p>
  <div class="stats">
    <div class="stat"><div class="stat-num">{len(results)}</div><div class="stat-label">Charts planned</div></div>
    <div class="stat"><div class="stat-num">{total_ok}</div><div class="stat-label">Charts generated</div></div>
  </div>
</header>
<main>
{sections}
</main>
</body>
</html>"""

    report_path = os.path.join(OUTPUT_DIR, "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Step 3] Report saved -> {report_path}  ({len(html) // 1024} KB)")
    return report_path


def generate_pdf() -> str:
    with open(os.path.join(OUTPUT_DIR, "results.json"), encoding="utf-8") as f:
        results = json.load(f)

    pdf_path = os.path.join(OUTPUT_DIR, "report.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    W = A4[0] - 3.6 * cm  # usable width

    base = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=base["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#888888"),
        spaceAfter=20,
    )
    chart_title_style = ParagraphStyle(
        "ChartTitle",
        parent=base["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=4,
        spaceAfter=2,
    )
    desc_style = ParagraphStyle(
        "Desc",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        spaceAfter=10,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#333333"),
        leftIndent=14,
        spaceBefore=2,
        spaceAfter=2,
        bulletIndent=4,
        bulletText="▸",
    )
    sql_style = ParagraphStyle(
        "SQL",
        parent=base["Code"],
        fontSize=7,
        textColor=colors.HexColor("#2d6a9f"),
        backColor=colors.HexColor("#f8f9fa"),
        leftIndent=8,
        rightIndent=8,
        spaceBefore=4,
        spaceAfter=4,
    )

    ACCENT = colors.HexColor("#4C72B0")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_ok = sum(1 for r in results if not r.get("error"))

    story = [
        Spacer(1, 0.5 * cm),
        Paragraph("Data Visualization Report", title_style),
        Paragraph(f"Generated: {generated_at} &nbsp;·&nbsp; {total_ok}/{len(results)} charts", meta_style),
    ]

    # Thin divider line via a 1-row table
    story.append(
        Table([[""]], colWidths=[W], rowHeights=[2],
              style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                                ("LINEABOVE", (0, 0), (-1, -1), 0, colors.white)]))
    )
    story.append(Spacer(1, 0.6 * cm))

    for i, r in enumerate(results, 1):
        # Number + title header row
        num_para = Paragraph(f'<font color="white"><b>{i}</b></font>',
                             ParagraphStyle("Num", parent=base["Normal"], fontSize=10,
                                            alignment=TA_CENTER))
        num_cell = Table([[num_para]], colWidths=[0.7 * cm], rowHeights=[0.7 * cm],
                         style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                           ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
                                           ("ROUNDEDCORNERS", [4, 4, 4, 4])]))

        header = Table(
            [[num_cell, Paragraph(r["title"], chart_title_style)]],
            colWidths=[0.9 * cm, W - 0.9 * cm],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (1, 0), (1, 0), 8)]),
        )
        story.append(header)
        story.append(Paragraph(r.get("description", ""), desc_style))

        # Chart image
        chart_path = r.get("chart_path", "")
        if chart_path and os.path.exists(chart_path):
            img = Image(chart_path, width=W, height=W * 0.5)
            story.append(img)
        elif r.get("error"):
            story.append(Paragraph(f"⚠ {r['error']}", desc_style))

        # Insights bullets
        if r.get("insights"):
            story.append(Spacer(1, 0.25 * cm))
            for line in r["insights"].split("\n"):
                text = line.lstrip("-•* ").strip()
                if text:
                    story.append(Paragraph(text, bullet_style))

        # SQL (collapsed in HTML, shown small in PDF)
        if r.get("sql"):
            sql_lines = r["sql"].replace("&", "&amp;").replace("<", "&lt;")
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(sql_lines, sql_style))

        if i < len(results):
            story.append(PageBreak())

    doc.build(story)
    print(f"[Step 3] PDF saved -> {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    generate_report()
    generate_pdf()
