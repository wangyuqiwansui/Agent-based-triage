"""Handoff source fidelity and bounded maintenance / 交接链来源保真与有界维护。

Usage / 用法: python -m pytest tests/test_handoff_chain_docs.py
Workflow / 流程: mutate isolated copies and require publication to fail closed.
/ 在隔离副本中注入来源或视图漂移，验证发布前拒绝。
Constraints / 约束: these tests do not execute business handoffs, calculate HCM
metrics or mark HET/HPT integration cases passed.
/ 测试不执行业务交接、不计算 HCM 指标、不将 HET/HPT 集成用例标为通过。
"""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/harness-engineering-patterns'
SPEC = importlib.util.spec_from_file_location('handoff_sync', SKILL / 'scripts/sync_handoff_chain_docs.py')
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


@pytest.fixture
def copied_handoff(tmp_path):
    target = tmp_path / 'skills/harness-engineering-patterns'
    for relative in (sync.DESIGN, sync.PROBE, sync.CONTRACT, sync.SOURCE_MAP, 'references/registry.json'):
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, path)
    source = json.loads((SKILL / sync.SOURCE_MAP).read_text(encoding='utf-8'))
    for item in source['sources']:
        path = tmp_path / item['snapshot_path']
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / item['snapshot_path'], path)
    assert sync.validate_handoff_assets(target) == []
    return target


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_map(target):
    return json.loads((target / sync.SOURCE_MAP).read_text(encoding='utf-8'))


def peer_bytes(target):
    return {relative: (target / relative).read_bytes() for relative in (sync.DESIGN, sync.PROBE)}


def replace_snapshot(target, source, role, transform):
    record = next(item for item in source['sources'] if item['id'] == role)
    path = target.parent.parent / record['snapshot_path']
    data = transform(path.read_bytes())
    path.write_bytes(data)
    record['sha256'] = hashlib.sha256(data).hexdigest()
    write_json(target / sync.SOURCE_MAP, source)


def test_complete_sources_and_both_maintained_views_are_valid():
    assert sync.validate_handoff_assets(SKILL) == []


@pytest.mark.parametrize('group', list(sync.GROUPS))
def test_omitted_source_requirement_blocks_all_writes(copied_handoff, group):
    target = copied_handoff
    source = read_map(target)
    source[group].pop()
    write_json(target / sync.SOURCE_MAP, source)
    before = peer_bytes(target)
    with pytest.raises(ValueError, match='source inventory|stable ID'):
        sync.sync(target)
    assert sync.validate_handoff_assets(target)
    assert peer_bytes(target) == before


@pytest.mark.parametrize('mutation', [
    'formula', 'boundary', 'case_outcome', 'duplicate_mapping', 'source_id',
    'truncated_node', 'missing_translation', 'metric_implementation', 'case_result',
    'source_pattern', 'source_contract',
])
def test_mapping_drift_or_unearned_support_is_rejected(copied_handoff, mutation):
    target = copied_handoff
    source = read_map(target)
    if mutation == 'formula':
        source['metrics'][0]['formula_zh'] = '到达消息数量就是正式接收数量'
    elif mutation == 'boundary':
        source['metrics'][26]['boundary_zh'] = '没有独立索引也可以报告全量覆盖'
    elif mutation == 'case_outcome':
        source['probe_cases'][8]['expected_zh'] = '自动创建新业务键重发'
    elif mutation == 'duplicate_mapping':
        row = deepcopy(source['metrics'][0])
        row['id'] = source['metrics'][1]['id']
        source['metrics'][1] = row
    elif mutation == 'source_id':
        source['execution_nodes'][0]['source_id'] = '虚构节点'
    elif mutation == 'truncated_node':
        row = source['execution_nodes'][0]
        row['source_end_line'] = row['source_line']
        row['source_text'] = row['source_text'].splitlines()[0]
        row['excerpt_sha256'] = sync.digest(row['source_text'])
    elif mutation == 'missing_translation':
        source['invariants'][0]['summary_en'] = ''
    elif mutation == 'metric_implementation':
        source['metrics'][0]['implementation'] = 'deployed'
    elif mutation == 'case_result':
        source['execution_cases'][0]['integration_status'] = 'passed'
    elif mutation == 'source_pattern':
        source['source_pattern_alias'] = 'PATTERN_0035'
    else:
        source['source_contract_version'] = '3.0.0'
    write_json(target / sync.SOURCE_MAP, source)
    before = peer_bytes(target)
    with pytest.raises(ValueError):
        sync.sync(target)
    assert sync.validate_handoff_assets(target)
    assert peer_bytes(target) == before


