#!/usr/bin/env python3
"""Generate submission-ready vector figure assets from report snapshots."""

from __future__ import annotations

import argparse
import csv
import html
import shutil
import subprocess
from pathlib import Path


CAMPAIGN_REPORT = Path("reports/lobby-capture-campaign.csv")
INTERACTION_REPORT = Path("reports/lobby-capture-interactions.csv")
SENSITIVITY_REPORT = Path("reports/lobby-capture-sensitivity.csv")
FIGURE_DIR = Path("paper/figures")

WIDTH = 1800
HEIGHT = 1100

INTERACTION_ROWS = {
    "interaction-enforcement-disclosure-0-10-0-10": "Low E/D",
    "interaction-enforcement-disclosure-1-25-1-25": "High E/D",
    "interaction-financing-evasion-1-25-0-90": "Finance+evasion",
    "interaction-cooling-1-25-revolving-door": "Cooling+door",
}

SCENARIO_TRADEOFF_ROWS = {
    "open-access-lobbying": ("Open", 70, 52, "start"),
    "low-salience-technical-rulemaking": ("Rule", 70, 46, "start"),
    "campaign-finance-dominant": ("Camp", 70, -44, "start"),
    "dark-money-dominant": ("Dark", 70, 5, "start"),
    "revolving-door-dominant": ("Door", 70, 46, "start"),
    "real-time-transparency": ("RTD", 70, -44, "start"),
    "democracy-vouchers": ("Vouch", 70, 74, "start"),
    "full-anti-capture-bundle": ("Bundle", 70, 18, "start"),
    "bundle-with-evasion": ("Evasion", 70, -44, "start"),
}

CHANNEL_ROWS = [
    ("open-access-lobbying", "Open access"),
    ("low-salience-technical-rulemaking", "Rulemaking"),
    ("campaign-finance-dominant", "Campaign"),
    ("dark-money-dominant", "Dark money"),
    ("democracy-vouchers", "Vouchers"),
    ("full-anti-capture-bundle", "Full bundle"),
    ("bundle-with-evasion", "Bundle+evasion"),
]

CHANNELS = [
    ("directAccessShare", "Access", "#d0d0d0"),
    ("informationDistortionShare", "Info", "#ababab"),
    ("publicCampaignShare", "Public", "#808080"),
    ("campaignFinanceShare", "Campaign", "#595959"),
    ("darkMoneyShare", "Dark", "#333333"),
    ("revolvingDoorShare", "Door", "#1a1a1a"),
    ("defensiveChannelShare", "Defense", "#000000"),
]

EVASION_ROWS = [
    ("sensitivity-evasion-0-00", "0.00"),
    ("sensitivity-evasion-0-30", "0.30"),
    ("sensitivity-evasion-0-60", "0.60"),
    ("sensitivity-evasion-0-90", "0.90"),
]

FIGURES = (
    "channel_mix.tex",
    "evasion_sensitivity.tex",
    "interaction_tradeoffs.tex",
    "scenario_tradeoffs.tex",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-report", type=Path, default=CAMPAIGN_REPORT)
    parser.add_argument("--interaction-report", type=Path, default=INTERACTION_REPORT)
    parser.add_argument("--sensitivity-report", type=Path, default=SENSITIVITY_REPORT)
    parser.add_argument("--figure-dir", type=Path, default=FIGURE_DIR)
    parser.add_argument(
        "--output",
        type=Path,
        help="Compatibility path for the interaction wrapper; all figure assets are written to its parent directory.",
    )
    args = parser.parse_args()

    if args.output is not None:
        args.figure_dir = args.output.parent

    args.figure_dir.mkdir(parents=True, exist_ok=True)
    campaign_rows = index_rows(read_rows(args.campaign_report))
    interaction_rows = index_rows(read_rows(args.interaction_report))
    sensitivity_rows = index_rows(read_rows(args.sensitivity_report))

    write_channel_mix(campaign_rows, args.campaign_report, args.figure_dir)
    write_evasion_sensitivity(sensitivity_rows, args.sensitivity_report, args.figure_dir)
    write_interaction_tradeoffs(interaction_rows, args.interaction_report, args.figure_dir)
    write_scenario_tradeoffs(campaign_rows, args.campaign_report, args.figure_dir)

    for name in FIGURES:
        print(f"Wrote {args.figure_dir / name}")
    return 0


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def index_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["scenarioKey"]: row for row in rows}


