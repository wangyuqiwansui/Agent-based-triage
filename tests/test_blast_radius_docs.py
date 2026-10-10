"""Source and registration integrity / 来源及注册完整性。

Mutate isolated assets to exercise validator failure paths. These checks do not
run the documented business scenarios. / 在隔离资产中注入异常验证失败路径，
不运行文档内业务场景。
"""

import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil

import pytest


SKILL = Path(__file__).resolve().parents[1] / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/validate_blast_radius_docs.py'))
validate = MODULE['validate_blast_radius_assets']
SOURCE_MAP = MODULE['SOURCE_MAP']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


@pytest.fixture
def assets(tmp_path):
    target = tmp_path / 'skill'
    documents = [MODULE[key] for key in ('EXECUTION', 'PROBE', 'CONTRACT', 'DESIGN', 'CARD')]
    paths = set(documents + [SOURCE_MAP, 'references/registry.json'])
    paths.update(item['snapshot_path'] for item in load(SKILL / SOURCE_MAP)['sources'])
    for relative in documents:
        for link in re.findall(r'\]\(([^)]+)\)', (SKILL / relative).read_text(encoding='utf-8')):
            if not link.startswith('#') and not re.match(r'[a-zA-Z][\w+.-]*:', link):
                paths.add((Path(relative).parent / link.split('#')[0]).as_posix())
    for relative in paths:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, path)
    return target


def test_assets_validate_readonly(assets):
    before = {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}
    assert validate(assets) == []
    assert before == {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_omitted_mapping_cannot_hide_requirement(assets, group):
    path = assets / SOURCE_MAP
    source = load(path)
    source['inventories'][group].pop()
    save(path, source)
    assert any('definition mapping drift: ' + group in error for error in validate(assets))


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_cross_reference_cannot_replace_definition(assets, group):
    prefix, _, _, target, _ = MODULE['GROUPS'][group]
    path = assets / target
    content = path.read_text(encoding='utf-8')
    content = re.sub(rf'^\| {prefix}01 \|.*\n', '', content, flags=re.M)
    path.write_text(content + '\nCitation / 引用: ' + prefix + '01\n', encoding='utf-8')
    assert any('definitions: ' + group in error for error in validate(assets))


def test_changed_source_bytes_rejected(assets):
    source = load(assets / SOURCE_MAP)
    path = assets / source['sources'][0]['snapshot_path']
    path.write_bytes(path.read_bytes() + b'\nchanged\n')
    assert any('snapshot digest drift' in error for error in validate(assets))


def test_source_removal_detected_even_with_updated_hash_and_mapping(assets):
    path = assets / SOURCE_MAP
    source = load(path)
    item = source['sources'][0]
    snapshot = assets / item['snapshot_path']
    content = snapshot.read_text(encoding='utf-8')
    content = re.sub(r'^\| 14\. .*\n', '', content, flags=re.M)
    snapshot.write_text(content, encoding='utf-8')
    item['sha256'] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    source['inventories']['execution_steps'] = MODULE['source_inventory'](content, 'execution_steps')
    save(path, source)
    assert any('unexpected definition count: execution_steps' in error for error in validate(assets))


@pytest.mark.parametrize('field,value', [('acceptance_status', 'passed'), ('metric_implementation', 'deployed')])
def test_asset_checks_do_not_claim_runtime_acceptance(assets, field, value):
    path = assets / SOURCE_MAP
    source = load(path)
    source[field] = value
    save(path, source)
    assert any('unsupported runtime' in error for error in validate(assets))


@pytest.mark.parametrize('mutation', ['maturity', 'identity', 'readiness', 'alias', 'duplicate_pattern'])
def test_registration_drift_rejected(assets, mutation):
    path = assets / 'references/registry.json'
    registry = load(path)
    cell = next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_HIERARCHY')
    if mutation == 'maturity':
        cell['maturity'] = 'operational'
    elif mutation == 'identity':
        cell['pattern_ref'] = 'PATTERN_GOVERNANCE_BLAST_RADIUS_0001'
    elif mutation == 'readiness':
        registry['blast_radius_specification']['implementation_status'] = 'deployed'
    elif mutation == 'alias':
        source = load(assets / SOURCE_MAP)
        source['source_aliases']['pattern'] = ['PATTERN_0050']
        save(assets / SOURCE_MAP, source)
    else:
        registry['patterns'].append({'id': 'PATTERN_GOVERNANCE_BLAST_RADIUS_0001'})
    save(path, registry)
    assert validate(assets)


def test_snapshot_path_cannot_escape_evidence_directory(assets):
    path = assets / SOURCE_MAP
    source = load(path)
    source['sources'][0]['snapshot_path'] = '../outside.txt'
    (assets.parent / 'outside.txt').write_text('outside', encoding='utf-8')
    save(path, source)
    assert any('outside skill' in error for error in validate(assets))


def test_broken_navigation_anchor_rejected(assets):
    path = assets / MODULE['DESIGN']
    path.write_text(path.read_text(encoding='utf-8').replace('#execution-steps', '#absent'), encoding='utf-8')
    assert any('missing anchor' in error for error in validate(assets))


@pytest.mark.parametrize('payload', ['{bad', 'null', '[]'])
def test_malformed_manifest_returns_diagnostic(assets, payload):
    (assets / SOURCE_MAP).write_text(payload, encoding='utf-8')
    assert validate(assets)