def test_snapshot_byte_drift_is_detected(copied_handoff):
    source = read_map(copied_handoff)
    path = copied_handoff.parent.parent / source['sources'][0]['snapshot_path']
    path.write_bytes(path.read_bytes() + b'\nUnexpected revision\n')
    assert any('snapshot digest drift' in error for error in sync.validate_handoff_assets(copied_handoff))


@pytest.mark.parametrize('mutation', ['protocol_version', 'event_field', 'request_target', 'patch_target'])
def test_shared_protocol_semantic_drift_rejected_with_updated_file_hash(copied_handoff, mutation):
    target = copied_handoff
    source = read_map(target)
    changes = {
        'protocol_version': (b'protocol_version: "1.0"', b'protocol_version: "9.0"'),
        'event_field': (b'source_sequence:', b'forged_sequence:'),
        'request_target': (b'expected_version: 2', b'expected_version: 99'),
        'patch_target': (b'patch_id:', b'wrong_patch_id:'),
    }
    old, new = changes[mutation]
    replace_snapshot(target, source, 'probe', lambda data: data.replace(old, new, 1))
    before = peer_bytes(target)
    assert sync.validate_handoff_assets(target)
    with pytest.raises(ValueError):
        sync.sync(target)
    assert peer_bytes(target) == before


def test_semantically_identical_yaml_formatting_is_accepted(copied_handoff):
    source = read_map(copied_handoff)
    replace_snapshot(copied_handoff, source, 'probe',
                     lambda data: data.replace(b'protocol_version: "1.0"', b"protocol_version: '1.0'"))
    assert sync.validate_handoff_assets(copied_handoff) == []


@pytest.mark.parametrize('role,group', [('execution', 'execution_nodes'), ('probe', 'probe_nodes')])
def test_new_source_node_cannot_hide_outside_fixed_inventory(copied_handoff, role, group):
    source = read_map(copied_handoff)
    replace_snapshot(copied_handoff, source, role,
                     lambda data: data + '\n### 节点九：新要求\n\n必须独立审查新增要求。\n'.encode())
    assert any('incomplete source inventory: ' + group in error
               for error in sync.validate_handoff_assets(copied_handoff))


@pytest.mark.parametrize('mutation', ['identity', 'maturity', 'specification', 'evidence_count', 'domain_count'])
def test_registry_cannot_rename_or_promote_specifications(copied_handoff, mutation):
    path = copied_handoff / 'references/registry.json'
    registry = json.loads(path.read_text(encoding='utf-8'))
    cell = next(item for item in registry['cells'] if item['id'] == 'CELL_COLLABORATION_CHAIN')
    if mutation == 'identity':
        cell['pattern_ref'] = 'PATTERN_0035'
    elif mutation == 'maturity':
        cell['maturity'] = 'validated'
    elif mutation == 'specification':
        cell['handoff_specification']['implementation_status'] = 'deployed'
    else:
        cell['local_evidence_count' if mutation == 'evidence_count' else 'domain_count'] = 1
    write_json(path, registry)
    assert any('handoff_registry' in error for error in sync.validate_handoff_assets(copied_handoff))


def test_snapshot_path_cannot_escape_project_evidence(copied_handoff):
    source = read_map(copied_handoff)
    source['sources'][0]['snapshot_path'] = '../outside.md'
    write_json(copied_handoff / sync.SOURCE_MAP, source)
    assert any('outside project evidence' in error for error in sync.validate_handoff_assets(copied_handoff))