def require_rows(indexed: dict[str, dict[str, str]], keys: list[str]) -> None:
    missing = [key for key in keys if key not in indexed]
    if missing:
        raise SystemExit("Missing figure rows: " + ", ".join(missing))


def write_channel_mix(indexed: dict[str, dict[str, str]], report: Path, figure_dir: Path) -> None:
    require_rows(indexed, [key for key, _label in CHANNEL_ROWS])
    body: list[str] = []
    chart_left = 440
    chart_top = 310
    chart_width = 1040
    row_gap = 82
    bar_height = 38
    axis_bottom = chart_top + row_gap * len(CHANNEL_ROWS) + 18

    body.extend(title_block("Channel allocation mix", "Share of lobby spending by channel"))
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = chart_left + tick * chart_width
        body.append(line(x, chart_top - 22, x, axis_bottom, "grid"))
        body.append(text(x, axis_bottom + 48, f"{tick:g}", anchor="middle", css_class="tick"))

    for index, (key, label) in enumerate(CHANNEL_ROWS):
        row = indexed[key]
        y = chart_top + index * row_gap
        body.append(text(70, y + 29, label, anchor="start"))
        x = chart_left
        for field, _legend, color in CHANNELS:
            width = max(0.0, min(chart_width, as_float(row[field]) * chart_width))
            if width > 0.5:
                body.append(rect(x, y, width, bar_height, color, "segment"))
            x += width

    body.append(line(chart_left, chart_top - 20, chart_left, axis_bottom, "axis"))
    body.append(line(chart_left, axis_bottom, chart_left + chart_width, axis_bottom, "axis"))
    body.append(text(chart_left + chart_width / 2, axis_bottom + 92, "Share of lobby spending by channel", anchor="middle"))

    legend_x = 70
    legend_y = 180
    for index, (_field, label, color) in enumerate(CHANNELS):
        x = legend_x + (index % 4) * 405
        y = legend_y + (index // 4) * 50
        body.append(rect(x, y - 24, 42, 28, color, "legend-swatch"))
        body.append(text(x + 56, y, label, anchor="start", css_class="small"))

    write_svg_and_pdf(
        figure_dir,
        "Figure_1_channel_mix",
        "Channel allocation mix",
        "Stacked horizontal bars showing modeled budget allocation shares across influence channels.",
        body,
    )
    write_wrapper(
        figure_dir / "channel_mix.tex",
        "Figure_1_channel_mix.pdf",
        report,
        "Channel allocation mix for selected scenarios. The stacked bars show how the model routes lobbying budgets across access, information, public campaigns, campaign finance, dark money, revolving-door pressure, and defensive reform spending.",
        "fig:channel-mix",
    )


def write_evasion_sensitivity(indexed: dict[str, dict[str, str]], report: Path, figure_dir: Path) -> None:
    require_rows(indexed, [key for key, _label in EVASION_ROWS])
    plot = Plot(left=260, top=170, width=1230, height=720)
    body: list[str] = []
    body.extend(title_block("Sensitivity to evasion freedom", "Hidden influence and transparency response"))
    draw_axes(
        body,
        plot,
        x_ticks=(0.0, 0.3, 0.6, 0.9),
        y_ticks=(0.0, 0.1, 0.2, 0.3, 0.4),
        x_max=0.9,
        y_max=0.4,
        x_label="Evasion freedom",
        y_label="Share / gain",
    )

    hidden_points = []
    transparency_points = []
    for key, raw_x in EVASION_ROWS:
        row = indexed[key]
        x_value = float(raw_x)
        hidden_points.append(plot.point(x_value, as_float(row["hiddenInfluenceShare"]), 0.9, 0.4))
        transparency_points.append(plot.point(x_value, as_float(row["netTransparencyGain"]), 0.9, 0.4))

    body.append(polyline(hidden_points, "series-primary"))
    body.append(polyline(transparency_points, "series-secondary"))
    for x, y in hidden_points:
        body.append(rect(x - 12, y - 12, 24, 24, "#111111", "point"))
    for x, y in transparency_points:
        body.append(rect(x - 12, y - 12, 24, 24, "#777777", "point"))

    body.append(line(1210, 170, 1290, 170, "series-primary"))
    body.append(text(1312, 178, "Hidden influence", anchor="start", css_class="small"))
    body.append(line(1210, 224, 1290, 224, "series-secondary"))
    body.append(text(1312, 232, "Net transparency", anchor="start", css_class="small"))

    write_svg_and_pdf(
        figure_dir,
        "Figure_2_evasion_sensitivity",
        "Sensitivity to evasion freedom",
        "Line chart showing hidden influence rising as evasion freedom increases and net transparency gain falling.",
        body,
    )
    write_wrapper(
        figure_dir / "evasion_sensitivity.tex",
        "Figure_2_evasion_sensitivity.pdf",
        report,
        "Sensitivity to evasion freedom. Hidden influence rises as evasion freedom increases, while net transparency gains fall, illustrating why reform assessment should track substitution rather than visible capture alone.",
        "fig:evasion-sensitivity",
    )


def write_interaction_tradeoffs(indexed: dict[str, dict[str, str]], report: Path, figure_dir: Path) -> None:
    require_rows(indexed, list(INTERACTION_ROWS))
    offsets = {
        "interaction-enforcement-disclosure-0-10-0-10": (64, -38, "start"),
        "interaction-enforcement-disclosure-1-25-1-25": (64, -38, "start"),
        "interaction-financing-evasion-1-25-0-90": (-64, -38, "end"),
        "interaction-cooling-1-25-revolving-door": (64, 42, "start"),
    }
    body = scatter_body(
        title="Interaction tradeoff view",
        subtitle="Hidden influence versus net transparency gain",
        x_label="Hidden influence",
        y_label="Net transparency gain",
        x_max=0.4,
        y_max=0.4,
        x_ticks=(0.0, 0.1, 0.2, 0.3, 0.4),
        y_ticks=(0.0, 0.1, 0.2, 0.3, 0.4),
        points=[
            ScatterPoint(
                label=label,
                x=as_float(indexed[key]["hiddenInfluenceShare"]),
                y=as_float(indexed[key]["netTransparencyGain"]),
                dx=offsets[key][0],
                dy=offsets[key][1],
                anchor=offsets[key][2],
                emphasis=False,
            )
            for key, label in INTERACTION_ROWS.items()
        ],
    )
    write_svg_and_pdf(
        figure_dir,
        "Figure_3_interaction_tradeoffs",
        "Interaction tradeoff view",
        "Scatter plot comparing hidden influence against net transparency gain after reforms bind.",
        body,
    )
    write_wrapper(
        figure_dir / "interaction_tradeoffs.tex",
        "Figure_3_interaction_tradeoffs.pdf",
        report,
        "Interaction tradeoff view. Points compare hidden influence against net transparency gain after reforms bind; the desirable direction is upper-left.",
        "fig:interaction-tradeoffs",
        extra="x=hidden influence; y=Net transparency gain",
    )


def write_scenario_tradeoffs(indexed: dict[str, dict[str, str]], report: Path, figure_dir: Path) -> None:
    require_rows(indexed, list(SCENARIO_TRADEOFF_ROWS))
    points = []
    for key, (label, dx, dy, anchor) in SCENARIO_TRADEOFF_ROWS.items():
        points.append(
            ScatterPoint(
                label=label,
                x=as_float(indexed[key]["captureRate"]),
                y=as_float(indexed[key]["hiddenInfluenceShare"]),
                dx=dx,
                dy=dy,
                anchor=anchor,
                emphasis=key in {"full-anti-capture-bundle", "bundle-with-evasion"},
            )
        )
    body = scatter_body(
        title="Scenario tradeoff view",
        subtitle="Observed capture versus hidden influence",
        x_label="Capture rate",
        y_label="Hidden influence share",
        x_max=0.75,
        y_max=0.4,
        x_ticks=(0.0, 0.25, 0.5, 0.75),
        y_ticks=(0.0, 0.1, 0.2, 0.3, 0.4),
        points=points,
    )
    write_svg_and_pdf(
        figure_dir,
        "Figure_4_scenario_tradeoffs",
        "Scenario tradeoff view",
        "Scatter plot comparing observed capture rates against hidden influence shares across selected scenarios.",
        body,
    )
    write_wrapper(
        figure_dir / "scenario_tradeoffs.tex",
        "Figure_4_scenario_tradeoffs.pdf",
        report,
        "Scenario tradeoff between observed capture and hidden influence. The low-capture bundle cases remain substantively different when evasion preserves hidden influence capacity.",
        "fig:scenario-tradeoffs",
        extra="x=capture rate; y=Hidden influence share",
    )


def scatter_body(
    title: str,
    subtitle: str,
    x_label: str,
    y_label: str,
    x_max: float,
    y_max: float,
    x_ticks: tuple[float, ...],
    y_ticks: tuple[float, ...],
    points: list["ScatterPoint"],
) -> list[str]:
    plot = Plot(left=260, top=170, width=1230, height=720)
    body: list[str] = []
    body.extend(title_block(title, subtitle))
    draw_axes(body, plot, x_ticks, y_ticks, x_max, y_max, x_label, y_label)
    for point in points:
        x, y = plot.point(point.x, point.y, x_max, y_max)
        size = 32 if point.emphasis else 24
        color = "#555555" if point.emphasis else "#111111"
        body.append(rect(x - size / 2, y - size / 2, size, size, color, "point"))
        body.append(text(x + point.dx, y + point.dy, point.label, anchor=point.anchor, css_class="label"))
    return body


class ScatterPoint:
    def __init__(self, label: str, x: float, y: float, dx: int, dy: int, anchor: str, emphasis: bool) -> None:
        self.label = label
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.anchor = anchor
        self.emphasis = emphasis


class Plot:
    def __init__(self, left: int, top: int, width: int, height: int) -> None:
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def point(self, x_value: float, y_value: float, x_max: float, y_max: float) -> tuple[float, float]:
        x = self.left + scale(x_value, x_max) * self.width
        y = self.bottom - scale(y_value, y_max) * self.height
        return x, y


def draw_axes(
    body: list[str],
    plot: Plot,
    x_ticks: tuple[float, ...],
    y_ticks: tuple[float, ...],
    x_max: float,
    y_max: float,
    x_label: str,
    y_label: str,
) -> None:
    for tick in x_ticks:
        x = plot.left + tick / x_max * plot.width
        body.append(line(x, plot.top, x, plot.bottom, "grid"))
        body.append(text(x, plot.bottom + 48, f"{tick:.2g}", anchor="middle", css_class="tick"))
    for tick in y_ticks:
        y = plot.bottom - tick / y_max * plot.height
        body.append(line(plot.left, y, plot.left + plot.width, y, "grid"))
        body.append(text(plot.left - 40, y + 10, f"{tick:.1f}", anchor="end", css_class="tick"))
    body.append(line(plot.left, plot.bottom, plot.left + plot.width, plot.bottom, "axis"))
    body.append(line(plot.left, plot.top, plot.left, plot.bottom, "axis"))
    body.append(text(plot.left + plot.width / 2, plot.bottom + 104, x_label, anchor="middle"))
    body.append(text(80, plot.top + plot.height / 2, y_label, anchor="middle", rotate=-90))


def write_svg_and_pdf(
    figure_dir: Path,
    base_name: str,
    title: str,
    description: str,
    body: list[str],
) -> None:
    svg_path = figure_dir / f"{base_name}.svg"
    pdf_path = figure_dir / f"{base_name}.pdf"
    changed = write_if_changed(svg_path, svg_document(title, description, body))
    if changed or not pdf_path.exists():
        convert_to_pdf(svg_path, pdf_path)


def write_wrapper(
    path: Path,
    pdf_name: str,
    report: Path,
    caption: str,
    label: str,
    extra: str | None = None,
) -> None:
    details = f"; {extra}" if extra else ""
    write_if_changed(
        path,
        "\n".join(
            [
                f"% Generated by scripts/generate-interaction-figures.py; source={report}; graphic={pdf_name}{details}",
                "\\begin{figure}[h]",
                "\\centering",
                f"\\includegraphics[width=\\linewidth]{{figures/{pdf_name}}}",
                f"\\caption{{{caption}}}",
                f"\\label{{{label}}}",
                "\\end{figure}",
                "",
            ]
        ),
    )


def convert_to_pdf(svg_path: Path, pdf_path: Path) -> None:
    inkscape = shutil.which("inkscape")
    if not inkscape:
        raise SystemExit(
            "Inkscape is required to convert generated SVG figures to Wiley-preferred PDF files. "
            "Install Inkscape or add it to PATH before running make figures."
        )
    subprocess.run(
        [inkscape, str(svg_path), "--export-type=pdf", f"--export-filename={pdf_path}"],
        check=True,
    )


def svg_document(title: str, description: str, body: list[str]) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}px" height="{HEIGHT}px" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
            f"<title>{xml(title)}</title>",
            f"<desc>{xml(description)}</desc>",
            "<style>",
            "text { font-family: Helvetica, Arial, sans-serif; font-size: 34px; fill: #111; }",
            ".title { font-size: 46px; font-weight: 700; }",
            ".subtitle { font-size: 30px; fill: #444; }",
            ".small, .tick, .label { font-size: 28px; }",
            ".axis { stroke: #111; stroke-width: 5; fill: none; }",
            ".grid { stroke: #d8d8d8; stroke-width: 3; fill: none; }",
            ".segment, .point, .legend-swatch { stroke: #111; stroke-width: 2; }",
            ".series-primary { stroke: #111; stroke-width: 8; fill: none; }",
            ".series-secondary { stroke: #777; stroke-width: 8; fill: none; stroke-dasharray: 24 18; }",
            "</style>",
            '<rect width="100%" height="100%" fill="#fff"/>',
            *body,
            "</svg>",
            "",
        ]
    )


