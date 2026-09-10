"""Sync Fan-Out/Gather specification views / 同步扇出聚合规格视图。

Usage / 用法: python sync_collaboration_gather_docs.py [skill_dir] [--write]
Workflow / 流程: Validate source identities, complete mappings and fingerprints;
render shared contract, workflow, metrics and acceptance cases into marked blocks.
/ 核验来源身份、完整映射与指纹，在标记区块生成共享契约、流程、指标与用例。
Constraints / 约束: Write only generated blocks after full preflight. No business
execution, metric calculation, source rewriting or implementation promotion.
/ 完整预检后仅写生成区块，不执行业务、不计算指标、不改来源、不晋升实现状态。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


DESIGN = 'references/patterns/collaboration/collaboration-parallel.md'
PROBE = 'references/patterns/collaboration/collaboration-parallel-observability.md'
CONTRACT = 'references/collaboration-gather-contract.md'
SOURCE_MAP = 'references/collaboration-gather-source-map.json'
GROUPS = {
    'execution_nodes': ('GN', 0, 11, 'execution'),
    'probe_nodes': ('GP', 0, 11, 'probe'),
    'metrics': ('GM', 1, 17, 'probe'),
    'execution_cases': ('GET', 1, 16, 'execution'),
    'probe_cases': ('GPT', 1, 20, 'probe'),
}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _end(lines: list[str], start: int) -> int:
    return next((i - 1 for i in range(start + 1, len(lines) + 1)
                 if re.match(r'^##(?:#)? ', lines[i - 1])), len(lines))


def source_rows(text: str, group: str) -> list[dict]:
    """Discover the original inventory, never infer it from the map.
    / 从原文发现完整清单，不从被测映射反推全集。
    """
    lines = text.splitlines()
    rows = []
    for number, line in enumerate(lines, 1):
        extra = {}
        end = number
        if group == 'execution_nodes':
            match = re.match(r'^### 7\.\d+ (N\d{2})：(.+)$', line)
            if match:
                extra['name_zh'] = match[2]
                end = _end(lines, number)
        elif group == 'probe_nodes':
            match = re.match(r'^\s*(?:→ )?(P\d{2}) (.+)$', line)
            if match:
                extra['name_zh'] = match[2]
        elif group == 'metrics':
            heading = re.match(r'^### (M0[1-4])：(.+)$', line)
            table = re.match(r'^\| (M\d{2}) (.+?) \| (.+) \| (.+) \|$', line)
            if table and int(table[1][1:]) < 5:
                table = None  # Exclude repeated M01 in the fixture comparison table.
                # / 排除固定样例对比表中重复展示的 M01。
            match = heading or table
            if match:
                extra['name_zh'] = match[2]
                if heading:
                    end = _end(lines, number)
                    excerpt = '\n'.join(lines[number - 1:end])
                    extra['formula_zh'] = re.findall(r'```text\n(.*?)\n```', excerpt, re.S)[0]
                else:
                    extra.update(formula_zh=match[3], boundary_zh=match[4])
        else:
            prefix = 'E' if group == 'execution_cases' else 'P'
            match = re.match(r'^\| (' + prefix + r'\d{2}) \| (.+?) \| (.+) \|$', line)
            if match:
                extra.update(condition_zh=match[2], expected_zh=match[3])
        if match:
            rows.append(dict(source_id=match[1], source_line=number, source_end_line=end,
                             excerpt_sha256=_digest('\n'.join(lines[number - 1:end])), **extra))
    return rows


def _read_source(skill_dir: Path, registry: dict | None = None) -> tuple[dict, list[str]]:
    errors = []
    registry = registry if registry is not None else json.loads(
        (skill_dir / 'references/registry.json').read_text(encoding='utf-8'))
    cell = next(item for item in registry['cells'] if item['id'] == 'CELL_COLLABORATION_PARALLEL')
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    expected_spec = dict(version='0.1.0', source_contract_version='0.1.0', status='draft',
                         implementation_status='specification_only', source_map_reference=SOURCE_MAP,
                         interaction_contract_reference=CONTRACT)
    if (cell['pattern_ref'] != 'PATTERN_0044' or cell['maturity'] != 'draft'
            or cell['design_path'] != DESIGN or cell['observability_path'] != PROBE
            or cell.get('gather_specification') != expected_spec):
        errors.append('gather_registry: identity, maturity or dedicated specification drift')
    if (source['pattern_ref'] != 'PATTERN_0044' or source['cell_ref'] != cell['id']
            or source['version'] != '0.1.0' or source['source_contract_version'] != '0.1.0'
            or source['implementation_status'] != 'specification_only'
            or source['source_pattern_alias'] != 'PATTERN_GATHER_0001'
            or source['source_skill_aliases'] != ['SKILL_GATHER_0001', 'SKILL_GATHER_0002']):
        errors.append('gather_source: identity, protocol or implementation claim drift')
    if [item['id'] for item in source['sources']] != ['execution', 'probe']:
        errors.append('gather_source: expected exactly one execution and one probe source')
    for field in ['name_en', 'name_zh', 'description_en', 'description_zh']:
        if not source.get(field):
            errors.append('gather_source: missing bilingual metadata: ' + field)
    snapshots = {}
    evidence_root = (skill_dir.parent.parent / '.harness-analysis').resolve()
    for item in source['sources']:
        path = (skill_dir.parent.parent / item['snapshot_path']).resolve()
        if not path.is_relative_to(evidence_root):
            raise ValueError('gather_source: snapshot must stay inside project evidence directory')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            errors.append('gather_source: snapshot digest drift: ' + item['id'])
        if item['version'] != '0.1.0' or not item.get('name_en') or not item.get('name_zh'):
            errors.append('gather_source: unsupported version or missing bilingual source metadata')
        snapshots[item['id']] = data.decode('utf-8').replace('\r\n', '\n')
    contracts = []
    for text in snapshots.values():
        begin = '<!-- 共享协议开始：扇出聚合补数协议/0.1.0 -->'
        end = '<!-- 共享协议结束：扇出聚合补数协议/0.1.0 -->'
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError('gather_source: missing or repeated source protocol block')
        contracts.append(text.split(begin, 1)[1].split(end, 1)[0].strip())
    if (len(contracts) != 2 or contracts[0] != contracts[1]
            or _digest(contracts[0]) != source['shared_source_contract_sha256']):
        errors.append('gather_source: supplied shared protocols differ or fingerprint changed')
    for group, (prefix, first, count, sid) in GROUPS.items():
        rows = source[group]
        original = source_rows(snapshots[sid], group)
        if [row['id'] for row in rows] != [f'{prefix}{i:02d}' for i in range(first, first + count)]:
            errors.append('gather_source: count or stable ID drift: ' + group)
        if len(original) != count or len(rows) != len(original):
            errors.append('gather_source: incomplete source inventory: ' + group)
        for row, expected in zip(rows, original):
            if row['source_ref'] != sid or any(row.get(key) != value for key, value in expected.items()):
                errors.append('gather_source: original mapping or definition drift: ' + row['id'])
            if not row.get('summary_en') or (group == 'metrics' and not row.get('name_en')):
                errors.append('gather_source: missing English instructions: ' + row['id'])
            if (group.endswith('_cases') or group == 'metrics') and row.get('integration_status') != 'pending':
                errors.append('gather_source: unsupported integration claim: ' + row['id'])
            if group == 'metrics' and row.get('implementation') != 'specification_only':
                errors.append('gather_source: unsupported metric implementation: ' + row['id'])
    return source, errors


def _cell(text: str) -> str:
    return text.replace('|', '&#124;').replace('\n', '<br>')


def _table(rows: list[dict], group: str) -> str:
    if group == 'metrics':
        headings = ['ID / 编号', 'Metric / 指标', 'Definition and boundary / 定义与边界', 'Original formula and limits / 原口径与限制']
        values = [[row['id'] + ' / ' + row['source_id'], row['name_en'] + ' / ' + row['name_zh'],
                   row['summary_en'], row['formula_zh'] + ('；' + row['boundary_zh'] if row.get('boundary_zh') else '')]
                  for row in rows]
    elif group.endswith('_cases'):
        headings = ['ID / 编号', 'Scenario / 场景', 'Required outcome / 必需结果']
        values = [[row['id'] + ' / ' + row['source_id'], row['condition_zh'],
                   row['summary_en'] + ' / ' + row['expected_zh']] for row in rows]
    else:
        headings = ['ID / 编号', 'Node / 节点', 'Required behavior / 必需行为']
        values = [[row['id'] + ' / ' + row['source_id'], row['name_zh'], row['summary_en']] for row in rows]
    return '\n'.join(['| ' + ' | '.join(headings) + ' |',
                      '| ' + ' | '.join(['---'] * len(headings)) + ' |']
                     + ['| ' + ' | '.join(_cell(value) for value in row) + ' |' for row in values])


def views(skill_dir: Path) -> dict[str, dict[str, str]]:
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    contract = (skill_dir / CONTRACT).read_text(encoding='utf-8').split('\n', 1)[1].strip()
    return {
        DESIGN: dict(execution_nodes=_table(source['execution_nodes'], 'execution_nodes'),
                     contract=contract, execution_cases=_table(source['execution_cases'], 'execution_cases')),
        PROBE: dict(probe_nodes=_table(source['probe_nodes'], 'probe_nodes'), contract=contract,
                    metrics=_table(source['metrics'], 'metrics'), probe_cases=_table(source['probe_cases'], 'probe_cases')),
    }


def _block(section: str, text: str) -> str:
    return f'<!-- gather:{section}:start -->\n{text}\n<!-- gather:{section}:end -->'


def _pattern(section: str) -> str:
    return re.escape(f'<!-- gather:{section}:start -->') + r'.*?' + re.escape(f'<!-- gather:{section}:end -->')


def validate_gather_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Verify specification fidelity only / 仅验证规格保真，不证明业务执行。"""
    try:
        _, errors = _read_source(skill_dir, registry)
        for relative, sections in views(skill_dir).items():
            text = (skill_dir / relative).read_text(encoding='utf-8')
            if '\ufffd' in text:
                errors.append('gather_view: invalid replacement character: ' + relative)
            for section, content in sections.items():
                if re.findall(_pattern(section), text, re.S) != [_block(section, content)]:
                    errors.append(f'gather_view: missing, repeated or stale block: {relative} {section}')
        return errors
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        return ['gather_specification: ' + str(error)]


def sync(skill_dir: Path) -> None:
    """Preflight all sources and markers before writing either peer.
    / 双方写入前先完整核验所有来源与标记。
    """
    _, errors = _read_source(skill_dir)
    if errors:
        raise ValueError('\n'.join(errors))
    pending = []
    for relative, sections in views(skill_dir).items():
        path = skill_dir / relative
        text = path.read_text(encoding='utf-8')
        for section, content in sections.items():
            text, count = re.subn(_pattern(section), lambda _: _block(section, content), text, flags=re.S)
            if count != 1:
                raise ValueError(f'Expected one generated block / 必须有一个生成区块: {relative} {section}')
        pending.append((path, text))
    for path, text in pending:
        path.write_text(text, encoding='utf-8', newline='\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        sync(args.skill_dir)
    errors = validate_gather_assets(args.skill_dir)
    for error in errors:
        print(error)
    print(f'Gather validation / 扇出聚合校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
