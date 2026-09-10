"""Source fidelity and bounded gather document generation / 聚合来源保真与有界文档生成。

These checks validate maintained assets, not live fan-out or GM measurements.
/ 这些检查验证维护资产，不执行真实扇出或 GM 测量。
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
SPEC = importlib.util.spec_from_file_location('gather_sync', SKILL / 'scripts/sync_collaboration_gather_docs.py')
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


@pytest.fixture
def copied_gather(tmp_path):
    target = tmp_path / 'skills/harness-engineering-patterns'
    for relative in [sync.DESIGN, sync.PROBE, sync.CONTRACT, sync.SOURCE_MAP, 'references/registry.json']:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, path)
    source = json.loads((SKILL / sync.SOURCE_MAP).read_text(encoding='utf-8'))
    for item in source['sources']:
        path = tmp_path / item['snapshot_path']
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / item['snapshot_path'], path)
    assert sync.validate_gather_assets(target) == []
    return target


@pytest.mark.parametrize('mutation', [
    'coverage_formula', 'timeout_boundary', 'case_outcome', 'duplicate_mapping',
    'missing_probe_node', 'truncated_reference', 'snapshot_digest', 'source_protocol',
    'metric_implementation', 'case_integration', 'protocol_version', 'snapshot_escape',
])
def test_source_drift_cannot_be_published(copied_gather, mutation):
    target = copied_gather
    path = target / sync.SOURCE_MAP
    source = json.loads(path.read_text(encoding='utf-8'))
    if mutation == 'coverage_formula':
        source['metrics'][0]['formula_zh'] = '成功回调数量 / 收到的回调数量'
    elif mutation == 'timeout_boundary':
        source['metrics'][8]['boundary_zh'] = '曾超时后成功也计最终超时'
    elif mutation == 'case_outcome':
        source['probe_cases'][10]['expected_zh'] = '补丁发出即计业务闭环'
    elif mutation == 'duplicate_mapping':
        item = deepcopy(source['metrics'][0])
        item['id'] = source['metrics'][1]['id']
        source['metrics'][1] = item
    elif mutation == 'missing_probe_node':
        source['probe_nodes'].pop(4)
    elif mutation == 'truncated_reference':
        # Keep the digest consistent with the shortened excerpt: coverage of the
        # complete source section must still fail. / 缩短段落并重算摘要仍须拒绝。
        item = source['metrics'][2]
        item['source_end_line'] = item['source_line']
        snapshot = target.parent.parent / source['sources'][1]['snapshot_path']
        line = snapshot.read_text(encoding='utf-8').splitlines()[item['source_line'] - 1]
        item['excerpt_sha256'] = hashlib.sha256(line.encode()).hexdigest()
    elif mutation in {'snapshot_digest', 'source_protocol'}:
        item = source['sources'][1]
        snapshot = target.parent.parent / item['snapshot_path']
        data = snapshot.read_bytes()
        if mutation == 'snapshot_digest':
            snapshot.write_bytes(data + b'\nchanged\n')
        else:
            data = data.replace('固定为本协议版本 `0.1.0`'.encode(), '固定为本协议版本 `9.0.0`'.encode())
            snapshot.write_bytes(data)
            item['sha256'] = hashlib.sha256(data).hexdigest()
    elif mutation == 'metric_implementation':
        source['metrics'][0]['implementation'] = 'reference'
    elif mutation == 'case_integration':
        source['execution_cases'][0]['integration_status'] = 'passed'
    elif mutation == 'protocol_version':
        source['source_contract_version'] = '3.0.0'
    else:
        source['sources'][0]['snapshot_path'] = '../outside.md'
    path.write_text(json.dumps(source, ensure_ascii=False), encoding='utf-8')
    assert sync.validate_gather_assets(target)
    before = {name: (target / name).read_bytes() for name in (sync.DESIGN, sync.PROBE)}
    with pytest.raises(ValueError):
        sync.sync(target)
    assert before == {name: (target / name).read_bytes() for name in before}


def test_shared_contract_propagates_without_losing_authored_prose(copied_gather):
    target = copied_gather
    note = '\nAuthored scenario note / 手写场景说明。\n'
    for relative in (sync.DESIGN, sync.PROBE):
        path = target / relative
        path.write_text(path.read_text(encoding='utf-8') + note, encoding='utf-8')
    contract = target / sync.CONTRACT
    contract.write_text(contract.read_text(encoding='utf-8') + '\nAdditional rule / 补充规则。\n', encoding='utf-8')
    assert sync.validate_gather_assets(target)
    sync.sync(target)
    assert sync.validate_gather_assets(target) == []
    before = {relative: (target / relative).read_bytes() for relative in (sync.DESIGN, sync.PROBE)}
    assert all(data.decode('utf-8').endswith(note) for data in before.values())
    sync.sync(target)
    assert before == {relative: (target / relative).read_bytes() for relative in before}


def test_missing_peer_marker_prevents_partial_sync(copied_gather):
    target = copied_gather
    path = target / sync.PROBE
    path.write_text(path.read_text(encoding='utf-8').replace('<!-- gather:metrics:end -->', ''), encoding='utf-8')
    contract = target / sync.CONTRACT
    contract.write_text(contract.read_text(encoding='utf-8') + '\nPending rule / 待同步规则。\n', encoding='utf-8')
    before = (target / sync.DESIGN).read_bytes()
    with pytest.raises(ValueError):
        sync.sync(target)
    assert (target / sync.DESIGN).read_bytes() == before


def test_registry_cannot_promote_or_rename_dedicated_specification(copied_gather):
    target = copied_gather
    path = target / 'references/registry.json'
    registry = json.loads(path.read_text(encoding='utf-8'))
    cell = next(item for item in registry['cells'] if item['id'] == 'CELL_COLLABORATION_PARALLEL')
    cell['pattern_ref'] = 'PATTERN_GATHER_0001'
    cell['gather_specification']['implementation_status'] = 'deployed'
    path.write_text(json.dumps(registry), encoding='utf-8')
    assert sync.validate_gather_assets(target)


def test_supplied_snapshot_comparison_checks_protocol_not_just_digest(copied_gather):
    target = copied_gather
    path = target / sync.SOURCE_MAP
    source = json.loads(path.read_text(encoding='utf-8'))
    probe = source['sources'][1]
    snapshot = target.parent.parent / probe['snapshot_path']
    data = snapshot.read_bytes().replace('固定为本协议版本 `0.1.0`'.encode(), '固定为本协议版本 `9.0.0`'.encode())
    snapshot.write_bytes(data)
    probe['sha256'] = hashlib.sha256(data).hexdigest()
    path.write_text(json.dumps(source, ensure_ascii=False), encoding='utf-8')
    assert any('shared protocols differ' in error for error in sync.validate_gather_assets(target))
