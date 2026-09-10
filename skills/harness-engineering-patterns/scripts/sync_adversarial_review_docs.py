"""Sync Adversarial Review specifications / 同步对抗评审规格。

Usage / 用法: python sync_adversarial_review_docs.py [skill_dir] [--write]
Workflow / 流程: Verify frozen sources and complete inventories, then render both
execution and observation views from the shared contract and source map.
/ 核对来源快照与完整清单，再从共享契约及来源映射生成执行和观测视图。
Constraints / 约束: Preflight before writing; preserve authored prose. This tool
validates specifications, never executes reviews, calculates metrics or approves.
/ 写入前完整预检，保留手写内容；只校验规格，不执行评审、计算指标或批准。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


DESIGN = 'references/patterns/collaboration/collaboration-loop.md'
PROBE = 'references/patterns/collaboration/collaboration-loop-observability.md'
CONTRACT = 'references/adversarial-review-contract.md'
SOURCE_MAP = 'references/adversarial-review-source-map.json'
GROUPS = {
    'execution_nodes': ('RN', 0, 13, 'execution'),
    'probe_nodes': ('RP', 0, 12, 'probe'),
    'metrics': ('RM', 1, 27, 'probe'),
    'execution_cases': ('RET', 1, 22, 'execution'),
    'probe_cases': ('RPT', 1, 22, 'probe'),
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def shared_contract(text: str) -> str:
    """Extract the shared source section / 提取原文内嵌共享契约。"""
    matches = re.findall(r'^## \d+\. 最小共享协议\n(.*?)(?=^## )', text, re.M | re.S)
    if len(matches) != 1:
        raise ValueError('Expected one shared source contract / 原文必须有一个共享契约')
    return matches[0].strip()


def source_rows(text: str, group: str) -> list[dict]:
    """Discover the original inventory, independent of the mapped inventory.
    / 独立扫描原文清单，不能用待验证映射反推完整性。
    """
    patterns = {
        'execution_nodes': r'^\| (节点-\d{2})：(.+?) \| (.+?) \| (.+?) \| (.+?) \|$',
        'probe_nodes': r'^\| (探针-\d{2})：(.+?) \| (.+?) \| (.+?) \| (.+?) \|$',
        'metrics': r'^\| (指标-\d{2}) (.+?) \| (.+?) \| (.+?) \|$',
        'execution_cases': r'^\| (验收-\d{2}) \| (.+?) \| (.+?) \|$',
        'probe_cases': r'^\| (探针验收-\d{2}) \| (.+?) \| (.+?) \|$',
    }
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(patterns[group], line)
        if not match:
            continue
        row = dict(source_id=match[1], source_line=number,
                   source_end_line=number, excerpt_sha256=digest(line))
        if group.endswith('_nodes'):
            row.update(name_zh=match[2], action_zh=match[3], output_zh=match[4], recovery_zh=match[5])
        elif group == 'metrics':
            row.update(name_zh=match[2], formula_zh=match[3], boundary_zh=match[4])
        else:
            row.update(condition_zh=match[2], expected_zh=match[3])
        rows.append(row)
    return rows


def _read_source(skill_dir: Path, registry: dict | None = None) -> tuple[dict, list[str]]:
    errors = []
    registry = registry if registry is not None else json.loads(
        (skill_dir / 'references/registry.json').read_text(encoding='utf-8'))
    cell = next(item for item in registry['cells'] if item['id'] == 'CELL_COLLABORATION_LOOP')
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    expected_spec = dict(version='0.1.0', source_contract_version='0.1.0', status='draft',
                         implementation_status='specification_only', source_map_reference=SOURCE_MAP,
                         interaction_contract_reference=CONTRACT)
    if (cell['pattern_ref'] != 'PATTERN_0045' or cell['maturity'] != 'draft'
            or cell['design_path'] != DESIGN or cell['observability_path'] != PROBE
            or cell.get('review_specification') != expected_spec):
        errors.append('review_registry: identity, maturity or specification registration drift')
    expected = dict(version='0.1.0', pattern_ref='PATTERN_0045', cell_ref='CELL_COLLABORATION_LOOP',
                    source_contract_version='0.1.0', implementation_status='specification_only',
                    source_pattern_alias='PATTERN_REVIEW_0001',
                    source_skill_aliases=['SKILL_REVIEW_0001', 'SKILL_OBSERVABILITY_0001'])
    if any(source.get(key) != value for key, value in expected.items()):
        errors.append('review_source: identity or implementation status drift')
    for field in ('name_en', 'name_zh', 'description_en', 'description_zh'):
        if not source.get(field):
            errors.append('review_source: missing bilingual metadata: ' + field)
    if [item['id'] for item in source['sources']] != ['execution', 'probe']:
        raise ValueError('review_source: expected exactly one execution and one probe source')
    snapshots = {}
    evidence_root = (skill_dir.parent.parent / '.harness-analysis').resolve()
    for item in source['sources']:
        path = (skill_dir.parent.parent / item['snapshot_path']).resolve()
        if not path.is_relative_to(evidence_root):
            raise ValueError('review_source: snapshot outside project evidence directory')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            errors.append('review_source: snapshot digest drift: ' + item['id'])
        text = data.decode('utf-8-sig').replace('\r\n', '\n')
        skill_id = 'SKILL_REVIEW_0001' if item['id'] == 'execution' else 'SKILL_OBSERVABILITY_0001'
        if (item['version'] != '0.1.0' or not item.get('name_en') or not item.get('name_zh')
                or not re.search(r'^version: 0\.1\.0$', text, re.M)
                or not re.search(r'^skill_id: ' + skill_id + '$', text, re.M)):
            errors.append('review_source: source identity, version or bilingual metadata drift')
        snapshots[item['id']] = text
    contracts = [shared_contract(text) for text in snapshots.values()]
    if (contracts[0] != contracts[1]
            or digest(contracts[0]) != source['shared_source_contract_sha256']):
        errors.append('review_source: supplied shared protocols differ or fingerprint changed')
    for group, (prefix, first, count, sid) in GROUPS.items():
        rows = source[group]
        original = source_rows(snapshots[sid], group)
        if [row['id'] for row in rows] != [f'{prefix}{i:02d}' for i in range(first, first + count)]:
            errors.append('review_source: count or stable ID drift: ' + group)
        if len(original) != count or len(rows) != len(original):
            errors.append('review_source: incomplete source inventory: ' + group)
        for row, original_row in zip(rows, original):
            if row['source_ref'] != sid or any(row.get(key) != value for key, value in original_row.items()):
                errors.append('review_source: original mapping or definition drift: ' + row['id'])
            english_fields = ('summary_en',) if group.endswith('_cases') else ('name_en', 'summary_en')
            if any(not row.get(field) for field in english_fields):
                errors.append('review_source: missing English instructions: ' + row['id'])
            if row.get('integration_status') != 'pending':
                errors.append('review_source: unsupported integration claim: ' + row['id'])
            if group == 'metrics' and row.get('implementation') != 'specification_only':
                errors.append('review_source: unsupported metric implementation: ' + row['id'])
    return source, errors


def _cell(text: str) -> str:
    return text.replace('|', '&#124;').replace('\n', '<br>')


def _table(rows: list[dict], group: str) -> str:
    if group.endswith('_nodes'):
        headings = ['ID / 编号', 'Node / 节点', 'Action, output and recovery / 动作、产出与恢复']
        values = [[row['id'] + ' / ' + row['source_id'], row['name_en'] + ' / ' + row['name_zh'],
                   row['summary_en'] + '<br>' + row['action_zh'] + '<br>产出 / Output: '
                   + row['output_zh'] + '<br>恢复 / Recovery: ' + row['recovery_zh']] for row in rows]
    elif group == 'metrics':
        headings = ['ID / 编号', 'Metric / 指标', 'Definition and limits / 定义与边界']
        values = [[row['id'] + ' / ' + row['source_id'], row['name_en'] + ' / ' + row['name_zh'],
                   row['summary_en'] + '<br>' + row['formula_zh'] + '<br>' + row['boundary_zh']]
                  for row in rows]
    else:
        headings = ['ID / 编号', 'Scenario / 场景', 'Required outcome / 必需结果']
        values = [[row['id'] + ' / ' + row['source_id'], row['condition_zh'],
                   row['summary_en'] + ' / ' + row['expected_zh']] for row in rows]
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
    return f'<!-- review:{section}:start -->\n{text}\n<!-- review:{section}:end -->'


def _pattern(section: str) -> str:
    return re.escape(f'<!-- review:{section}:start -->') + r'.*?' + re.escape(f'<!-- review:{section}:end -->')


def _require_markers(text: str, section: str) -> None:
    if any(text.count(f'<!-- review:{section}:{edge} -->') != 1 for edge in ('start', 'end')):
        raise ValueError('review_view: missing or repeated marker: ' + section)


def validate_review_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Verify source fidelity, not deployed behavior / 验证来源保真，不证明部署行为。"""
    try:
        _, errors = _read_source(skill_dir, registry)
        for relative, sections in views(skill_dir).items():
            text = (skill_dir / relative).read_text(encoding='utf-8')
            if '\ufffd' in text:
                errors.append('review_view: invalid replacement character: ' + relative)
            for section, content in sections.items():
                _require_markers(text, section)
                if re.findall(_pattern(section), text, re.S) != [_block(section, content)]:
                    errors.append(f'review_view: stale block: {relative} {section}')
        return errors
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        return ['review_specification: ' + str(error)]


def sync(skill_dir: Path) -> None:
    """Preflight all sources and both views before any write.
    / 写入之前，完整预检来源及两份视图。
    """
    _, errors = _read_source(skill_dir)
    if errors:
        raise ValueError('\n'.join(errors))
    pending = []
    for relative, sections in views(skill_dir).items():
        path = skill_dir / relative
        text = path.read_text(encoding='utf-8')
        for section, content in sections.items():
            _require_markers(text, section)
            text, count = re.subn(_pattern(section), lambda _: _block(section, content), text, flags=re.S)
            if count != 1:
                raise ValueError(f'review_view: invalid marker order: {relative} {section}')
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
    errors = validate_review_assets(args.skill_dir)
    for error in errors:
        print(error)
    print(f'Review validation / 对抗评审校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
