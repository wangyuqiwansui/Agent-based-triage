"""Blast radius specification validator / 爆炸半径规格校验器。

Usage / 用法: python validate_blast_radius_docs.py [skill_dir]
Workflow / 流程: Independently extract source definitions, verify fingerprints,
registration and maintained links. / 独立提取来源定义，校验指纹、注册与维护链接。
Constraints / 约束: Read-only asset checks, not runtime or business acceptance.
/ 只读资产检查，不执行运行时或业务验收。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXECUTION = 'references/blast-radius-execution-flow.md'
PROBE = 'references/blast-radius-observability-probes.md'
CONTRACT = 'references/blast-radius-contract.md'
SOURCE_MAP = 'references/blast-radius-source-map.json'
DESIGN = 'references/patterns/governance/governance-hierarchy.md'
CARD = 'references/patterns/governance/governance-hierarchy-observability.md'
GROUPS = {
    'execution_steps': ('BRE', 14, 'execution', EXECUTION, '14.2'),
    'probe_steps': ('BRP', 16, 'probe', PROBE, '11'),
    'components': ('BRC', 18, 'probe', PROBE, '12'),
    'metrics': ('BRM', 39, 'probe', PROBE, '13'),
    'execution_cases': ('BRT', 16, 'execution', EXECUTION, '28.1'),
    'probe_cases': ('BRQ', 16, 'probe', PROBE, '25'),
}
ALIASES = {
    'pattern': ['PATTERN_GOVERNANCE_BLAST_RADIUS_0001'],
    'skill': ['SKILL_GOVERNANCE_BLAST_RADIUS_EXECUTION_0001',
              'SKILL_GOVERNANCE_BLAST_RADIUS_PROBE_0001'],
}
REGISTRATION = {
    'version': '0.1.0', 'status': 'draft',
    'implementation_status': 'specification_only',
    'pattern_ref': 'PATTERN_0050', 'cell_ref': 'CELL_GOVERNANCE_HIERARCHY',
    'execution_reference': EXECUTION, 'observability_reference': PROBE,
    'interaction_contract_reference': CONTRACT, 'source_map_reference': SOURCE_MAP,
}


def source_inventory(text: str, group: str) -> list[dict]:
    """Extract full source sections/rows / 提取完整来源章节或表格行。"""
    prefix, _, _, target, section = GROUPS[group]
    lines = text.splitlines()
    found = []
    if group in ('components', 'metrics'):
        pattern = r'^## 12\.\d+ ' if group == 'components' else r'^### 13\.\d+\.\d+ '
        for index, line in enumerate(lines):
            if re.match(pattern, line):
                end = index + 1
                while end < len(lines) and not lines[end].startswith('#'):
                    end += 1
                found.append((index, end, line.lstrip('# ').strip()))
    else:
        matches = [i for i, line in enumerate(lines)
                   if re.match(rf'^#+ {re.escape(section)}\.? ', line)]
        if len(matches) != 1:
            raise ValueError('source section missing or repeated: ' + group)
        start = matches[0] + 1
        end = next((i for i in range(start, len(lines)) if lines[i].startswith('#')), len(lines))
        rows = [i for i in range(start, end) if lines[i].startswith('|')]
        for index in rows[2:]:  # header and separator / 跳过表头及分隔行
            found.append((index, index + 1, lines[index].split('|')[1].strip()))
    return [dict(id=f'{prefix}{number:02d}', source_line=start + 1,
                 source_end_line=end, source_label=label,
                 excerpt_sha256=hashlib.sha256('\n'.join(lines[start:end]).rstrip().encode('utf-8')).hexdigest(),
                 target_document=target)
            for number, (start, end, label) in enumerate(found, 1)]


def _local_file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('missing or outside skill file: ' + relative)
    return path


def validate_blast_radius_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Check source/navigation integrity, not semantic correctness.
    / 检查来源导航完整性，不证明语义正确性。
    """
    errors = []
    try:
        root = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            _local_file(root, 'references/registry.json').read_text(encoding='utf-8'))
        source = json.loads(_local_file(root, SOURCE_MAP).read_text(encoding='utf-8'))
        for label, value in [('registry', registry.get('blast_radius_specification', {})), ('source', source)]:
            if any(value.get(key) != expected for key, expected in REGISTRATION.items()):
                errors.append(label + ': registration or readiness drift')
            for key in ('name_en', 'name_zh', 'description_en', 'description_zh'):
                if not isinstance(value.get(key), str) or not value[key].strip():
                    errors.append(label + ': missing bilingual metadata: ' + key)
        if source.get('source_aliases') != ALIASES:
            errors.append('source: alias drift')
        if source.get('acceptance_status') != 'not_executed' or source.get('metric_implementation') != 'specification_only':
            errors.append('source: unsupported runtime validation claim')
        cells = [c for c in registry['cells'] if c['id'] == REGISTRATION['cell_ref']]
        if len(cells) != 1 or any(cells[0].get(k) != v for k, v in {
            'pattern_ref': 'PATTERN_0050', 'status': 'named', 'maturity': 'draft',
            'design_path': DESIGN, 'observability_path': CARD,
            'coordinate': 'COG_GOVERNANCE__TOP_HIERARCHY',
        }.items()):
            errors.append('registry: stable cell identity or maturity drift')
        if any(p['id'] in ALIASES['pattern'] for p in registry['patterns']):
            errors.append('registry: source alias registered as new pattern')
        if [item['id'] for item in source['sources']] != ['execution', 'probe']:
            raise ValueError('expected exactly two ordered source snapshots')
        snapshots = {}
        evidence_root = (root / 'references/sources/blast-radius').resolve()
        for item in source['sources']:
            path = _local_file(root, item['snapshot_path'])
            if not path.is_relative_to(evidence_root):
                raise ValueError('snapshot outside blast-radius evidence directory')
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                errors.append('source: snapshot digest drift: ' + item['id'])
            content = data.decode('utf-8-sig').replace('\r\n', '\n')
            skill_alias = ALIASES['skill'][0 if item['id'] == 'execution' else 1]
            for key, value in [('pattern_id', ALIASES['pattern'][0]), ('skill_id', skill_alias),
                               ('version', '0.1.0'), ('status', 'draft')]:
                if not re.search(rf'^{key}: {re.escape(value)}$', content, re.M):
                    errors.append('source: metadata drift: ' + key)
            snapshots[item['id']] = content
        documents = {path: _local_file(root, path).read_text(encoding='utf-8')
                     for path in (EXECUTION, PROBE, CONTRACT, DESIGN, CARD)}
        for group, (prefix, count, sid, target, _) in GROUPS.items():
            inventory = source_inventory(snapshots[sid], group)
            expected_ids = [f'{prefix}{i:02d}' for i in range(1, count + 1)]
            if [row['id'] for row in inventory] != expected_ids:
                errors.append('source: unexpected definition count: ' + group)
            if source['inventories'].get(group) != inventory:
                errors.append('source: definition mapping drift: ' + group)
            ids = re.findall(rf'^\| ({prefix}\d+) \|', documents[target], re.M)
            if ids != expected_ids:
                errors.append('document: missing/repeated/reordered definitions: ' + group)
        for path, content in documents.items():
            if '\ufffd' in content:
                errors.append('document: corrupt Unicode: ' + path)
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if re.match(r'[a-zA-Z][\w+.-]*:', link) or link.startswith('#'):
                    continue
                location, _, fragment = link.partition('#')
                destination = _local_file(root, str((Path(path).parent / location)))
                # Explicit anchors are checked for our new references.
                # / 新增文档使用显式锚点并校验其存在。
                if fragment and destination.name.startswith('blast-radius-'):
                    if f'id="{fragment}"' not in destination.read_text(encoding='utf-8'):
                        errors.append('document: missing anchor: ' + link)
        for path in (EXECUTION, PROBE):
            if '(blast-radius-contract.md)' not in documents[path]:
                errors.append('document: missing shared contract link: ' + path)
        for path, target in [(DESIGN, EXECUTION), (CARD, PROBE)]:
            if Path(target).name not in documents[path]:
                errors.append('document: missing pattern attachment: ' + path)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
        errors.append('blast_radius_specification: ' + str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_blast_radius_assets(parser.parse_args().skill_dir)
    for error in errors:
        print(error)
    print(f'Blast radius asset validation / 爆炸半径资产校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
