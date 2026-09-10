"""Sync and validate hierarchy specification views / 同步并校验层级委派规格视图。

Usage / 用法: python sync_collaboration_hierarchy_docs.py [skill_dir] [--write]
Workflow / 流程: Read source map and canonical contract, render marked sections,
then verify identity, source fingerprints, mappings and implementation boundaries.
/ 读取来源映射与规范契约，生成标记区块，核验身份、来源指纹、映射与实现边界。
Constraints / 约束: Only marked sections are written. No runtime or business
state is changed; source acceptance cases remain pending host implementation.
/ 只写标记区块，不修改运行时或业务状态；来源验收用例仍待宿主实现。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


DESIGN = 'references/patterns/collaboration/collaboration-hierarchy.md'
PROBE = 'references/patterns/collaboration/collaboration-hierarchy-observability.md'
CONTRACT = 'references/collaboration-hierarchy-contract.md'
SOURCE_MAP = 'references/collaboration-hierarchy-source-map.json'
GROUPS = {
    'execution_nodes': ('HE', 11, 'execution', '执行'),
    'probe_nodes': ('HP', 7, 'probe', '观测'),
    'probe_catalog': ('HPR', 10, 'probe', '探针'),
    'metrics': ('HM', 22, 'probe', '指标'),
    'execution_cases': ('HET', 16, 'execution', '执行验收'),
    'probe_cases': ('HPT', 22, 'probe', '探针验收'),
}


def _cell(value: str) -> str:
    return value.replace('|', '&#124;').replace('\n', ' ')


def _table(rows: list[dict], group: str) -> str:
    if group == 'metrics':
        headings = ['ID / 编号', 'Metric / 指标', 'Definition / 口径', 'Inputs and boundary / 输入与边界']
        values = [[row['id'] + ' / ' + row['source_id'], row['name_zh'],
                   row['summary_en'] + ' / ' + row['formula_zh'],
                   row['inputs_zh'] + '；' + row['boundary_zh']] for row in rows]
    elif group == 'probe_catalog':
        headings = ['ID / 编号', 'Probe / 探针', 'Inputs and checks / 输入与检查', 'Boundary and owner / 边界与责任人']
        values = [[row['id'] + ' / ' + row['source_id'], row['summary_en'] + ' / ' + row['name_zh'],
                   row['inputs_zh'] + '；' + row['checks_zh'],
                   row['boundary_zh'] + '；' + row['receiver_zh']] for row in rows]
    else:
        headings = ['ID / 编号', 'Scenario and expected behavior / 场景与预期行为', 'Source scenario / 来源场景', 'Required outcome / 必需结果']
        values = [[row['id'] + ' / ' + row['source_id'], row['summary_en'],
                   row['condition_zh'], row['expected_zh']] for row in rows]
    table = ['| ' + ' | '.join(headings) + ' |', '| ' + ' | '.join(['---'] * len(headings)) + ' |']
    return '\n'.join(table + ['| ' + ' | '.join(_cell(value) for value in row) + ' |' for row in values])


def views(skill_dir: Path) -> dict[str, dict[str, str]]:
    """Build deterministic views from maintained sources / 从维护源生成确定视图。"""
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    contract = (skill_dir / CONTRACT).read_text(encoding='utf-8').split('\n', 1)[1].strip()
    contract = contract.replace('## Quick Navigation / 快速导航', '### Contract Navigation / 契约导航', 1)
    return {
        DESIGN: {'contract': contract, 'execution_cases': _table(source['execution_cases'], 'execution_cases')},
        PROBE: {'contract': contract, **{key: _table(source[key], key) for key in ['probe_catalog', 'metrics', 'probe_cases']}},
    }


def _block(section: str, content: str) -> str:
    return f'<!-- hierarchy:{section}:start -->\n{content}\n<!-- hierarchy:{section}:end -->'


def _pattern(section: str) -> str:
    return re.escape(f'<!-- hierarchy:{section}:start -->') + r'.*?' + re.escape(f'<!-- hierarchy:{section}:end -->')


def validate_hierarchy_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Check documentation provenance, not business success / 核验文档来源，不判业务成功。"""
    errors: list[str] = []
    try:
        registry = registry or json.loads((skill_dir / 'references/registry.json').read_text(encoding='utf-8'))
        cell = next(item for item in registry['cells'] if item['id'] == 'CELL_COLLABORATION_HIERARCHY')
        source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
        expected_spec = dict(version='0.1.0', source_contract_version='0.1.0', status='draft',
                             implementation_status='specification_only', source_map_reference=SOURCE_MAP,
                             interaction_contract_reference=CONTRACT)
        if (cell['pattern_ref'] != 'PATTERN_0046' or cell['maturity'] != 'draft'
                or cell['design_path'] != DESIGN or cell['observability_path'] != PROBE
                or cell.get('delegation_specification') != expected_spec):
            errors.append('hierarchy_registry: identity, maturity or specification reference drift')
        if (source['pattern_ref'] != cell['pattern_ref'] or source['cell_ref'] != cell['id']
                or source['version'] != '0.1.0' or source['source_contract_version'] != '0.1.0'
                or source['implementation_status'] != 'specification_only'):
            errors.append('hierarchy_source: unsupported identity, protocol or implementation claim')
        if [item['id'] for item in source['sources']] != ['execution', 'probe']:
            errors.append('hierarchy_source: expected execution and probe sources')
        snapshots = {}
        for item in source['sources']:
            data = (skill_dir.parent.parent / item['snapshot_path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                errors.append('hierarchy_source: snapshot digest drift: ' + item['id'])
            snapshots[item['id']] = data.decode('utf-8')
        # Both supplied documents carry the same complete source contract.
        # / 两份原文必须携带相同的完整共享契约。
        shared = [text.split('### 共享契约版本与对象归属', 1)[1].split('\n## ', 1)[0].strip()
                  for text in snapshots.values()]
        if len(shared) != 2 or shared[0] != shared[1]:
            errors.append('hierarchy_source: supplied shared contracts differ')
        for group, (prefix, count, source_id, source_prefix) in GROUPS.items():
            rows = source[group]
            if [row['id'] for row in rows] != [f'{prefix}{i:02d}' for i in range(1, count + 1)]:
                errors.append('hierarchy_source: count or stable ID drift: ' + group)
            # Ordered source IDs/lines prevent duplicated mappings hiding omissions.
            # / 有序来源编号与行号防止重复映射掩盖遗漏。
            pattern = ('^### ' if group.endswith('_nodes') else r'^\| ') + source_prefix + '[一二三四五六七八九十]+' + ('：' if group.endswith('_nodes') or group in {'metrics', 'probe_catalog'} else r' \|')
            expected_lines = [i for i, line in enumerate(snapshots[source_id].splitlines(), 1) if re.match(pattern, line)]
            if [row['source_line'] for row in rows] != expected_lines:
                errors.append('hierarchy_source: incomplete or duplicate source mapping: ' + group)
            for row in rows:
                line = snapshots[source_id].splitlines()[row['source_line'] - 1]
                source_label = line.removeprefix('### ').removeprefix('| ').split('|', 1)[0].split('：', 1)[0].strip()
                if row['source_ref'] != source_id or row['source_id'] != source_label:
                    errors.append('hierarchy_source: source identity drift: ' + row['id'])
                if any(value not in line for key, value in row.items() if key.endswith('_zh')):
                    errors.append('hierarchy_source: original definition drift: ' + row['id'])
                if not row.get('name_en', row.get('summary_en')):
                    errors.append('hierarchy_source: missing English mapping: ' + row['id'])
                if group.endswith('_cases') and row.get('integration_status') != 'pending':
                    errors.append('hierarchy_source: unsupported integration claim: ' + row['id'])
                if group == 'metrics' and row.get('implementation') != 'specification_only':
                    errors.append('hierarchy_source: unsupported metric implementation: ' + row['id'])
        for relative, sections in views(skill_dir).items():
            text = (skill_dir / relative).read_text(encoding='utf-8')
            for section, content in sections.items():
                matches = re.findall(_pattern(section), text, flags=re.S)
                if matches != [_block(section, content)]:
                    errors.append(f'hierarchy_view: missing, repeated or stale block: {relative} {section}')
        for group, relative in [('execution_nodes', DESIGN), ('probe_nodes', PROBE)]:
            text = (skill_dir / relative).read_text(encoding='utf-8')
            for row in source[group]:
                if f"| {row['id']} / {row['source_id']} |" not in text:
                    errors.append('hierarchy_view: missing workflow node: ' + row['id'])
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        errors.append('hierarchy_specification: ' + str(error))
    return errors


def sync(skill_dir: Path) -> None:
    """Write only generated blocks; preserve authored prose / 仅写生成区块，保留手写正文。"""
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
    errors = validate_hierarchy_assets(args.skill_dir)
    for error in errors:
        print(error)
    print(f'Hierarchy validation / 层级委派校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
