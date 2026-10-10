"""Progressive commitment asset validator / 渐进承诺资产校验器。

Usage / 用法: python validate_progressive_commitment_docs.py [skill_dir]
Workflow / 流程: Verify source bytes, independently extract inventories and check
registration, definitions and navigation. / 核验来源字节，独立提取目录，检查注册定义和导航。
Constraints / 约束: Read-only; no business actions or runtime acceptance claims.
/ 只读，不执行业务动作，不宣称运行时验收通过。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXECUTION = 'references/progressive-commitment-execution-flow.md'
PROBE = 'references/progressive-commitment-observability-probes.md'
CONTRACT = 'references/progressive-commitment-contract.md'
SOURCE_MAP = 'references/progressive-commitment-source-map.json'
DESIGN = 'references/patterns/governance/governance-parallel.md'
CARD = 'references/patterns/governance/governance-parallel-observability.md'
REGISTRATION = {
    'version': '0.1.0', 'status': 'draft',
    'implementation_status': 'specification_only',
    'pattern_ref': 'PATTERN_0048', 'cell_ref': 'CELL_GOVERNANCE_PARALLEL',
    'execution_reference': EXECUTION, 'observability_reference': PROBE,
    'interaction_contract_reference': CONTRACT, 'source_map_reference': SOURCE_MAP,
}
ALIASES = {'pattern': ['PATTERN_GOVERNANCE_0003'], 'probe': ['PROBE_GOVERNANCE_0003']}
GROUPS = {
    'execution_steps': ('execution', EXECUTION, r'F\d{2}', 15),
    'probe_steps': ('probe', PROBE, r'P\d{2}', 13),
    'specialized_probes': ('probe', PROBE, r'SP-\d{2}', 20),
    'metrics': ('probe', PROBE, r'PM-[A-Z]+-\d{2}', 114),
    'execution_cases': ('execution', EXECUTION, r'PCT-\d{2}', 29),
    'probe_cases': ('probe', PROBE, r'PCQ-\d{2}', 31),
}


def source_inventory(text: str, group: str) -> list[dict]:
    """Extract source-owned sections/rows / 提取来源拥有的章节和表格行。"""
    _, target, pattern, _ = GROUPS[group]
    lines = text.replace('\r\n', '\n').splitlines()
    found = []
    for index, line in enumerate(lines):
        if group.endswith('_steps'):
            match = re.match(rf'^### ({pattern}) (.+)$', line)
            if match:
                end = next((i for i in range(index + 1, len(lines))
                            if lines[i].startswith('#')), len(lines))
                found.append((match[1], index, end, match[2]))
        elif group in ('metrics', 'specialized_probes'):
            match = re.match(rf'^\| ({pattern}) \|', line)
            if match:
                found.append((match[1], index, index + 1, line.split('|')[2].strip()))
    if group.endswith('_cases'):
        chapter, prefix = ('23', 'PCT') if group == 'execution_cases' else ('36', 'PCQ')
        start = next(i for i, line in enumerate(lines) if line.startswith(f'## {chapter}. '))
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('## '))
        for index in range(start, end):
            match = re.match(r'^\d+\. (.+)$', lines[index])
            if match:
                found.append((f'{prefix}-{len(found) + 1:02}', index, index + 1, match[1]))
    return [dict(id=key, source_line=start + 1, source_end_line=end,
                 source_label=label,
                 excerpt_sha256=hashlib.sha256('\n'.join(lines[start:end]).rstrip().encode('utf-8')).hexdigest(),
                 target_document=target)
            for key, start, end, label in found]


def _file(root: Path, path: str) -> Path:
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('missing or outside skill file: ' + path)
    return resolved


def validate_progressive_commitment_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Validate asset integrity, not implemented behavior / 校验资产完整性，不证明已实现行为。"""
    errors = []
    try:
        root = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            _file(root, 'references/registry.json').read_text(encoding='utf-8'))
        mapping = json.loads(_file(root, SOURCE_MAP).read_text(encoding='utf-8'))
        for label, record in [('registry', registry.get('progressive_commitment_specification', {})),
                              ('source', mapping)]:
            if any(record.get(k) != v for k, v in REGISTRATION.items()):
                errors.append(label + ': registration or readiness drift')
            for key in ('name_en', 'name_zh', 'description_en', 'description_zh'):
                if not isinstance(record.get(key), str) or not record[key].strip():
                    errors.append(label + ': missing bilingual metadata: ' + key)
        if mapping.get('source_aliases') != ALIASES:
            errors.append('source: alias drift')
        if mapping.get('acceptance_status') != 'not_executed' or mapping.get('metric_implementation') != 'specification_only':
            errors.append('source: unsupported runtime validation claim')
        cell = [c for c in registry['cells'] if c['id'] == REGISTRATION['cell_ref']]
        expected = {'pattern_ref': 'PATTERN_0048', 'coordinate': 'COG_GOVERNANCE__TOP_PARALLEL',
                    'status': 'named', 'maturity': 'draft', 'design_path': DESIGN, 'observability_path': CARD}
        if len(cell) != 1 or any(cell[0].get(k) != v for k, v in expected.items()):
            errors.append('registry: stable identity, coordinate or maturity drift')
        if any(p['id'] in ALIASES['pattern'] for p in registry['patterns']):
            errors.append('registry: source alias registered as a new pattern')
        for key in ('CHAIN', 'LOOP'):
            cells = [c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_' + key]
            if len(cells) != 1 or cells[0]['status'] != 'extension_candidate' or cells[0]['pattern_ref'] is not None:
                errors.append('registry: source coordinate promoted without evidence: ' + key)
        if [s['id'] for s in mapping['sources']] != ['execution', 'probe']:
            raise ValueError('expected two ordered source snapshots')
        snapshots = {}
        for source in mapping['sources']:
            path = _file(root, source['snapshot_path'])
            if not path.is_relative_to(root / 'references/sources/progressive-commitment'):
                raise ValueError('snapshot outside progressive-commitment evidence directory')
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != source['sha256']:
                errors.append('source: snapshot digest drift: ' + source['id'])
            content = raw.decode('utf-8-sig').replace('\r\n', '\n')
            for required in ('PATTERN_GOVERNANCE_0003', 'COG_GOVERNANCE__TOP_CHAIN', 'COG_GOVERNANCE__TOP_LOOP'):
                if required not in content:
                    errors.append('source: original identity missing: ' + required)
            snapshots[source['id']] = content
        documents = {name: _file(root, name).read_text(encoding='utf-8')
                     for name in (EXECUTION, PROBE, CONTRACT, DESIGN, CARD)}
        for group, (source_id, target, pattern, count) in GROUPS.items():
            inventory = source_inventory(snapshots[source_id], group)
            ids = [row['id'] for row in inventory]
            if len(ids) != count or len(set(ids)) != count:
                errors.append('source: unexpected count or duplicate: ' + group)
            if mapping['inventories'].get(group) != inventory:
                errors.append('source: definition mapping drift: ' + group)
            definition_text = documents[target]
            if group == 'metrics':
                # Clarification tables may cite an exact metric ID as well.
                # / 口径澄清表也可能引用完整指标 ID，定义仅从目录提取。
                definition_text = definition_text.partition('## Metric Catalog / 指标目录\n')[2].split('\n## ', 1)[0]
            rows = [line for line in definition_text.splitlines()
                    if re.match(rf'^\| ({pattern}) \|', line)]
            if [row.split('|')[1].strip() for row in rows] != ids:
                errors.append('document: missing/repeated/reordered definitions: ' + group)
            source_lines = snapshots[source_id].splitlines()
            for item, row in zip(inventory, rows):
                if item['source_label'] not in row:
                    errors.append('document: source label lost: ' + item['id'])
                if group == 'metrics':
                    formula = source_lines[item['source_line'] - 1].split('|')[3].strip()
                    if formula not in row:
                        errors.append('document: source formula drift: ' + item['id'])
        for path, content in documents.items():
            if '\ufffd' in content or '<!-- SOURCE_' in content:
                errors.append('document: corrupt Unicode or unfinished source block: ' + path)
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if re.match(r'[a-zA-Z][\w+.-]*:', link) or link.startswith('#'):
                    continue
                location, _, anchor = link.partition('#')
                destination = _file(root, str(Path(path).parent / location))
                if anchor and destination.name.startswith('progressive-commitment-'):
                    if f'id="{anchor}"' not in destination.read_text(encoding='utf-8'):
                        errors.append('document: missing anchor: ' + link)
        for name in (EXECUTION, PROBE):
            if '(progressive-commitment-contract.md)' not in documents[name]:
                errors.append('document: missing shared contract: ' + name)
        for name, target in ((DESIGN, EXECUTION), (CARD, PROBE)):
            if Path(target).name not in documents[name]:
                errors.append('document: missing pattern attachment: ' + name)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, StopIteration) as error:
        errors.append('progressive_commitment_specification: ' + str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_progressive_commitment_assets(parser.parse_args().skill_dir)
    for error in errors:
        print(error)
    print(f'Progressive commitment assets / 渐进承诺资产: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
