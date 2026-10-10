"""Governance provenance validation / 治理来源校验。

Exercise the asset validator's failure paths, not business authorization or
the 54 unexecuted integration scenarios. / 验证资产校验器的失败路径，不验证业务授权，
也不代表 54 项集成场景已运行。
"""

import hashlib
import json
from pathlib import Path
import runpy
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/validate_governance_docs.py'))
validate = MODULE['validate_governance_assets']
SOURCE_MAP = MODULE['SOURCE_MAP']


@pytest.fixture
def assets(tmp_path):
    target = tmp_path / 'skill'
    paths = [MODULE[key] for key in ('EXECUTION', 'PROBE', 'CONTRACT', 'SOURCE_MAP')]
    paths.append('references/registry.json')
    registry = json.loads((SKILL / paths[-1]).read_text(encoding='utf-8'))
    for cell in registry['cells']:
        if cell['capability_ref'] == 'COG_GOVERNANCE':
            paths.extend([cell['design_path'], cell['observability_path']])
    source = json.loads((SKILL / SOURCE_MAP).read_text(encoding='utf-8'))
    paths.extend(item['snapshot_path'] for item in source['sources'])
    for relative in paths:
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, output)
    return target


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def test_complete_assets_validate_without_modification(assets):
    before = {path.relative_to(assets): path.read_bytes() for path in assets.rglob('*') if path.is_file()}
    assert validate(assets) == []
    assert before == {path.relative_to(assets): path.read_bytes() for path in assets.rglob('*') if path.is_file()}


@pytest.mark.parametrize('group', list(MODULE['GROUPS']))
def test_omitted_mapping_cannot_hide_a_source_requirement(assets, group):
    path = assets / SOURCE_MAP
    source = load(path)
    source['inventories'][group].pop()
    save(path, source)
    assert any('definition drift: ' + group in error for error in validate(assets))


def test_source_change_is_rejected_before_trusting_its_inventory(assets):
    source = load(assets / SOURCE_MAP)
    path = assets / source['sources'][0]['snapshot_path']
    path.write_bytes(path.read_bytes() + b'\nChanged source\n')
    assert any('snapshot digest drift' in error for error in validate(assets))


def test_disagreeing_shared_protocols_rejected_even_after_hash_update(assets):
    map_path = assets / SOURCE_MAP
    source = load(map_path)
    item = source['sources'][1]
    path = assets / item['snapshot_path']
    data = path.read_bytes().replace(b'base_state_revision: 12', b'base_state_revision: 13')
    path.write_bytes(data)
    item['sha256'] = hashlib.sha256(data).hexdigest()
    save(map_path, source)
    assert any('shared protocols differ' in error for error in validate(assets))


def test_snapshot_cannot_escape_evidence_directory(assets):
    path = assets / SOURCE_MAP
    source = load(path)
    source['sources'][0]['snapshot_path'] = '../../elsewhere.txt'
    save(path, source)
    assert any('outside governance evidence' in error for error in validate(assets))


@pytest.mark.parametrize('group', list(MODULE['GROUPS']))
def test_deleted_definition_is_detected_even_when_id_remains_in_prose(assets, group):
    prefix, _, _, target = MODULE['GROUPS'][group]
    path = assets / target
    # Remove all definition appearances, then leave an ordinary citation.
    # / 删除定义后留下普通引用，不能把引用当完整覆盖。
    content = path.read_text(encoding='utf-8').replace(prefix + '01', 'REMOVED_01')
    path.write_text(content + '\nCross-reference / 交叉引用: ' + prefix + '01\n', encoding='utf-8')
    assert any('definitions: ' + group in error for error in validate(assets))


@pytest.mark.parametrize('field,value', [('acceptance_status', 'passed'), ('metric_implementation', 'deployed')])
def test_asset_checks_cannot_claim_business_validation(assets, field, value):
    path = assets / SOURCE_MAP
    source = load(path)
    source[field] = value
    save(path, source)
    assert any('unsupported runtime' in error for error in validate(assets))


@pytest.mark.parametrize('mutation', ['identity', 'maturity', 'readiness', 'missing_link'])
def test_registration_and_navigation_drift_is_detected(assets, mutation):
    path = assets / 'references/registry.json'
    registry = load(path)
    cell = next(cell for cell in registry['cells'] if cell['id'] == 'CELL_GOVERNANCE_ROUTING')
    if mutation == 'identity':
        cell['pattern_ref'] = 'PATTERN_GOVERNANCE_0036'
    elif mutation == 'maturity':
        cell['maturity'] = 'operational'
    elif mutation == 'readiness':
        registry['governance_specification']['implementation_status'] = 'deployed'
    else:
        document = assets / cell['design_path']
        document.write_text(document.read_text(encoding='utf-8').replace('governance-execution-flow.md', 'missing.md'), encoding='utf-8')
    save(path, registry)
    assert validate(assets)


def test_corrupt_or_missing_manifest_returns_diagnostic(assets):
    (assets / SOURCE_MAP).write_text('{invalid', encoding='utf-8')
    assert validate(assets)[0].startswith('governance_specification:')
