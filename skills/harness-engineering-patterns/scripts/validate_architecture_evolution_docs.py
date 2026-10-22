"""Architecture evolution asset validation / 架构演化资产校验。

Usage / 用法: python validate_architecture_evolution_docs.py [skill_dir]
Workflow / 流程: Verify source integrity, complete provenance, registration and
local navigation. / 核验来源完整性、完整映射、注册与本地导航。
Constraints / 约束: Read-only asset checks, not business acceptance or a release
controller. / 只读资产检查，不是业务验收或发布控制器。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote


SOURCE_MAP = 'references/architecture-evolution-source-map.json'
SOURCE_HASHES = {
    'execution': 'e75f0dc5a3a67ce449fe56a6c105a6e342c05d224368411a3dd0b12dace6711f',
    'probe': '62fd8a63b1f4d057152c04e3d8d9cf0f3f02f84c087e7d66c346530bf62118e6',
}
REFERENCES = {
    'execution_reference': 'references/architecture-evolution-execution-flow.md',
    'observability_reference': 'references/architecture-evolution-observability-probes.md',
    'interaction_contract_reference': 'references/architecture-evolution-contract.md',
    'source_map_reference': SOURCE_MAP,
}


def _file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('missing or outside skill file: ' + relative)
    return path


def source_inventory(content: str, source_id: str, group: str) -> list[dict]:
    """Extract source sections independently / 独立提取来源章节。"""
    lines = content.splitlines()
    pattern = r'^## (\d+)\. (.+)$' if group == 'chapters' else r'^### 第[^：]+步：(.+)$'
    matches = [(i, m) for i, line in enumerate(lines) if (m := re.match(pattern, line))]
    target = REFERENCES['execution_reference' if source_id == 'execution' else 'observability_reference']
    entries = []
    for n, (start, match) in enumerate(matches):
        end = next((i for i in range(start + 1, len(lines)) if
                    lines[i].startswith('## ') or
                    (group == 'steps' and lines[i].startswith('### '))), len(lines))
        entries.append(dict(
            id=f'{source_id}-{group}-{n + 1:02}', source_id=source_id,
            source_line=start + 1, source_end_line=end,
            source_label=match[2] if group == 'chapters' else match[1],
            excerpt_sha256=hashlib.sha256('\n'.join(lines[start:end]).rstrip().encode('utf-8')).hexdigest(),
            target_document=target,
        ))
    return entries


def _anchors(content: str) -> set[str]:
    result = set(re.findall(r'<a\s+id=["\']([^"\']+)', content))
    for heading in re.findall(r'^#{1,6}\s+(.+)$', content, re.M):
        # GFM heading slugs; authored explicit IDs remain preferable.
        # / GFM 标题锚点；维护文档优先使用显式 ID。
        slug = re.sub(r'[^\w\s-]', '', heading.lower()).replace(' ', '-')
        result.add(slug)
    return result


def validate_architecture_evolution_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Validate retained evidence and discoverability / 校验保留证据与可发现性。"""
    errors = []
    try:
        root = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            _file(root, 'references/registry.json').read_text(encoding='utf-8'))
        mapping = json.loads(_file(root, SOURCE_MAP).read_text(encoding='utf-8'))
        registration = registry.get('architecture_evolution_specification', {})
        expected = dict(REFERENCES, pattern_ref='PATTERN_0054', version='0.2.0',
                        status='draft', implementation_status='specification_only',
                        shared_probe_pattern_ref='PATTERN_0052', shared_probe_version='0.8.0')
        for label, record in [('registry', registration), ('source map', mapping)]:
            if any(record.get(key) != value for key, value in expected.items()):
                errors.append(label + ': identity or readiness drift')
            for key in ('name_en', 'name_zh', 'description_en', 'description_zh'):
                if not record.get(key) or record.get(key) != registration.get(key):
                    errors.append(label + ': bilingual metadata mismatch: ' + key)
        if (mapping.get('acceptance_status') != 'not_executed'
                or mapping.get('metric_implementation') != 'specification_only'):
            errors.append('unsupported runtime validation')
        patterns = registry['patterns']
        matches = [p for p in patterns if p['id'] == 'PATTERN_0054']
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in {
            'status': 'draft', 'source_kind': 'local_seed', 'source_version': '0.1.0',
            'specification_version': '0.2.0', 'reference': REFERENCES['execution_reference'],
            'observability_reference': REFERENCES['observability_reference'],
        }.items()):
            errors.append('architecture evolution pattern registration drift')
        if any(c.get('pattern_ref') == 'PATTERN_0054' for c in registry['cells']):
            errors.append('cross-cell specification cannot replace a matrix cell')
        shared = [p for p in patterns if p['id'] == 'PATTERN_0052']
        if len(shared) != 1 or shared[0].get('source_version') != '0.8.0':
            errors.append('shared probe protocol drift')

        sources = mapping['sources']
        if sorted(s['id'] for s in sources) != sorted(SOURCE_HASHES):
            errors.append('source set drift')
        expected_inventories = {}
        for source in sources:
            source_id = source['id']
            path = _file(root, source['snapshot_path'])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != source.get('sha256') or digest != SOURCE_HASHES.get(source_id):
                errors.append('snapshot digest drift: ' + source_id)
            for group in ('chapters', 'steps'):
                expected_inventories[f'{source_id}_{group}'] = source_inventory(
                    path.read_text(encoding='utf-8'), source_id, group)
        if mapping['inventories'] != expected_inventories:
            errors.append('source inventory drift')
        source_ids = {item['id'] for group in expected_inventories.values() for item in group}
        for refinement in mapping['refinements']:
            if not refinement['source_refs'] or not set(refinement['source_refs']) <= source_ids:
                errors.append('unresolved refinement provenance: ' + refinement['id'])
            _file(root, refinement['target_document'])

        for relative in REFERENCES.values():
            _file(root, relative)
        for relative in list(REFERENCES.values())[:3]:
            path = _file(root, relative)
            content = path.read_text(encoding='utf-8')
            for href in re.findall(r'\]\(([^)]+)\)', content):
                if re.match(r'^[a-zA-Z][\w+.-]*:', href):
                    continue
                target, _, anchor = unquote(href).partition('#')
                linked = _file(root, str(path.parent.relative_to(root) / target)) if target else path
                if anchor and anchor not in _anchors(linked.read_text(encoding='utf-8')):
                    errors.append(f'missing anchor: {relative} -> {href}')
        for relative in ('SKILL.md', 'references/pattern-catalog.md', 'references/matrix-index.md'):
            if 'architecture-evolution-execution-flow.md' not in _file(root, relative).read_text(encoding='utf-8'):
                errors.append('missing navigation: ' + relative)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_architecture_evolution_assets(parser.parse_args().skill_dir)
    for error in errors:
        print('ERROR / 错误: ' + error)
    print(f'Architecture evolution assets / 架构演化资产: {len(errors)} error(s) / 错误')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
