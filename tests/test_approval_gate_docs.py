"""Approval asset integrity tests / 审批资产完整性测试。

These exercise source/view validation and safe synchronization, not live
approval, receipt consumption or the 55 integration requirements.
/ 验证来源视图校验及安全同步，不执行真实审批、回执消费或 55 项集成验收。
"""

import hashlib
import json
from pathlib import Path
import runpy
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/sync_approval_gate_docs.py'))
validate = MODULE['validate_approval_assets']
sync = MODULE['sync']
SOURCE_MAP = MODULE['SOURCE_MAP']
PEERS = [MODULE[key] for key in ('EXECUTION', 'PROBE', 'CONTRACT')]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def peer_bytes(target):
    return {relative: (target / relative).read_bytes() for relative in PEERS}


@pytest.fixture
def assets(tmp_path):
    target = tmp_path / 'skill'
    source = read(SKILL / SOURCE_MAP)
    paths = PEERS + [SOURCE_MAP, MODULE['DESIGN_CARD'], MODULE['PROBE_CARD'],
                     'references/registry.json'] + [item['snapshot_path'] for item in source['sources']]
    for relative in paths:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, path)
    assert validate(target) == []
    return target


def test_real_source_inventory_and_views_validate_read_only():
    before = peer_bytes(SKILL)
    assert validate(SKILL) == []
    assert peer_bytes(SKILL) == before


@pytest.mark.parametrize('group', list(MODULE['GROUPS']))
def test_omission_cannot_hide_a_source_requirement_or_partially_publish(assets, group):
    path = assets / SOURCE_MAP
    source = read(path)
    source['inventories'][group].pop()
    write(path, source)
    before = peer_bytes(assets)
    with pytest.raises(ValueError, match='incomplete inventory'):
        sync(assets)
    assert validate(assets)
    assert peer_bytes(assets) == before


@pytest.mark.parametrize('mutation', ['formula', 'nested_field', 'excerpt', 'duplicate',
                                     'translation', 'metric_readiness', 'case_result'])
def test_mapping_corruption_and_unearned_readiness_are_rejected(assets, mutation):
    path = assets / SOURCE_MAP
    source = read(path)
    rows = source['inventories']
    if mutation == 'formula':
        rows['metrics'][0]['formula_zh'] = '审批通过率就是业务成功率'
    elif mutation == 'nested_field':
        rows['objects'][0]['fields'].remove('action.tool_version')
    elif mutation == 'excerpt':
        rows['execution_steps'][0]['source_end_line'] -= 1
    elif mutation == 'duplicate':
        rows['probe_checks'][1] = rows['probe_checks'][0]
    elif mutation == 'translation':
        rows['execution_steps'][0]['summary_zh'] = ''
    elif mutation == 'metric_readiness':
        rows['metrics'][0]['implementation'] = 'deployed'
    else:
        rows['probe_cases'][0]['integration_status'] = 'passed'
    write(path, source)
    before = peer_bytes(assets)
    with pytest.raises(ValueError):
        sync(assets)
    assert validate(assets)
    assert peer_bytes(assets) == before


def mutate_snapshot(target, transform, *, rehash):
    path = target / SOURCE_MAP
    source = read(path)
    item = source['sources'][0]
    snapshot = target / item['snapshot_path']
    data = transform(snapshot.read_bytes())
    snapshot.write_bytes(data)
    if rehash:
        item['sha256'] = hashlib.sha256(data).hexdigest()
        write(path, source)


def test_source_bytes_cannot_drift_unnoticed(assets):
    mutate_snapshot(assets, lambda data: data + b'\n', rehash=False)
    assert any('snapshot digest drift' in error for error in validate(assets))


def test_new_source_stage_detected_independently_of_fixed_mapping(assets):
    mutate_snapshot(assets, lambda data: data.replace(
        b'# 14. ', '## 13.21 新阶段\n\n新增要求。\n\n# 14. '.encode('utf-8'), 1), rehash=True)
    assert validate(assets)
    with pytest.raises(ValueError):
        sync(assets)


