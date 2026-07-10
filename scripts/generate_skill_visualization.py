from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SKILL_DIR = ROOT / "skills" / "harness-engineering-patterns"
DEFAULT_OUTPUT = ROOT / "harness-engineering-patterns.html"
CELL_ORDER = ["chain", "routing", "parallel", "orchestration", "loop", "hierarchy"]
PROVENANCE_LABELS = {
    "paper_v2": "Paper v2 / 论文 v2",
    "paper_blank": "Paper blank / 论文空白",
    "local_extension": "Local extension / 本地扩展",
    "local_seed": "Local seed / 本地种子",
}
MATURITY_LABELS = {
    "seed": "Seed / 种子",
    "draft": "Draft / 草案",
    "validated": "Validated / 已验证",
    "operational": "Operational / 运行中",
}


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def load_registry(skill_dir: pathlib.Path) -> dict[str, Any]:
    return json.loads(read_text(skill_dir / "references" / "registry.json"))


def registry_axes(
    registry: dict[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    vertical_axes = [
        {
            "id": axis["id"],
            "key": axis["key"],
            "en": axis["name_en"],
            "zh": axis["name_zh"],
            "question": f"{axis['question_en']} / {axis['question_zh']}",
            "fit": f"{axis['fit_en']} / {axis['fit_zh']}",
            "boundary": f"{axis['boundary_en']} / {axis['boundary_zh']}",
        }
        for axis in registry["capabilities"]
    ]
    horizontal_axes = [
        {
            "id": mode["id"],
            "key": mode["key"],
            "en": mode["name_en"],
            "zh": mode["name_zh"],
            "alias": f"{mode['alias_en']} / {mode['alias_zh']}",
            "fit": f"{mode['fit_en']} / {mode['fit_zh']}",
            "boundary": f"{mode['boundary_en']} / {mode['boundary_zh']}",
        }
        for mode in registry["topologies"]
    ]
    return vertical_axes, horizontal_axes


def registry_matrix(registry: dict[str, Any]) -> list[dict[str, str]]:
    capabilities = {axis["id"]: axis for axis in registry["capabilities"]}
    topologies = {mode["id"]: mode for mode in registry["topologies"]}
    matrix = []
    for cell in registry["cells"]:
        capability = capabilities[cell["capability_ref"]]
        topology = topologies[cell["topology_ref"]]
        status = "named" if cell["status"] == "named" else "extension"
        matrix.append(
            {
                "id": cell["id"],
                "coordinate": cell["coordinate"],
                "cell_key": cell["cell_key"],
                "capability_key": capability["key"],
                "capability": f"{capability['name_en']} / {capability['name_zh']}",
                "capability_en": capability["name_en"],
                "capability_zh": capability["name_zh"],
                "mode_key": topology["key"],
                "pattern_ref": cell["pattern_ref"],
                "pattern": f"{cell['local_name_en']} / {cell['local_name_zh']}",
                "status": status,
                "source_kind": cell["source_kind"],
                "maturity": cell["maturity"],
                "diagnostic_use": (
                    f"{cell['diagnostic_use_en']} / {cell['diagnostic_use_zh']}"
                ),
                "href": (
                    "skills/harness-engineering-patterns/" + cell["design_path"]
                ),
                "observability_href": (
                    "skills/harness-engineering-patterns/"
                    + cell["observability_path"]
                ),
            }
        )
    return matrix


def split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def is_table_separator(row: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in row)


def parse_named_table_rows(text: str, first_header: str) -> list[list[str]]:
    rows: list[list[str]] = []
    in_table = False
    for line in text.splitlines():
        if not line.startswith("|"):
            if in_table:
                break
            continue
        cells = split_markdown_row(line)
        if not in_table:
            if cells and cells[0] == first_header:
                in_table = True
            continue
        if is_table_separator(cells):
            continue
        rows.append(cells)
    return rows


def parse_axes(skill_dir: pathlib.Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    text = read_text(skill_dir / "references" / "axes.md")
    vertical_rows = parse_named_table_rows(text.split("## Horizontal Axis", 1)[0], "Key")
    horizontal_text = text.split("## Horizontal Axis", 1)[1].split("## Selection Heuristics", 1)[0]
    horizontal_rows = parse_named_table_rows(horizontal_text, "Key")

    vertical_axes = [
        {
            "key": row[0],
            "zh": row[1],
            "en": row[2],
            "question": row[3],
            "fit": row[4],
            "boundary": row[5],
        }
        for row in vertical_rows
    ]
    horizontal_axes = [
        {
            "key": row[0],
            "zh": row[1],
            "en": row[2],
            "alias": row[3],
            "fit": row[4],
            "boundary": row[5],
        }
        for row in horizontal_rows
    ]
    return vertical_axes, horizontal_axes


def parse_matrix(skill_dir: pathlib.Path) -> list[dict[str, str]]:
    text = read_text(skill_dir / "references" / "matrix-index.md")
    section = text.split("## Initial Matrix", 1)[1].split("## Reading A Cell", 1)[0]
    rows = parse_named_table_rows(section, "Capability / 能力")
    matrix: list[dict[str, str]] = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for row in rows:
        capability_label = row[0]
        capability_en, capability_zh = split_label(capability_label)
        capability_key = capability_en.lower()
        for mode_key, cell in zip(CELL_ORDER, row[1:]):
            match = link_pattern.search(cell)
            if not match:
                continue
            pattern_label, target = match.groups()
            file_path, separator, anchor = target.partition("#")
            cell_key = pathlib.PurePosixPath(file_path).stem
            if separator and "--" in anchor:
                cell_key = anchor.split("--", 1)[0]
            href = f"skills/harness-engineering-patterns/references/{file_path}"
            if separator:
                href = f"{href}#{anchor}"
            matrix.append(
                {
                    "cell_key": cell_key,
                    "capability_key": capability_key,
                    "capability": capability_label,
                    "capability_en": capability_en,
                    "capability_zh": capability_zh,
                    "mode_key": mode_key,
                    "pattern": pattern_label,
                    "href": href,
                }
            )
    return matrix


def split_label(label: str) -> tuple[str, str]:
    parts = [part.strip() for part in label.split("/", 1)]
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def parse_markdown_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        fields[key.strip()] = value.strip().rstrip(".")
    return fields


def parse_pattern_files(skill_dir: pathlib.Path) -> dict[str, dict[str, str]]:
    pattern_dir = skill_dir / "references" / "patterns"
    patterns: dict[str, dict[str, str]] = {}
    for path in sorted(pattern_dir.glob("*/*.md")):
        if path.name in {"cell.md", "trace.md"} or path.stem.endswith("-observability"):
            continue
        cell_key = path.stem
        text = read_text(path)
        title_match = re.search(r"^# (.+)$", text, re.M)
        if not title_match:
            continue
        fields = parse_markdown_fields(text)
        status_text = fields.get("状态 / Status", "")
        status = "extension" if re.search(r"扩展候选|Extension candidate", status_text, re.I) else "named"
        diagnostic_use = fields.get(
            "诊断用途 / Diagnostic Use",
            fields.get("适配信号 / Fit Signals", "Extension candidate / 扩展候选"),
        )
        patterns[cell_key] = {
            "pattern": title_match.group(1).strip(),
            "status": status,
            "diagnostic_use": diagnostic_use,
            "source": path.relative_to(skill_dir).as_posix(),
        }
    return patterns


def parse_observability_files(skill_dir: pathlib.Path) -> dict[str, dict[str, str]]:
    pattern_dir = skill_dir / "references" / "patterns"
    observability: dict[str, dict[str, str]] = {}
    for path in sorted(pattern_dir.glob("*/*-observability.md")):
        cell_key = path.stem.removesuffix("-observability")
        text = read_text(path)
        title_match = re.search(r"^# (.+)$", text, re.M)
        source = path.relative_to(skill_dir).as_posix()
        observability[cell_key] = {
            "title": title_match.group(1).strip() if title_match else path.stem,
            "source": source,
            "href": f"skills/harness-engineering-patterns/{source}",
        }
    return observability


def parse_cell_guides(skill_dir: pathlib.Path) -> dict[str, dict[str, str]]:
    pattern_dir = skill_dir / "references" / "patterns"
    guides: dict[str, dict[str, str]] = {}
    for path in sorted(pattern_dir.glob("*/cell.md")):
        text = read_text(path)
        title_match = re.search(r"^# (.+)$", text, re.M)
        cell_key = path.parent.name
        source = path.relative_to(skill_dir).as_posix()
        guides[cell_key] = {
            "title": title_match.group(1).strip() if title_match else path.stem,
            "source": source,
            "href": f"skills/harness-engineering-patterns/{source}",
        }
    return guides


def parse_traces(skill_dir: pathlib.Path) -> dict[str, dict[str, str]]:
    pattern_dir = skill_dir / "references" / "patterns"
    traces: dict[str, dict[str, str]] = {}
    for path in sorted(pattern_dir.glob("*/trace.md")):
        text = read_text(path)
        title_match = re.search(r"^# (.+)$", text, re.M)
        cell_key = path.parent.name
        source = path.relative_to(skill_dir).as_posix()
        traces[cell_key] = {
            "title": title_match.group(1).strip() if title_match else path.stem,
            "source": source,
            "href": f"skills/harness-engineering-patterns/{source}",
        }
    return traces


def parse_selection_card(skill_dir: pathlib.Path) -> dict[str, str]:
    path = skill_dir / "references" / "pattern-selection-card.md"
    text = read_text(path)
    title_match = re.search(r"^# (.+)$", text, re.M)
    source = path.relative_to(skill_dir).as_posix()
    return {
        "title": title_match.group(1).strip() if title_match else "Pattern Selection Card / 模式选型卡",
        "source": source,
        "href": f"skills/harness-engineering-patterns/{source}",
    }


def source_files(skill_dir: pathlib.Path) -> list[pathlib.Path]:
    references = skill_dir / "references"
    files = [
        references / "registry.json",
        references / "axes.md",
        references / "matrix-index.md",
        references / "pattern-catalog.md",
        references / "pattern-selection-card.md",
    ]
    files.extend(sorted((references / "patterns").glob("*/*.md")))
    return files


def source_hash(skill_dir: pathlib.Path) -> str:
    digest = hashlib.sha256()
    for path in source_files(skill_dir):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def load_skill_data(skill_dir: pathlib.Path = DEFAULT_SKILL_DIR) -> dict[str, Any]:
    skill_dir = pathlib.Path(skill_dir)
    registry = load_registry(skill_dir)
    vertical_axes, horizontal_axes = registry_axes(registry)
    matrix = registry_matrix(registry)
    patterns = parse_pattern_files(skill_dir)
    observability = parse_observability_files(skill_dir)
    cell_guides = parse_cell_guides(skill_dir)
    traces = parse_traces(skill_dir)
    selection_card = parse_selection_card(skill_dir)

    for axis in vertical_axes:
        guide = cell_guides.get(axis["key"])
        if guide:
            axis["guide_href"] = guide["href"]
        trace = traces.get(axis["key"])
        if trace:
            axis["trace_href"] = trace["href"]

    summary = {
        "vertical_axes": len(vertical_axes),
        "horizontal_axes": len(horizontal_axes),
        "matrix_cells": len(matrix),
        "named_patterns": sum(1 for cell in matrix if cell["status"] == "named"),
        "extension_candidates": sum(1 for cell in matrix if cell["status"] == "extension"),
    }
    return {
        "title": "Harness Engineering Patterns",
        "registry": registry,
        "vertical_axes": vertical_axes,
        "horizontal_axes": horizontal_axes,
        "matrix": matrix,
        "patterns": patterns,
        "observability": observability,
        "cell_guides": cell_guides,
        "traces": traces,
        "selection_card": selection_card,
        "summary": summary,
        "source_hash": source_hash(skill_dir),
    }


def render_html(data: dict[str, Any]) -> str:
    vertical_axes = data["vertical_axes"]
    horizontal_axes = data["horizontal_axes"]
    matrix_by_axis = {
        (cell["capability_key"], cell["mode_key"]): cell for cell in data["matrix"]
    }
    summary = data["summary"]

    axis_cards = "\n".join(render_axis_card(axis) for axis in vertical_axes)
    mode_cards = "\n".join(render_mode_card(mode) for mode in horizontal_axes)
    selection_flow = render_selection_flow(data["selection_card"])
    matrix_rows = "\n".join(
        render_matrix_row(axis, horizontal_axes, matrix_by_axis) for axis in vertical_axes
    )

    return f"""<!doctype html>
<html lang="zh-CN" data-source-hash="{escape_attr(data['source_hash'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3' fill='%230f766e'/%3E%3Cpath d='M4 4h8v2H6v2h5v2H6v2H4z' fill='white'/%3E%3C/svg%3E">
  <title>Harness Engineering Patterns</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f2933;
      --muted: #52606d;
      --line: #d9e2ec;
      --surface: #ffffff;
      --paper: #f7f8fa;
      --accent: #0f766e;
      --accent-2: #7c3aed;
      --warn: #b45309;
      --ok-bg: #e6f4f1;
      --maybe-bg: #fff4df;
      --soft: #eef2f6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background: var(--paper);
      line-height: 1.5;
    }}
    main {{
      width: min(1440px, calc(100% - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: end;
      padding: 4px 0 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 8px 0 0;
      color: var(--muted);
      max-width: 860px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(92px, 1fr));
      gap: 8px;
      min-width: 520px;
    }}
    .metric {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
    }}
    .metric strong {{
      display: block;
      font-size: 22px;
      line-height: 1;
    }}
    .metric span {{
      display: block;
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
    }}
    .axis-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 150px;
    }}
    .axis-title {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: baseline;
      margin-bottom: 8px;
    }}
    .axis-title strong {{
      font-size: 15px;
    }}
    .axis-title code {{
      color: var(--accent);
      background: var(--soft);
      border-radius: 4px;
      padding: 2px 5px;
      font-size: 12px;
    }}
    .axis-card p {{
      margin: 6px 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .guide-link {{
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
    }}
    .axis-links {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .guide-link:hover {{ text-decoration: underline; }}
    .selection-flow {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .flow-title {{
      margin: 0 0 8px;
      font-size: 15px;
      font-weight: 700;
    }}
    .flow-copy {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .flow-link {{
      color: var(--accent);
      font-weight: 700;
      text-decoration: none;
      white-space: nowrap;
    }}
    .flow-link:hover {{ text-decoration: underline; }}
    .matrix-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
    }}
    .matrix-note {{
      margin: -4px 0 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1120px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      border-right: 1px solid var(--line);
      vertical-align: top;
      padding: 10px;
    }}
    th:last-child, td:last-child {{ border-right: 0; }}
    tr:last-child td {{ border-bottom: 0; }}
    th {{
      background: #edf2f7;
      text-align: left;
      font-size: 13px;
      position: sticky;
      top: 0;
      z-index: 1;
    }}
    .row-head {{
      width: 150px;
      background: #f8fafc;
      font-weight: 700;
    }}
    .cell {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-height: 118px;
    }}
    .pattern {{
      color: var(--ink);
      text-decoration: none;
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .pattern:hover {{ text-decoration: underline; }}
    .tag {{
      display: inline-flex;
      width: fit-content;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 700;
    }}
    .tag.named {{
      background: var(--ok-bg);
      color: var(--accent);
    }}
    .tag.extension {{
      background: var(--maybe-bg);
      color: var(--warn);
    }}
    .use {{
      color: var(--muted);
      font-size: 12px;
    }}
    .cell-links {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .cell-link {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-decoration: none;
    }}
    .cell-link:hover {{ text-decoration: underline; }}
    footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 820px) {{
      main {{ width: min(100% - 20px, 1440px); }}
      header {{ grid-template-columns: 1fr; }}
      .selection-flow {{ grid-template-columns: 1fr; }}
      .summary {{ min-width: 0; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <section>
        <h1>Harness Engineering Patterns / Harness 工程模式</h1>
        <p class="subtitle">Current skill visualization generated from the capability axis, orchestration mode axis, grouped cell folders, trace files, dedicated pattern files, and matrix index. / 根据当前 Skill 的纵轴能力、横轴模式、按 cell 分组的文件夹、追踪文件、独立模式文件和交织表生成。</p>
      </section>
      <section class="summary" aria-label="Matrix summary">
        {render_metric(summary['vertical_axes'], 'Vertical axes / 纵轴')}
        {render_metric(summary['horizontal_axes'], 'Horizontal modes / 横轴')}
        {render_metric(summary['matrix_cells'], 'Matrix cells / 交织点')}
        {render_metric(summary['named_patterns'], 'Named / 已命名')}
        {render_metric(summary['extension_candidates'], 'Extensions / 扩展候选')}
      </section>
    </header>

    {selection_flow}

    <h2>Vertical Capabilities / 纵轴能力</h2>
    <section class="grid">{axis_cards}</section>

    <h2>Horizontal Modes / 横轴模式</h2>
    <section class="grid">{mode_cards}</section>

    <h2>Intersection Matrix / 交织表</h2>
    <p class="matrix-note">Each cell links to two markdown files: Design Pattern / 设计模式 and Observability Metrics / 可观测性指标. / 每个交织点链接两个 Markdown 文件：设计模式与可观测性指标。</p>
    <section class="matrix-wrap">
      <table>
        <thead>
          <tr>
            <th>Capability / 能力</th>
            {''.join(f"<th>{escape(mode['en'])} / {escape(mode['zh'])}</th>" for mode in horizontal_axes)}
          </tr>
        </thead>
        <tbody>{matrix_rows}</tbody>
      </table>
    </section>

    <footer>Source hash / 源哈希: {escape(data['source_hash'])}</footer>
  </main>
</body>
</html>
"""


def render_metric(value: int, label: str) -> str:
    return f'<div class="metric"><strong>{value}</strong><span>{escape(label)}</span></div>'


def render_selection_flow(card: dict[str, str]) -> str:
    return f"""
    <h2>Pattern Selection Card / 模式选型卡</h2>
    <section class="selection-flow" aria-label="Pattern selection card">
      <div>
        <p class="flow-title">Trace Insert / Trace 插入 -> ASSESS / 评估 -> ROUTE / 判拓扑 -> SELECT / 查矩阵 -> Plan / 规划</p>
        <p class="flow-copy">Trace is inserted first to complete engineering node evidence; the card runs only after the node is ready. / 先插入 Trace 补全工程节点证据，节点就绪后再运行选型卡。</p>
      </div>
      <a class="flow-link" href="{escape_attr(card['href'])}">{escape(card['source'])}</a>
    </section>"""


def render_axis_card(axis: dict[str, str]) -> str:
    links = []
    if axis.get("guide_href"):
        links.append(f'<a class="guide-link" href="{escape_attr(axis["guide_href"])}">Guide / 导论</a>')
    if axis.get("trace_href"):
        links.append(f'<a class="guide-link" href="{escape_attr(axis["trace_href"])}">Trace / 追踪</a>')
    guide_link = f'<p class="axis-links">{" ".join(links)}</p>' if links else ""
    return f"""
      <article class="axis-card">
        <div class="axis-title"><strong>{escape(axis['en'])} / {escape(axis['zh'])}</strong><code>{escape(axis['key'])}</code></div>
        <p>{escape(axis.get('question', ''))}</p>
        <p>{escape(axis.get('fit', ''))}</p>
        {guide_link}
      </article>"""


def render_mode_card(mode: dict[str, str]) -> str:
    return f"""
      <article class="axis-card">
        <div class="axis-title"><strong>{escape(mode['en'])} / {escape(mode['zh'])}</strong><code>{escape(mode['key'])}</code></div>
        <p>{escape(mode.get('alias', ''))}</p>
        <p>{escape(mode.get('fit', ''))}</p>
      </article>"""


def render_matrix_row(
    axis: dict[str, str],
    horizontal_axes: list[dict[str, str]],
    matrix_by_axis: dict[tuple[str, str], dict[str, str]],
) -> str:
    cells = []
    for mode in horizontal_axes:
        cell = matrix_by_axis[(axis["key"], mode["key"])]
        cells.append(render_matrix_cell(cell))
    return f"""
          <tr>
            <td class="row-head">{escape(axis['en'])}<br>{escape(axis['zh'])}</td>
            {''.join(cells)}
          </tr>"""


def render_matrix_cell(cell: dict[str, str]) -> str:
    status = cell["status"]
    status_label = "Named / 已命名" if status == "named" else "Extension / 扩展"
    provenance = PROVENANCE_LABELS.get(cell.get("source_kind", ""), "Unknown / 未知")
    maturity = MATURITY_LABELS.get(cell.get("maturity", ""), "Unknown / 未知")
    observability_link = ""
    if cell.get("observability_href"):
        observability_link = (
            f'<a class="cell-link" href="{escape_attr(cell["observability_href"])}">'
            "Observability / 可观测性</a>"
        )
    return f"""
            <td>
              <div class="cell">
                <span class="tag {escape_attr(status)}">{escape(status_label)}</span>
                <a class="pattern" href="{escape_attr(cell['href'])}">{escape(cell['pattern'])}</a>
                <div class="cell-links"><a class="cell-link" href="{escape_attr(cell['href'])}">Design Pattern / 设计模式</a>{observability_link}</div>
                <div class="use"><strong>Provenance / 来源:</strong> {escape(provenance)}</div>
                <div class="use"><strong>Maturity / 成熟度:</strong> {escape(maturity)}</div>
                <div class="use">{escape(cell['diagnostic_use'])}</div>
              </div>
            </td>"""


def escape(value: str) -> str:
    return html.escape(str(value), quote=False)


def escape_attr(value: str) -> str:
    return html.escape(str(value), quote=True)


def write_visualization(skill_dir: pathlib.Path = DEFAULT_SKILL_DIR, output: pathlib.Path = DEFAULT_OUTPUT) -> pathlib.Path:
    data = load_skill_data(skill_dir)
    output = pathlib.Path(output)
    html_text = "\n".join(line.rstrip() for line in render_html(data).splitlines()) + "\n"
    output.write_text(html_text, encoding="utf-8", newline="\n")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Harness Engineering Patterns HTML visualization.")
    parser.add_argument("--skill-dir", type=pathlib.Path, default=DEFAULT_SKILL_DIR)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = write_visualization(args.skill_dir, args.output)
    print(f"Generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
