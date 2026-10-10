"""Maintain Handoff Chain specifications / 维护交接链规格。

Usage / 用法: python sync_handoff_chain_docs.py [skill_dir] [--write]
Workflow / 流程: independently discover complete source inventories, check their
provenance and shared YAML semantics, then synchronize bounded bilingual views.
/ 独立发现来源全集，校验出处与共享 YAML 语义，再同步有界双语视图。
Constraints / 约束: preflight every input and peer before writing; preserve
authored prose. These checks neither execute handoffs nor measure business gains.
/ 写入前预检全部输入与两端文档，保留手写内容；不执行交接或测量业务收益。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

try:
    import yaml
except ImportError:  # Optional validation dependency / 可选校验依赖。
    yaml = None

YAML_ERROR = yaml.YAMLError if yaml is not None else ValueError


DESIGN = 'references/patterns/collaboration/collaboration-chain.md'
PROBE = 'references/patterns/collaboration/collaboration-chain-observability.md'
CONTRACT = 'references/handoff-chain-contract.md'
SOURCE_MAP = 'references/handoff-chain-source-map.json'
GROUPS = {
    'execution_nodes': ('HN', 0, 9, 'execution'),
    'gates': ('HG', 1, 8, 'execution'),
    'execution_cases': ('HET', 1, 12, 'execution'),
    'invariants': ('HI', 1, 12, 'execution'),
    'recovery': ('HR', 1, 12, 'execution'),
    'variants': ('HEV', 1, 6, 'execution'),
    'probe_nodes': ('HP', 0, 8, 'probe'),
    'probe_checks': ('HCP', 1, 12, 'probe'),
    'metrics': ('HCM', 1, 30, 'probe'),
    'probe_cases': ('HPT', 1, 17, 'probe'),
}
SECTION_HEADINGS = {
    'gates': '### 节点六：接收方验收',
    'execution_cases': '## 十一、验收测试与完成标准',
    'invariants': '## 五、执行不变量',
    'recovery': '### 7.1 恢复决策表',
    'variants': '### 10.2 必须补测的变体',
    'probe_checks': '## 六、探针清单与证据要求',
    'metrics': '## 七、指标口径与计算规则',
    'probe_cases': '## 十二、探针验证用例',
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class _UniqueKeyLoader(yaml.SafeLoader if yaml is not None else object):
    """Reject ambiguous protocol maps / 拒绝重复键造成的协议歧义。"""


def _unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError('handoff_source: duplicate YAML key: ' + str(key))
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


if yaml is not None:
    _UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def shared_protocols(text: str) -> dict:
    """Read event/request/patch as data; never execute source prompts.
    / 事件、请求与补丁仅作为数据读取，不执行来源内嵌指令。
    """
    if yaml is None:
        raise ValueError('handoff_source: PyYAML is required for protocol validation / 协议校验需要 PyYAML')
    found = {}
    for block in re.findall(r'^```yaml\s*\n(.*?)^```\s*$', text, re.M | re.S):
        value = yaml.load(block, Loader=_UniqueKeyLoader)
        if not isinstance(value, dict) or 'protocol_version' not in value:
            continue
        role = ('event' if 'event_id' in value else 'patch' if 'patch_id' in value
                else 'request' if 'request_id' in value else None)
        if role is None:
            continue
        if role in found:
            raise ValueError('handoff_source: repeated shared protocol: ' + role)
        if value.get('protocol_version') != '1.0':
            raise ValueError('handoff_source: shared protocols differ from required version 1.0')
        found[role] = value
    if set(found) != {'event', 'request', 'patch'}:
        raise ValueError('handoff_source: incomplete shared event/request/patch protocols')
    return found


def protocol_digest(protocols: dict) -> str:
    return digest(json.dumps(protocols, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


def _key_paths(value, prefix: str = '') -> set[str]:
    """Compare recursive fields, not localized example values or scalar types.
    / 比较递归字段，不比较本地化示例值或标量类型。
    """
    paths = set()
    if isinstance(value, dict):
        for key, child in value.items():
            path = prefix + '.' + str(key) if prefix else str(key)
            paths.add(path)
            paths.update(_key_paths(child, path))
    elif isinstance(value, list):
        for child in value:
            paths.update(_key_paths(child, prefix + '[]'))
    return paths


def _section(lines: list[str], heading: str) -> tuple[int, int]:
    matches = [i for i, line in enumerate(lines) if line == heading]
    if len(matches) != 1:
        raise ValueError('handoff_source: expected one source section: ' + heading)
    start = matches[0]
    level = len(heading) - len(heading.lstrip('#'))
    end = next((i for i in range(start + 1, len(lines))
                if re.match(r'^#{1,' + str(level) + r'} ', lines[i])), len(lines))
    return start, end


def _provenance(lines: list[str], start: int, end: int, source_id: str) -> dict:
    while end > start and not lines[end - 1].strip():
        end -= 1
    text = '\n'.join(lines[start:end])
    return dict(source_id=source_id, source_line=start + 1, source_end_line=end,
                source_text=text, excerpt_sha256=digest(text))


def source_rows(text: str, group: str) -> list[dict]:
    """Discover inventories independently from maintained mappings.
    / 从来源独立发现全集，不由待验证映射反推应有项目。
    """
    lines = text.splitlines()
    if group.endswith('_nodes'):
        starts = [i for i, line in enumerate(lines) if re.match(r'^### 节点[^：]+：', line)]
        rows = []
        for start in starts:
            end = next((i for i in range(start + 1, len(lines))
                        if re.match(r'^#{1,3} ', lines[i])), len(lines))
            source_id, name = lines[start][4:].split('：', 1)
            row = _provenance(lines, start, end, source_id)
            row['name_zh'] = name
            rows.append(row)
        return rows
    start, end = _section(lines, SECTION_HEADINGS[group])
    rows = []
    in_table = False
    for i in range(start + 1, end):
        line = lines[i]
        if not line.startswith('|'):
            in_table = False
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-+:?', cell) for cell in cells):
            in_table = True
            continue
        if not in_table:
            continue
        row = _provenance(lines, i, i + 1, cells[0])
        row['source_cells'] = cells
        if group == 'metrics':
            row.update(name_zh=cells[0], formula_zh=cells[1], boundary_zh=cells[2])
        elif group.endswith('_cases') or group == 'variants':
            row.update(condition_zh=cells[0], expected_zh=cells[1])
        else:
            row['name_zh'] = cells[0]
        rows.append(row)
    return rows


def _read_source(skill_dir: Path, registry: dict | None = None) -> tuple[dict, list[str]]:
    if yaml is None:
        raise ValueError('handoff_source: PyYAML is required for protocol validation / 协议校验需要 PyYAML')
    errors = []
    registry = registry if registry is not None else json.loads(
        (skill_dir / 'references/registry.json').read_text(encoding='utf-8'))
    cell = next(item for item in registry['cells'] if item['id'] == 'CELL_COLLABORATION_CHAIN')
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    expected_spec = dict(version='0.1.0', source_contract_version='1.0', status='draft',
                         implementation_status='specification_only', source_map_reference=SOURCE_MAP,
                         interaction_contract_reference=CONTRACT)
    if (cell['pattern_ref'] != 'PATTERN_0043' or cell['maturity'] != 'draft'
            or cell.get('local_evidence_count') != 0 or cell.get('domain_count') != 0
            or cell['coordinate'] != 'COG_COLLABORATION__TOP_CHAIN'
            or cell['design_path'] != DESIGN or cell['observability_path'] != PROBE
            or cell.get('handoff_specification') != expected_spec):
        errors.append('handoff_registry: identity, maturity or specification registration drift')
    expected = dict(version='0.1.0', pattern_ref='PATTERN_0043', cell_ref='CELL_COLLABORATION_CHAIN',
                    source_contract_version='1.0', implementation_status='specification_only',
                    source_pattern_alias='PATTERN_XXXX')
    if any(source.get(key) != value for key, value in expected.items()):
        errors.append('handoff_source: identity or implementation status drift')
    for field in ('name_en', 'name_zh', 'description_en', 'description_zh'):
        if not source.get(field):
            errors.append('handoff_source: missing bilingual metadata: ' + field)
    if [item['id'] for item in source['sources']] != ['execution', 'probe']:
        raise ValueError('handoff_source: expected one execution and one probe source')
    snapshots = {}
    evidence_root = (skill_dir.parent.parent / '.harness-analysis').resolve()
    for item in source['sources']:
        path = (skill_dir.parent.parent / item['snapshot_path']).resolve()
        if not path.is_relative_to(evidence_root):
            raise ValueError('handoff_source: snapshot outside project evidence directory')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            errors.append('handoff_source: snapshot digest drift: ' + item['id'])
        text = data.decode('utf-8-sig').replace('\r\n', '\n')
        front = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        metadata = yaml.load(front[1], Loader=_UniqueKeyLoader) if front else {}
        source_identity = (metadata.get('pattern_id') == 'PATTERN_XXXX' if item['id'] == 'execution'
                           else metadata.get('related_patterns') == ['PATTERN_XXXX'])
        if (item['version'] != '0.1.0' or not item.get('name_en') or not item.get('name_zh')
                or metadata.get('version') != '0.1.0' or not source_identity
                or metadata.get('interface_version') != '1.0'):
            errors.append('handoff_source: source identity, version or bilingual metadata drift')
        snapshots[item['id']] = text
    protocols = [shared_protocols(text) for text in snapshots.values()]
    if (protocols[0] != protocols[1]
            or protocol_digest(protocols[0]) != source['shared_source_protocols_sha256']):
        errors.append('handoff_source: shared protocols differ or fingerprint changed')
    contract = (skill_dir / CONTRACT).read_text(encoding='utf-8')
    if not all(token in contract for token in ('PATTERN_0043', '1.0', 'specification_only')):
        errors.append('handoff_contract: missing pattern, protocol or specification identity')
    try:
        local_protocols = shared_protocols(contract)
        for role in ('event', 'request', 'patch'):
            missing = _key_paths(protocols[0][role]) - _key_paths(local_protocols[role])
            if missing:
                errors.append('handoff_contract: missing source field paths: '
                              + ', '.join(role + '.' + path for path in sorted(missing)))
    except (ValueError, YAML_ERROR) as error:
        errors.append('handoff_contract: ' + str(error))
    for group, (prefix, first, count, sid) in GROUPS.items():
        rows = source[group]
        original = source_rows(snapshots[sid], group)
        if [row['id'] for row in rows] != [f'{prefix}{i:02d}' for i in range(first, first + count)]:
            errors.append('handoff_source: count or stable ID drift: ' + group)
        if len(original) != count or len(rows) != len(original):
            errors.append('handoff_source: incomplete source inventory: ' + group)
        for row, original_row in zip(rows, original):
            if row['source_ref'] != sid or any(row.get(key) != value for key, value in original_row.items()):
                errors.append('handoff_source: original mapping or definition drift: ' + row['id'])
            if not row.get('name_en') or not row.get('summary_en'):
                errors.append('handoff_source: missing English instructions: ' + row['id'])
            if row.get('integration_status') != 'pending':
                errors.append('handoff_source: unsupported integration claim: ' + row['id'])
            if group == 'metrics' and row.get('implementation') != 'specification_only':
                errors.append('handoff_source: unsupported metric implementation: ' + row['id'])
    return source, errors


def _cell(text: str) -> str:
    return text.replace('|', '&#124;').replace('\n', '<br>')


def _table(rows: list[dict], group: str) -> str:
    headings = ['ID / 编号', 'Item / 条目', 'Definition and evidence / 定义与证据']
    values = []
    for row in rows:
        name_zh = row.get('name_zh', row.get('condition_zh', row['source_id']))
        if group.endswith('_nodes'):
            chinese = row['source_text'].split('\n', 1)[1].strip()
        elif group == 'metrics':
            chinese = row['formula_zh'] + '<br>Boundary / 边界：' + row['boundary_zh']
        else:
            chinese = '<br>'.join(row['source_cells'][1:])
        values.append([row['id'], row['name_en'] + ' / ' + name_zh,
                       row['summary_en'] + '<br>' + chinese])
    return '\n'.join(['| ' + ' | '.join(headings) + ' |', '| --- | --- | --- |']
                     + ['| ' + ' | '.join(_cell(value) for value in row) + ' |' for row in values])


def views(skill_dir: Path) -> dict[str, dict[str, str]]:
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    return {relative: {group: _table(source[group], group)
                       for group, (_, _, _, owner) in GROUPS.items() if owner == sid}
            for relative, sid in ((DESIGN, 'execution'), (PROBE, 'probe'))}


def _block(section: str, text: str) -> str:
    return f'<!-- handoff:{section}:start -->\n{text}\n<!-- handoff:{section}:end -->'


def _pattern(section: str) -> str:
    return re.escape(f'<!-- handoff:{section}:start -->') + r'.*?' + re.escape(f'<!-- handoff:{section}:end -->')


def _require_markers(text: str, section: str) -> None:
    start, end = [f'<!-- handoff:{section}:{edge} -->' for edge in ('start', 'end')]
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('handoff_view: missing or repeated marker: ' + section)
    if text.index(start) >= text.index(end):
        raise ValueError('handoff_view: invalid marker order: ' + section)


def _preflight_views(text: str, sections: dict[str, str]) -> None:
    ranges = []
    for section in sections:
        _require_markers(text, section)
        ranges.append((text.index(f'<!-- handoff:{section}:start -->'),
                       text.index(f'<!-- handoff:{section}:end -->')))
    ranges.sort()
    if any(left[1] > right[0] for left, right in zip(ranges, ranges[1:])):
        raise ValueError('handoff_view: overlapping generated blocks')


def validate_handoff_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Validate specifications, never deployment / 校验规格，不证明已部署。"""
    try:
        _, errors = _read_source(skill_dir, registry)
        for relative, sections in views(skill_dir).items():
            text = (skill_dir / relative).read_text(encoding='utf-8')
            if '\ufffd' in text:
                errors.append('handoff_view: invalid replacement character: ' + relative)
            _preflight_views(text, sections)
            for section, content in sections.items():
                if re.findall(_pattern(section), text, re.S) != [_block(section, content)]:
                    errors.append(f'handoff_view: stale block: {relative} {section}')
        return errors
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration, YAML_ERROR) as error:
        return ['handoff_specification: ' + str(error)]


def sync(skill_dir: Path) -> None:
    """Preflight both peers before writing / 写入前预检两份文档。"""
    _, errors = _read_source(skill_dir)
    if errors:
        raise ValueError('\n'.join(errors))
    pending = []
    for relative, sections in views(skill_dir).items():
        path = skill_dir / relative
        text = path.read_text(encoding='utf-8')
        _preflight_views(text, sections)
        for section, content in sections.items():
            text, count = re.subn(_pattern(section), lambda _: _block(section, content), text, flags=re.S)
            if count != 1:
                raise ValueError(f'handoff_view: invalid marker order: {relative} {section}')
        pending.append((path, text))
    for path, text in pending:
        if path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8', newline='\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    try:
        if args.write:
            sync(args.skill_dir)
        errors = validate_handoff_assets(args.skill_dir)
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration, YAML_ERROR) as error:
        errors = [str(error)]
    for error in errors:
        print(error)
    print(f'Handoff validation / 交接链校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
