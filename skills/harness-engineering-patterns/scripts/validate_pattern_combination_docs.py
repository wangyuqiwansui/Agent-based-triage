"""Pattern combination asset validation / 模式组合资产校验。

Usage / 用法: python validate_pattern_combination_docs.py [skill_dir]
Workflow / 流程: Check immutable sources, complete inventories, bilingual views,
registration and links. / 检查不可变来源、完整清单、双语视图、注册与链接。
Constraints / 约束: Read-only; does not execute business acceptance scenarios.
/ 只读，不执行业务验收场景。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXECUTION = 'references/pattern-combination-execution-flow.md'
PROBE = 'references/pattern-combination-observability-probes.md'
CONTRACT = 'references/pattern-combination-contract.md'
SOURCE_MAP = 'references/pattern-combination-source-map.json'
SOURCE_HASHES = {
    'execution': 'd97598b686b7636f7be96cd5804c9fa84e5b970c506aba1a6e1929a36fa2286a',
    'probe': 'b614d92c69f9cc50b7937f0a621aa689cf290704c6ee092deb81ec9f0379a19a',
}
REGISTRATION = {
    'name_en': 'Pattern Combination Execution and Independent Probes',
    'name_zh': '模式组合执行与独立探针',
    'description_en': 'Source-backed composition of existing patterns with dependency, version, budget, recovery, evidence and acceptance contracts.',
    'description_zh': '基于来源组合既有模式，明确依赖、版本、预算、恢复、证据及验收契约。',
    'version': '0.1.0', 'status': 'draft',
    'implementation_status': 'specification_only',
    'pattern_ref': 'PATTERN_0053', 'shared_probe_pattern_ref': 'PATTERN_0052',
    'shared_probe_version': '0.8.0',
    'execution_reference': EXECUTION, 'observability_reference': PROBE,
    'interaction_contract_reference': CONTRACT, 'source_map_reference': SOURCE_MAP,
}
GROUPS = {
    'execution_chapters': ('execution', EXECUTION, 21),
    'probe_chapters': ('probe', PROBE, 26),
    'execution_stages': ('execution', EXECUTION, 11),
    'probes': ('probe', PROBE, 14),
    'metrics': ('probe', PROBE, 54),
    'execution_cases': ('execution', EXECUTION, 8),
    'probe_cases': ('probe', PROBE, 12),
}


def source_inventory(content: str, group: str) -> list[dict]:
    """Independently extract full source spans / 独立提取来源完整片段。"""
    source_id, target, _ = GROUPS[group]
    lines = content.replace('\r\n', '\n').splitlines()
    found = []
    if group.endswith('_chapters'):
        starts = [(i, m) for i, line in enumerate(lines)
                  if (m := re.match(r'^## (\d+)\. (.+)$', line))]
        for n, (i, m) in enumerate(starts):
            end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
            found.append((f'{source_id}-chapter-{m[1]}', i, end, m[2]))
    elif group in ('execution_stages', 'probes'):
        section = '9' if group == 'execution_stages' else '11'
        for i, line in enumerate(lines):
            m = re.match(rf'^## {section}\.(\d+) (.+)$', line)
            if not m:
                continue
            end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith('## ')), len(lines))
            key = f'PCF-{int(m[1]):02}' if group == 'execution_stages' else re.search(
                r'`(PROBE_[A-Z]+_001)`', '\n'.join(lines[i:end]))[1]
            found.append((key, i, end, m[2]))
    elif group == 'metrics':
        # Read only each probe's calculation block, excluding prose/examples.
        # / 仅读取各探针计算块，排除说明及示例。
        for probe in source_inventory(content, 'probes'):
            start, end = probe['source_line'] - 1, probe['source_end_line']
            calc = next(i for i in range(start, end) if lines[i] == '### 计算项')
            fence = next(i for i in range(calc, end) if lines[i] == '```text')
            close = next(i for i in range(fence + 1, end) if lines[i] == '```')
            for i in range(fence + 1, close):
                if lines[i].strip():
                    found.append((f'PCM-{len(found) + 1:02}', i, i + 1, lines[i]))
    else:
        chapter = '18' if source_id == 'execution' else '23'
        start = next(i for i, line in enumerate(lines) if line.startswith(f'## {chapter}. '))
        end = next(i for i in range(start + 1, len(lines)) if re.match(r'^## \d+\. ', lines[i]))
        starts = [i for i in range(start, end) if lines[i].startswith('### 用例')]
        prefix = 'PCE' if source_id == 'execution' else 'PCQ'
        for n, i in enumerate(starts):
            stop = starts[n + 1] if n + 1 < len(starts) else end
            found.append((f'{prefix}-{n + 1:02}', i, stop, lines[i][4:]))
    return [dict(id=key, source_id=source_id, source_line=start + 1,
                 source_end_line=end, source_label=label,
                 excerpt_sha256=hashlib.sha256('\n'.join(lines[start:end]).rstrip().encode('utf-8')).hexdigest(),
                 target_document=target)
            for key, start, end, label in found]


def _file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('missing or outside skill file: ' + relative)
    return path


def validate_pattern_combination_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Validate assets, not runtime enforcement / 校验资产，不证明运行时执行。"""
    errors = []
    try:
        root = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            _file(root, 'references/registry.json').read_text(encoding='utf-8'))
        mapping = json.loads(_file(root, SOURCE_MAP).read_text(encoding='utf-8'))
        for label, record in [('registry', registry.get('pattern_combination_specification', {})), ('source', mapping)]:
            if any(record.get(k) != v for k, v in REGISTRATION.items()):
                errors.append(label + ': registration or readiness drift')
        if mapping.get('source_aliases') != {
            'PATTERN_COMBINATION_0001': 'PATTERN_0053',
            'PATTERN_OBSERVABILITY_PROBE_0001': 'PATTERN_0052',
        }:
            errors.append('source: alias drift')
        if mapping.get('acceptance_status') != 'not_executed' or mapping.get('metric_implementation') != 'specification_only':
            errors.append('source: unsupported runtime validation claim')
        if [s['id'] for s in mapping['sources']] != list(SOURCE_HASHES):
            raise ValueError('expected two ordered source snapshots')
        snapshots = {}
        for source in mapping['sources']:
            key = source['id']
            expected_path = f'references/sources/pattern-combination/{key}.source.txt'
            path = _file(root, source['snapshot_path'])
            if source['snapshot_path'] != expected_path:
                errors.append('source: unexpected snapshot path')
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != SOURCE_HASHES[key] or source['sha256'] != SOURCE_HASHES[key]:
                errors.append('source: snapshot digest drift: ' + key)
            snapshots[key] = raw.decode('utf-8-sig').replace('\r\n', '\n')
        documents = {p: _file(root, p).read_text(encoding='utf-8') for p in (EXECUTION, PROBE, CONTRACT)}
        for group, (source_id, target, count) in GROUPS.items():
            inventory = source_inventory(snapshots[source_id], group)
            if len(inventory) != count or len({i['id'] for i in inventory}) != count:
                errors.append('source: unexpected count or duplicate: ' + group)
            if mapping['inventories'].get(group) != inventory:
                errors.append('source: definition mapping drift: ' + group)
            if group.endswith('_chapters'):
                continue
            ids = [i['id'] for i in inventory]
            prefix = {'execution_stages': 'PCF-', 'probes': 'PROBE_', 'metrics': 'PCM-',
                      'execution_cases': 'PCE-', 'probe_cases': 'PCQ-'}[group]
            rows = [line for line in documents[target].splitlines() if line.startswith('| ' + prefix)]
            if [row.split('|')[1].strip() for row in rows] != ids:
                errors.append('document: missing/repeated/reordered definitions: ' + group)
            for item, row in zip(inventory, rows):
                if item['source_label'] not in row:
                    errors.append('document: source definition drift: ' + item['id'])
                if not re.search('[A-Za-z]{3,}', row.split('|', 2)[-1]) or not re.search('[\u3400-\u9fff]', row):
                    errors.append('document: missing bilingual definition: ' + item['id'])
        patterns = {p['id']: p for p in registry['patterns']}
        composition = patterns.get('PATTERN_0053', {})
        expected = {'reference': EXECUTION, 'observability_reference': PROBE,
                    'source_kind': 'local_seed', 'status': 'draft', 'source_version': '0.1.0',
                    'source_draft_id': 'PATTERN_COMBINATION_0001'}
        if any(composition.get(k) != v for k, v in expected.items()):
            errors.append('registry: composition identity drift')
        for key, section in [('cognition_refs', 'capabilities'), ('topology_refs', 'topologies')]:
            if set(composition.get(key, [])) != {r['id'] for r in registry[section]}:
                errors.append('registry: composition axes drift: ' + key)
        coordinates = re.findall(r'^  - (COG_\w+__TOP_\w+)$', snapshots['execution'], re.M)
        if composition.get('matrix_coordinates') != coordinates:
            errors.append('registry: composition coordinates drift')
        shared = patterns.get('PATTERN_0052', {})
        if shared.get('source_version') != '0.8.0' or shared.get('reference') != 'references/workflow-observability-probes.md':
            errors.append('registry: shared probe protocol replaced')
        if 'PATTERN_0053' not in shared.get('related_pattern_refs', []):
            errors.append('registry: missing shared probe relation')
        if any(alias in patterns for alias in mapping['source_aliases']):
            errors.append('registry: source alias registered as independent pattern')
        if any(c.get('pattern_ref') == 'PATTERN_0053' for c in registry['cells']):
            errors.append('registry: composition must not replace matrix cells')
        chain = next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_CHAIN')
        if chain['status'] != 'extension_candidate' or chain['pattern_ref'] is not None:
            errors.append('registry: source facet promoted without evidence')
        for path, content in documents.items():
            if '\ufffd' in content or '<!-- METRIC_TABLE -->' in content:
                errors.append('document: corrupt or unfinished content: ' + path)
            if 'pattern-combination-contract.md' not in content and path != CONTRACT:
                errors.append('document: missing shared contract: ' + path)
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if re.match(r'[a-zA-Z][\w+.-]*:', link):
                    continue
                relative, _, anchor = link.partition('#')
                dest = _file(root, str(Path(path).parent / relative)) if relative else root / path
                if anchor and f'id="{anchor}"' not in dest.read_text(encoding='utf-8'):
                    errors.append('document: missing anchor: ' + link)
        for path in ('SKILL.md', 'references/pattern-catalog.md', 'references/matrix-index.md',
                     'references/workflow-observability-probes.md', 'references/evaluation-governance.md'):
            content = _file(root, path).read_text(encoding='utf-8')
            if 'pattern-combination-' not in content:
                errors.append('navigation: missing composition route: ' + path)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, StopIteration) as error:
        errors.append('pattern_combination_specification: ' + str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_pattern_combination_assets(parser.parse_args().skill_dir)
    for error in errors:
        print(error)
    print(f'Pattern combination assets / 模式组合资产: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
