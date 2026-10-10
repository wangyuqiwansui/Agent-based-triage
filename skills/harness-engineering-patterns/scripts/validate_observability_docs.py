"""Observability specification validator / 可观测性规格校验器。

Usage / 用法: python validate_observability_docs.py [skill_dir]
Workflow / 流程: Extract source inventories independently, then verify hashes,
identity, coverage and navigation. / 独立提取来源清单，校验哈希、身份、覆盖和导航。
Constraints / 约束: Read-only asset checks; never executes business scenarios
or claims production acceptance. / 只读资产检查，不执行业务场景或宣称生产验收。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

EXECUTION = 'references/observability-execution-flow.md'
PROBE = 'references/observability-probes.md'
CONTRACT = 'references/observability-contract.md'
SOURCE_MAP = 'references/observability-source-map.json'
DESIGN = 'references/patterns/governance/governance-orchestration.md'
CARD = 'references/patterns/governance/governance-orchestration-observability.md'
GROUPS = {
    'execution_steps': ('OBE', 13, 'execution', EXECUTION),
    'probes': ('PROBE_', 45, 'probe', PROBE),
    'metrics': ('OBM', 50, 'probe', PROBE),
    'acceptance_cases': ('OBT', 15, 'probe', PROBE),
}
ALIASES = {
    'pattern': ['PATTERN_OBSERVABILITY_0001', 'PATTERN_OBSERVABILITY_0002'],
    'skill': ['SKILL_OBSERVABILITY_EXECUTION_0001', 'SKILL_OBSERVABILITY_PROBE_0001'],
}
REGISTRATION = {
    'version': '0.1.0', 'status': 'draft', 'implementation_status': 'specification_only',
    'pattern_ref': 'PATTERN_0049', 'cell_ref': 'CELL_GOVERNANCE_ORCHESTRATION',
    'execution_reference': EXECUTION, 'observability_reference': PROBE,
    'interaction_contract_reference': CONTRACT, 'source_map_reference': SOURCE_MAP,
    'shared_probe_pattern_ref': 'PATTERN_0052', 'shared_probe_version': '0.8.0',
}


def source_inventory(content: str, group: str) -> list[dict]:
    """Extract definition blocks, not incidental mentions / 提取定义而非偶然引用。"""
    prefix, _, _, target = GROUPS[group]
    lines = content.splitlines()
    found = []
    section = ''
    for index, line in enumerate(lines):
        if line.startswith('#'):
            section = line
        if group == 'execution_steps' and re.match(r'^### 阶段 \d+：', line):
            end = next((i for i in range(index + 1, len(lines)) if lines[i].startswith('#')), len(lines))
            found.append((index, end, line.lstrip('# ').strip(), None))
        elif group == 'probes' and re.match(r'^\| PROBE_[A-Z]+_\d{3} \|', line):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            found.append((index, index + 1, cells[1], cells[0]))
        elif group == 'metrics' and re.match(r'^### (13\.\d+|21\.2) ', section):
            if line.startswith('|') and not re.match(r'^\|(?:---| 指标)', line):
                found.append((index, index + 1, line.split('|')[1].strip(), None))
        elif group == 'acceptance_cases' and section.startswith('### 21.3 ') and line.startswith('- '):
            found.append((index, index + 1, line[2:].rstrip('；。'), None))
    return [dict(id=source_id or f'{prefix}{number:02d}', source_line=start + 1,
                 source_end_line=end, source_label=label,
                 excerpt_sha256=hashlib.sha256('\n'.join(lines[start:end]).rstrip().encode('utf-8')).hexdigest(),
                 target_document=target)
            for number, (start, end, label, source_id) in enumerate(found, 1)]


def _local_file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('missing or outside skill file: ' + relative)
    return path


def validate_observability_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Validate assets, not live behavior / 校验资产，不证明线上行为。"""
    errors = []
    try:
        root = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            _local_file(root, 'references/registry.json').read_text(encoding='utf-8'))
        source = json.loads(_local_file(root, SOURCE_MAP).read_text(encoding='utf-8'))
        for label, value in [('registry', registry.get('observability_specification', {})), ('source', source)]:
            if any(value.get(key) != expected for key, expected in REGISTRATION.items()):
                errors.append(label + ': registration or readiness drift')
            for key in ('name_en', 'name_zh', 'description_en', 'description_zh'):
                if not isinstance(value.get(key), str) or not value[key].strip():
                    errors.append(label + ': missing bilingual metadata: ' + key)
        if source.get('source_aliases') != ALIASES:
            errors.append('source: alias drift')
        if source.get('acceptance_status') != 'not_executed' or source.get('metric_implementation') != 'specification_only':
            errors.append('source: unsupported runtime validation claim')
        cell = [c for c in registry['cells'] if c['id'] == REGISTRATION['cell_ref']]
        if len(cell) != 1 or any(cell[0].get(k) != v for k, v in {
            'pattern_ref': 'PATTERN_0049', 'maturity': 'draft', 'status': 'named',
            'coordinate': 'COG_GOVERNANCE__TOP_ORCHESTRATION',
            'design_path': DESIGN, 'observability_path': CARD,
        }.items()):
            errors.append('registry: stable identity or maturity drift')
        if any(p['id'] in ALIASES['pattern'] for p in registry['patterns']):
            errors.append('registry: source alias registered as new pattern')
        shared = [p for p in registry['patterns'] if p['id'] == 'PATTERN_0052']
        if len(shared) != 1 or shared[0].get('source_version') != '0.8.0':
            errors.append('registry: shared protocol drift')
        if [s['id'] for s in source['sources']] != ['execution', 'probe']:
            raise ValueError('expected exactly two ordered sources')
        snapshots = {}
        for n, item in enumerate(source['sources']):
            path = _local_file(root, item['snapshot_path'])
            if not path.is_relative_to(root / 'references/sources/observability'):
                raise ValueError('snapshot outside observability evidence directory')
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                errors.append('source: snapshot digest drift: ' + item['id'])
            content = data.decode('utf-8-sig').replace('\r\n', '\n')
            for key, value in [('pattern_id', ALIASES['pattern'][n]), ('skill_candidate', ALIASES['skill'][n]),
                               ('version', '0.1.0'), ('status', 'draft')]:
                if not re.search(rf'^{key}: {re.escape(value)}$', content, re.M):
                    errors.append('source: metadata drift: ' + key)
            snapshots[item['id']] = content
        documents = {p: _local_file(root, p).read_text(encoding='utf-8')
                     for p in (EXECUTION, PROBE, CONTRACT, DESIGN, CARD)}
        for group, (prefix, count, sid, target) in GROUPS.items():
            inventory = source_inventory(snapshots[sid], group)
            if len(inventory) != count or len({r['id'] for r in inventory}) != count:
                errors.append('source: unexpected definition count: ' + group)
            if source['inventories'].get(group) != inventory:
                errors.append('source: definition mapping drift: ' + group)
            expression = r'PROBE_[A-Z]+_\d{3}' if group == 'probes' else prefix + r'\d+'
            ids = re.findall(rf'^\| ({expression}) \|', documents[target], re.M)
            if ids != [r['id'] for r in inventory]:
                errors.append('document: missing/repeated/reordered definitions: ' + group)
            source_lines = snapshots[sid].splitlines()
            for item in inventory:
                row = next((line for line in documents[target].splitlines()
                            if line.startswith('| ' + item['id'] + ' |')), '')
                label = re.sub(r'^阶段 \d+：', '', item['source_label'])
                if label not in row:
                    errors.append('document: source label lost: ' + item['id'])
                if group in ('metrics', 'probes'):
                    cells = [c.strip() for c in source_lines[item['source_line'] - 1].split('|')[1:-1]]
                    required = cells[1:2] if group == 'metrics' else cells[2:]
                    if any(value not in row for value in required):
                        errors.append('document: source requirement drift: ' + item['id'])
        local_ids = [f'OBX{i:02d}' for i in range(1, 13)]
        if source.get('local_acceptance_ids') != local_ids:
            errors.append('source: local acceptance inventory drift')
        if re.findall(r'^\| (OBX\d+) \|', documents[PROBE], re.M) != local_ids:
            errors.append('document: local acceptance coverage drift')
        for path, content in documents.items():
            if '\ufffd' in content:
                errors.append('document: corrupt Unicode: ' + path)
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if re.match(r'[a-zA-Z][\w+.-]*:', link):
                    continue
                location, _, fragment = link.partition('#')
                destination = _local_file(root, str(Path(path).parent / location) if location else path)
                if fragment and destination.name.startswith('observability-'):
                    if f'id="{fragment}"' not in destination.read_text(encoding='utf-8'):
                        errors.append('document: missing anchor: ' + link)
        for path in (EXECUTION, PROBE):
            if '(observability-contract.md)' not in documents[path]:
                errors.append('document: missing shared contract link: ' + path)
        for path, target in [(DESIGN, EXECUTION), (CARD, PROBE)]:
            if Path(target).name not in documents[path]:
                errors.append('document: missing pattern attachment: ' + path)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
        errors.append('observability_specification: ' + str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_observability_assets(parser.parse_args().skill_dir)
    for error in errors:
        print(error)
    print(f'Observability asset validation / 可观测性资产校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