def title_block(title: str, subtitle: str) -> list[str]:
    return [
        text(70, 72, title, anchor="start", css_class="title"),
        text(70, 122, subtitle, anchor="start", css_class="subtitle"),
    ]


def rect(x: float, y: float, width: float, height: float, fill: str, css_class: str) -> str:
    return (
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(width)}" height="{num(height)}" '
        f'fill="{fill}" class="{css_class}"/>'
    )


def line(x1: float, y1: float, x2: float, y2: float, css_class: str) -> str:
    return f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" y2="{num(y2)}" class="{css_class}"/>'


def polyline(points: list[tuple[float, float]], css_class: str) -> str:
    joined = " ".join(f"{num(x)},{num(y)}" for x, y in points)
    return f'<polyline points="{joined}" class="{css_class}"/>'


def text(
    x: float,
    y: float,
    value: str,
    anchor: str,
    css_class: str | None = None,
    rotate: int | None = None,
) -> str:
    class_attr = f' class="{css_class}"' if css_class else ""
    transform = f' transform="rotate({rotate} {num(x)} {num(y)})"' if rotate is not None else ""
    return (
        f'<text x="{num(x)}" y="{num(y)}" text-anchor="{anchor}"{class_attr}{transform}>'
        f"{xml(value)}</text>"
    )


def scale(value: float, max_value: float) -> float:
    if max_value <= 0.0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def as_float(row_value: str) -> float:
    return float(row_value)


def num(value: float) -> str:
    if abs(value - round(value)) < 0.01:
        return str(int(round(value)))
    return f"{value:.1f}"


def xml(value: str) -> str:
    return html.escape(value, quote=True)


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
