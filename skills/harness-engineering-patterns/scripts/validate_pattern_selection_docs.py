"""Pattern selection asset validation / 模式选型资产校验。

Usage / 用法: python validate_pattern_selection_docs.py [skill_dir]
Workflow / 流程: Re-extract immutable evidence inventories, check provenance,
identity, definitions and links. / 重提取不可变证据目录，检查来源、身份、定义及链接。
Constraints / 约束: Read-only asset checks; no runtime or business validation.
/ 只读资产检查，不执行运行时或业务验收。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXECUTION = 'references/pattern-selection-execution-flow.md'
PROBE = 'references/pattern-selection-observability-probes.md'
CONTRACT = 'references/pattern-selection-contract.md'
SOURCE_MAP = 'references/pattern-selection-source-map.json'
REGISTRATION = {
    'version': '0.1.0', 'status': 'draft',
    'implementation_status': 'specification_only',
    'profile': 'pattern-selection/0.1.0',
    'probe_pattern_ref': 'PATTERN_0052',
    'entry_reference': 'references/pattern-selection-card.md',
    'execution_reference': EXECUTION, 'observability_reference': PROBE,
    'interaction_contract_reference': CONTRACT, 'source_map_reference': SOURCE_MAP,
}
ALIASES = {
    'selection': ['PATTERN_SELECTION_0001', 'SKILL_SELECTION_0001'],
    'probe': ['PATTERN_OBSERVABILITY_0001', 'SKILL_OBSERVABILITY_0001'],
}
GROUPS = {
    'execution_steps': ('execution', EXECUTION, 11),
    'difficulties': ('execution', EXECUTION, 12),
    'probes': ('probe', PROBE, 16),
    'metrics': ('probe', PROBE, 68),
    'anomalies': ('probe', PROBE, 30),
    'execution_cases': ('execution', EXECUTION, 10),
    'probe_cases': ('probe', PROBE, 14),
}


def source_inventory(content: str, group: str) -> list[dict]:
    """Extract source sections with byte-independent line digests / 提取带行内容摘要的来源章节。"""
    source, target, _ = GROUPS[group]
    lines = content.replace('\r\n', '\n').splitlines()
    found = []
    patterns = {
        'execution_steps': r'^## (S\d+)\. (.+)$',
        'difficulties': r'^\| (D\d+) \| ([^|]+) \|',
        'probes': r'^## (PRB-\d+) (.+)$',
        'metrics': r'^\| (MTR-\d+) \| ([^|]+) \|',
        'anomalies': r'^\| (ANO-\d+) \| ([^|]+) \|',
    }
    if group.endswith('_cases'):
        heading = '### 最低验收用例' if source == 'execution' else '### 最低测试集'
        start = lines.index(heading)
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('# '))
        prefix = 'SEL-CASE' if source == 'execution' else 'OBS-CASE'
        for index in range(start + 1, end):
            match = re.match(r'^\d+\. (.+)$', lines[index])
            if match:
                found.append((f'{prefix}-{len(found) + 1:02}', match[1], index, index + 1))
    else:
        for index, line in enumerate(lines):
            match = re.match(patterns[group], line)
            if match:
                end = index + 1
                if group in ('execution_steps', 'probes'):
                    end = next((i for i in range(index + 1, len(lines))
                                if re.match(r'^#{1,2} ', lines[i])), len(lines))
                found.append((match[1], match[2].strip(), index, end))
    return [dict(id=key, source_id=source, source_line=start + 1, source_end_line=end,
                 source_label=label,
                 excerpt_sha256=hashlib.sha256('\n'.join(lines[start:end]).rstrip().encode('utf-8')).hexdigest(),
                 target_document=target)
            for key, label, start, end in found]


def source_events(content: str) -> list[str]:
    """Unique standalone event vocabulary / 去重独立事件词汇。"""
    return list(dict.fromkeys(re.findall(r'^(?:selection|workflow|probe)\.[a-z_.]+$', content, re.M)))


def _file(root: Path, path: str) -> Path:
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('missing or outside skill: ' + path)
    return resolved


def validate_pattern_selection_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Check documentation integrity, never claim execution / 仅校验文档完整性，不宣称执行。"""
    errors = []
    try:
        root = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            _file(root, 'references/registry.json').read_text(encoding='utf-8'))
        mapping = json.loads(_file(root, SOURCE_MAP).read_text(encoding='utf-8'))
        for label, record in [('registry', registry.get('pattern_selection_specification', {})), ('source', mapping)]:
            if any(record.get(k) != v for k, v in REGISTRATION.items()):
                errors.append(label + ': registration or implementation status drift')
            for key in ('name_en', 'name_zh', 'description_en', 'description_zh'):
                if not isinstance(record.get(key), str) or not record[key].strip():
                    errors.append(label + ': missing bilingual metadata: ' + key)
        if mapping.get('source_aliases') != ALIASES:
            errors.append('source: alias drift')
        if mapping.get('acceptance_status') != 'not_executed':
            errors.append('source: unsupported business validation claim')
        stable = [p for p in registry['patterns'] if p['id'] == 'PATTERN_0052']
        if len(stable) != 1 or stable[0]['reference'] != 'references/workflow-observability-probes.md':
            errors.append('registry: existing probe identity changed')
        aliases = sum(ALIASES.values(), [])
        if any(p['id'] in aliases for p in registry['patterns']):
            errors.append('registry: source alias promoted as a new pattern')
        if [s['id'] for s in mapping['sources']] != ['execution', 'probe']:
            raise ValueError('expected two ordered sources')
        snapshots = {}
        for source in mapping['sources']:
            path = _file(root, source['snapshot_path'])
            if not path.is_relative_to(root / 'references/sources/pattern-selection'):
                raise ValueError('source outside dedicated evidence directory')
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != source['sha256']:
                errors.append('source: digest drift: ' + source['id'])
            snapshots[source['id']] = raw.decode('utf-8-sig').replace('\r\n', '\n')
        documents = {p: _file(root, p).read_text(encoding='utf-8')
                     for p in (EXECUTION, PROBE, CONTRACT, REGISTRATION['entry_reference'])}
        for group, (source_id, target, count) in GROUPS.items():
            inventory = source_inventory(snapshots[source_id], group)
            ids = [item['id'] for item in inventory]
            if len(ids) != count or len(set(ids)) != count:
                errors.append('source: unexpected count or duplicate: ' + group)
            if mapping['inventories'].get(group) != inventory:
                errors.append('source: section mapping drift: ' + group)
            for item in inventory:
                rows = [line for line in documents[target].splitlines() if line.startswith('| ' + item['id'] + ' |')]
                if len(rows) != 1 or item['source_label'] not in rows[0]:
                    errors.append('document: missing/repeated definition or lost label: ' + item['id'])
                elif group in ('metrics', 'anomalies'):
                    original = snapshots[source_id].splitlines()[item['source_line'] - 1]
                    if any(part.strip() not in rows[0] for part in original.split('|')[2:-1]):
                        errors.append('document: source definition drift: ' + item['id'])
        vocabulary = {key: source_events(value) for key, value in snapshots.items()}
        if mapping.get('source_events') != vocabulary:
            errors.append('source: event vocabulary drift')
        expected_events = list(dict.fromkeys(vocabulary['probe'] + vocabulary['execution']))
        if source_events(documents[PROBE]) != expected_events:
            errors.append('document: event vocabulary drift')
        expected_alias = {'workflow.response.generated': 'workflow.response.drafted'}
        if mapping.get('event_aliases') != expected_alias:
            errors.append('source: response alias drift')
        for path, content in documents.items():
            if '\ufffd' in content or '<!-- SELECTION_' in content:
                errors.append('document: corrupt Unicode or unfinished block: ' + path)
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if re.match(r'[a-zA-Z][\w+.-]*:', link):
                    continue
                location, _, anchor = link.partition('#')
                destination = _file(root, str(Path(path).parent / location)) if location else root / path
                if anchor and destination.name.startswith('pattern-selection-'):
                    if f'id="{anchor}"' not in destination.read_text(encoding='utf-8'):
                        errors.append('document: missing anchor: ' + link)
        for path in (EXECUTION, PROBE):
            if '(pattern-selection-contract.md)' not in documents[path]:
                errors.append('document: missing shared contract link: ' + path)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, StopIteration) as error:
        errors.append('pattern_selection_specification: ' + str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_pattern_selection_assets(parser.parse_args().skill_dir)
    for error in errors:
        print(error)
    print(f'Pattern selection assets / 模式选型资产: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