def test_bilingual_view_refresh_preserves_authored_prose_and_is_idempotent(copied_handoff):
    target = copied_handoff
    note = '\nLocal authored scenario / 本地手写场景。\n'
    for relative in (sync.DESIGN, sync.PROBE):
        path = target / relative
        path.write_text(path.read_text(encoding='utf-8') + note, encoding='utf-8')
    source = read_map(target)
    source['metrics'][0]['summary_en'] += ' This is a design definition, not a measured result.'
    source['execution_nodes'][0]['summary_en'] += ' All adoption remains scoped to this task.'
    write_json(target / sync.SOURCE_MAP, source)
    assert sync.validate_handoff_assets(target)
    sync.sync(target)
    assert sync.validate_handoff_assets(target) == []
    before = peer_bytes(target)
    assert all(value.decode().endswith(note) for value in before.values())
    sync.sync(target)
    assert peer_bytes(target) == before


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'reversed', 'overlapping'])
def test_invalid_peer_markers_cannot_partially_publish(copied_handoff, mutation):
    target = copied_handoff
    probe = target / sync.PROBE
    text = probe.read_text(encoding='utf-8')
    start, end = '<!-- handoff:metrics:start -->', '<!-- handoff:metrics:end -->'
    if mutation == 'missing':
        text = text.replace(end, '')
    elif mutation == 'duplicate':
        text += '\n' + start
    elif mutation == 'reversed':
        text = text.replace(start, 'TEMP_START').replace(end, start).replace('TEMP_START', end)
    else:
        node_end = '<!-- handoff:probe_nodes:end -->'
        check_start = '<!-- handoff:probe_checks:start -->'
        text = text.replace(node_end, 'TEMP_END').replace(check_start, node_end).replace('TEMP_END', check_start)
    probe.write_text(text, encoding='utf-8')
    source = read_map(target)
    source['execution_nodes'][0]['summary_en'] += ' Pending view update.'
    write_json(target / sync.SOURCE_MAP, source)
    before = peer_bytes(target)
    with pytest.raises(ValueError):
        sync.sync(target)
    assert peer_bytes(target) == before


def test_missing_yaml_dependency_returns_a_validation_error(monkeypatch):
    monkeypatch.setattr(sync, 'yaml', None)
    assert any('PyYAML is required' in error for error in sync.validate_handoff_assets(SKILL))


def test_ambiguous_protocol_yaml_is_rejected():
    source = read_map(SKILL)
    text = (ROOT / source['sources'][1]['snapshot_path']).read_text(encoding='utf-8')
    text = text.replace('protocol_version: "1.0"', 'protocol_version: "1.0"\nprotocol_version: "1.0"', 1)
    with pytest.raises(ValueError, match='duplicate YAML key'):
        sync.shared_protocols(text)


@pytest.mark.parametrize('line,expected_path', [
    ('  expected_manifest_digest: "<algorithm:target-digest>"\n', 'request.target.expected_manifest_digest'),
    ('    source_digest: null\n', 'patch.observations[].source_digest'),
    ('  task_id: "<task>"\n', 'request.scope.task_id'),
])
def test_local_contract_cannot_omit_nested_source_fields(copied_handoff, line, expected_path):
    contract = copied_handoff / sync.CONTRACT
    text = contract.read_text(encoding='utf-8')
    assert line in text
    contract.write_text(text.replace(line, '', 1), encoding='utf-8')
    before = peer_bytes(copied_handoff)
    assert any(expected_path in error for error in sync.validate_handoff_assets(copied_handoff))
    with pytest.raises(ValueError, match='handoff_contract'):
        sync.sync(copied_handoff)
    assert peer_bytes(copied_handoff) == before


def test_local_contract_cannot_change_shared_protocol_version(copied_handoff):
    contract = copied_handoff / sync.CONTRACT
    text = contract.read_text(encoding='utf-8')
    contract.write_text(text.replace('protocol_version: "1.0"', 'protocol_version: "2.0"', 1),
                        encoding='utf-8')
    assert any('handoff_contract' in error for error in sync.validate_handoff_assets(copied_handoff))


def test_local_contract_allows_localized_examples_and_additional_fields(copied_handoff):
    contract = copied_handoff / sync.CONTRACT
    text = contract.read_text(encoding='utf-8')
    text = text.replace('source_sequence: 12', 'source_sequence: 来源序号占位说明')
    text = text.replace('max_cost: 1 #', 'max_cost: 由本地配置提供 #')
    text = text.replace('target:\n', 'target:\n  declared_extension: local_example\n')
    contract.write_text(text, encoding='utf-8')
    assert sync.validate_handoff_assets(copied_handoff) == []
