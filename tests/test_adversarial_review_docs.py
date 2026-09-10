"""Adversarial Review asset integrity / 对抗评审资产完整性。

These tests exercise source validation and bounded document updates, not deployed
review gates or RM calculators. / 验证来源校验和有界文档更新，不验证已部署闸门或指标计算器。
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/harness-engineering-patterns'
SPEC = importlib.util.spec_from_file_location('review_sync', SKILL / 'scripts/sync_adversarial_review_docs.py')
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


@pytest.fixture
def copied_review(tmp_path):
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
    return target


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def test_all_source_inventories_and_both_views_are_valid():
    assert sync.validate_review_assets(SKILL) == []


@pytest.mark.parametrize('group', list(sync.GROUPS))
def test_omitting_a_source_requirement_blocks_sync_without_partial_write(copied_review, group):
    target = copied_review
    source_path = target / sync.SOURCE_MAP
    data = json.loads(source_path.read_text(encoding='utf-8'))
    data[group].pop()
    write_json(source_path, data)
    before = {relative: (target / relative).read_bytes() for relative in (sync.DESIGN, sync.PROBE)}
    with pytest.raises(ValueError):
        sync.sync(target)
    assert sync.validate_review_assets(target)
    assert before == {relative: (target / relative).read_bytes() for relative in before}


def test_contract_updates_both_peers_preserves_prose_and_is_idempotent(copied_review):
    target = copied_review
    note = '\nAuthored project context / 手写项目说明。\n'
    for relative in (sync.DESIGN, sync.PROBE):
        path = target / relative
        path.write_text(path.read_text(encoding='utf-8') + note, encoding='utf-8')
    contract = target / sync.CONTRACT
    contract.write_text(contract.read_text(encoding='utf-8') + '\nNew constraint / 新约束。\n', encoding='utf-8')
    assert sync.validate_review_assets(target)
    sync.sync(target)
    assert sync.validate_review_assets(target) == []
    before = {relative: (target / relative).read_bytes() for relative in (sync.DESIGN, sync.PROBE)}
    assert all(data.decode('utf-8').endswith(note) for data in before.values())
    sync.sync(target)
    assert before == {relative: (target / relative).read_bytes() for relative in before}


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'reversed'])
def test_invalid_peer_markers_prevent_any_update(copied_review, mutation):
    target = copied_review
    probe = target / sync.PROBE
    text = probe.read_text(encoding='utf-8')
    begin, end = '<!-- review:metrics:start -->', '<!-- review:metrics:end -->'
    if mutation == 'missing':
        text = text.replace(end, '')
    elif mutation == 'duplicate':
        text += '\n' + begin
    else:
        text = text.replace(begin, 'TEMP_METRIC_START').replace(end, begin).replace('TEMP_METRIC_START', end)
    probe.write_text(text, encoding='utf-8')
    contract = target / sync.CONTRACT
    contract.write_text(contract.read_text(encoding='utf-8') + '\nPending update / 待更新。\n', encoding='utf-8')
    before = (target / sync.DESIGN).read_bytes()
    with pytest.raises(ValueError):
        sync.sync(target)
    assert before == (target / sync.DESIGN).read_bytes()


def test_source_payload_drift_is_rejected_even_if_the_map_is_unchanged(copied_review):
    source = json.loads((copied_review / sync.SOURCE_MAP).read_text(encoding='utf-8'))
    path = copied_review.parent.parent / source['sources'][0]['snapshot_path']
    path.write_bytes(path.read_bytes() + b'\nUnexpected revision\n')
    assert any('digest drift' in error for error in sync.validate_review_assets(copied_review))


def test_protocol_disagreement_is_rejected_even_with_updated_file_hash(copied_review):
    source_path = copied_review / sync.SOURCE_MAP
    source = json.loads(source_path.read_text(encoding='utf-8'))
    probe = source['sources'][1]
    path = copied_review.parent.parent / probe['snapshot_path']
    data = path.read_bytes().replace('契约版本为 `0.1.0`'.encode(), '契约版本为 `9.0.0`'.encode())
    path.write_bytes(data)
    probe['sha256'] = hashlib.sha256(data).hexdigest()
    write_json(source_path, source)
    assert any('shared protocols differ' in error for error in sync.validate_review_assets(copied_review))


def test_formula_change_cannot_silently_redefine_a_source_metric(copied_review):
    path = copied_review / sync.SOURCE_MAP
    source = json.loads(path.read_text(encoding='utf-8'))
    source['metrics'][6]['formula_zh'] = '评审人数 / reviewer count'
    write_json(path, source)
    with pytest.raises(ValueError, match='definition drift'):
        sync.sync(copied_review)


@pytest.mark.parametrize('mutation', ['identity', 'maturity', 'implementation', 'case_result'])
def test_specification_cannot_claim_new_identity_or_executed_controls(copied_review, mutation):
    path = copied_review / ('references/registry.json' if mutation in ('identity', 'maturity') else sync.SOURCE_MAP)
    data = json.loads(path.read_text(encoding='utf-8'))
    if mutation in ('identity', 'maturity'):
        cell = next(item for item in data['cells'] if item['id'] == 'CELL_COLLABORATION_LOOP')
        cell['pattern_ref' if mutation == 'identity' else 'maturity'] = 'PATTERN_REVIEW_0001' if mutation == 'identity' else 'validated'
    elif mutation == 'implementation':
        data['metrics'][0]['implementation'] = 'deployed'
    else:
        data['execution_cases'][0]['integration_status'] = 'passed'
    write_json(path, data)
    assert sync.validate_review_assets(copied_review)


def test_snapshot_reference_cannot_escape_project_evidence(copied_review):
    path = copied_review / sync.SOURCE_MAP
    data = json.loads(path.read_text(encoding='utf-8'))
    data['sources'][0]['snapshot_path'] = '../../outside.md'
    write_json(path, data)
    assert any('outside project evidence' in error for error in sync.validate_review_assets(copied_review))
