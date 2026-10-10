"""Composition source integrity tests / 模式组合来源完整性测试。

Test omission, tampering and unsupported promotion on isolated copies.
/ 在隔离副本检查遗漏、篡改与不受支持的晋升，不执行来源业务用例。
"""

import json
from pathlib import Path
import re
import runpy
import shutil

import pytest


SKILL = Path(__file__).resolve().parents[1] / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/validate_pattern_combination_docs.py'))
validate = MODULE['validate_pattern_combination_assets']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


@pytest.fixture
def assets(tmp_path):
    target = tmp_path / 'skill'
    paths = [MODULE[k] for k in ('EXECUTION', 'PROBE', 'CONTRACT', 'SOURCE_MAP')]
    paths += ['references/registry.json', 'SKILL.md', 'references/pattern-catalog.md',
              'references/matrix-index.md', 'references/workflow-observability-probes.md',
              'references/evaluation-governance.md']
    paths += [s['snapshot_path'] for s in load(SKILL / MODULE['SOURCE_MAP'])['sources']]
    for key in ('EXECUTION', 'PROBE', 'CONTRACT'):
        document = MODULE[key]
        for link in re.findall(r'\]\(([^)]+)\)', (SKILL / document).read_text(encoding='utf-8')):
            if not link.startswith('#') and not re.match(r'[a-zA-Z][\w+.-]*:', link):
                paths.append((Path(document).parent / link.split('#')[0]).as_posix())
    for relative in set(paths):
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, dest)
    return target


def test_validates_without_writing(assets):
    before = {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}
    assert validate(assets) == []
    assert before == {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_source_inventory_omission_is_detected(assets, group):
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    mapping['inventories'][group].pop()
    save(path, mapping)
    assert any('definition mapping drift: ' + group in e for e in validate(assets))


@pytest.mark.parametrize('group', ['execution_stages', 'probes', 'metrics', 'execution_cases', 'probe_cases'])
def test_bare_citation_cannot_replace_definition(assets, group):
    item = load(assets / MODULE['SOURCE_MAP'])['inventories'][group][-1]
    path = assets / item['target_document']
    content = re.sub(rf'^\| {re.escape(item["id"])} \|.*\n', '', path.read_text(encoding='utf-8'), flags=re.M)
    path.write_text(content + '\nSee / 参见: ' + item['id'] + '\n', encoding='utf-8')
    assert any('definitions: ' + group in e for e in validate(assets))


def test_changed_formula_is_rejected(assets):
    path = assets / MODULE['PROBE']
    text = path.read_text(encoding='utf-8').replace('已启动的必需分支数量', '所有分支数量')
    path.write_text(text, encoding='utf-8')
    assert any('source definition drift: PCM-04' in e for e in validate(assets))


def test_changed_source_rejected_even_with_updated_map_digest(assets):
    import hashlib
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    source = mapping['sources'][0]
    snapshot = assets / source['snapshot_path']
    snapshot.write_bytes(snapshot.read_bytes() + b'\nchanged\n')
    source['sha256'] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    save(path, mapping)
    assert any('snapshot digest drift' in e for e in validate(assets))


@pytest.mark.parametrize('mutation', ['replace_shared_protocol', 'promote_cell', 'alias_pattern', 'claim_implemented'])
def test_registration_preserves_boundaries(assets, mutation):
    path = assets / 'references/registry.json'
    registry = load(path)
    if mutation == 'replace_shared_protocol':
        next(p for p in registry['patterns'] if p['id'] == 'PATTERN_0052')['source_version'] = '0.1.0'
    elif mutation == 'promote_cell':
        next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_CHAIN')['pattern_ref'] = 'PATTERN_0053'
    elif mutation == 'alias_pattern':
        registry['patterns'].append({'id': 'PATTERN_COMBINATION_0001'})
    else:
        registry['pattern_combination_specification']['implementation_status'] = 'deployed'
    save(path, registry)
    assert validate(assets)


def test_cannot_claim_business_acceptance(assets):
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    mapping['acceptance_status'] = 'passed'
    save(path, mapping)
    assert any('unsupported runtime validation' in e for e in validate(assets))


def test_source_path_cannot_escape_skill(assets):
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    mapping['sources'][0]['snapshot_path'] = '../outside.txt'
    (assets.parent / 'outside.txt').write_text('outside', encoding='utf-8')
    save(path, mapping)
    assert any('outside skill file' in e for e in validate(assets))


def test_broken_navigation_anchor_is_rejected(assets):
    path = assets / MODULE['PROBE']
    path.write_text(path.read_text(encoding='utf-8').replace('(#metrics)', '(#missing)'), encoding='utf-8')
    assert any('missing anchor' in e for e in validate(assets))