def test_source_version_mismatch_rejected_even_with_new_hash(assets):
    mutate_snapshot(assets, lambda data: data.replace(
        b'contract_version: 1.0.0', b'contract_version: 2.0.0', 1), rehash=True)
    assert any('source version' in error for error in validate(assets))


def test_source_path_cannot_escape_evidence_directory(assets):
    path = assets / SOURCE_MAP
    source = read(path)
    source['sources'][0]['snapshot_path'] = '../outside.source.txt'
    write(path, source)
    assert any('outside approval evidence' in error for error in validate(assets))


@pytest.mark.parametrize('mutation', ['identity', 'maturity', 'evidence_count', 'domain_count', 'runtime'])
def test_registration_cannot_rename_or_promote_documentation(assets, mutation):
    path = assets / 'references/registry.json'
    registry = read(path)
    cell = next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_ROUTING')
    if mutation == 'identity':
        cell['pattern_ref'] = 'PATTERN_GOVERNANCE_APPROVAL_0001'
    elif mutation == 'maturity':
        cell['maturity'] = 'operational'
    elif mutation == 'runtime':
        cell['approval_specification']['implementation_status'] = 'deployed'
    else:
        cell['local_evidence_count' if mutation == 'evidence_count' else 'domain_count'] += 1
    write(path, registry)
    assert validate(assets)


@pytest.mark.parametrize('group', list(MODULE['GROUPS']))
def test_deleted_table_definition_is_not_replaced_by_an_inline_citation(assets, group):
    _, prefix, _, target = MODULE['GROUPS'][group]
    path = assets / target
    content = path.read_text(encoding='utf-8')
    content = '\n'.join(line for line in content.split('\n') if not line.startswith('| ' + prefix + '01 |'))
    path.write_text(content + '\nCitation / 引用: ' + prefix + '01\n', encoding='utf-8')
    assert any('view drift' in error for error in validate(assets))


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'reversed', 'overlap'])
def test_invalid_peer_markers_block_all_writes(assets, mutation):
    path = assets / MODULE['PROBE']
    content = path.read_text(encoding='utf-8')
    start, end = '<!-- approval:metrics:start -->', '<!-- approval:metrics:end -->'
    if mutation == 'missing':
        content = content.replace(end, '')
    elif mutation == 'duplicate':
        content += '\n' + start
    elif mutation == 'reversed':
        content = content.replace(start, 'TEMP').replace(end, start).replace('TEMP', end)
    else:
        check_end = '<!-- approval:probe_checks:end -->'
        content = content.replace(check_end, 'TEMP').replace(start, check_end).replace('TEMP', start)
    path.write_text(content, encoding='utf-8')
    manifest = read(assets / SOURCE_MAP)
    manifest['inventories']['execution_steps'][0]['summary_en'] += ' Pending revision.'
    write(assets / SOURCE_MAP, manifest)
    before = peer_bytes(assets)
    with pytest.raises(ValueError, match='marker'):
        sync(assets)
    assert peer_bytes(assets) == before


def test_refresh_is_idempotent_and_preserves_authored_prose(assets):
    note = '\nLocal interpretation / 本地解释。\n'
    for relative in PEERS:
        path = assets / relative
        path.write_text(path.read_text(encoding='utf-8') + note, encoding='utf-8')
    path = assets / SOURCE_MAP
    source = read(path)
    source['inventories']['execution_steps'][0]['summary_en'] += ' This is not runtime evidence.'
    write(path, source)
    assert validate(assets)
    sync(assets)
    assert validate(assets) == []
    before = peer_bytes(assets)
    assert all(content.decode('utf-8').replace('\r\n', '\n').endswith(note) for content in before.values())
    sync(assets)
    assert before == peer_bytes(assets)


def test_broken_json_returns_diagnostic(assets):
    (assets / SOURCE_MAP).write_text('{broken', encoding='utf-8')
    assert validate(assets)[0].startswith('approval_specification:')


def test_source_field_inventory_includes_nested_security_bindings():
    source = read(SKILL / SOURCE_MAP)
    proposal = source['inventories']['objects'][0]
    assert {'actor.delegation_chain', 'action.tool_version', 'action.environment',
            'targets[].target_version', 'scope.currency', 'proposal_digest'} <= set(proposal['fields'])
