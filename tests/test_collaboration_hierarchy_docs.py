"""Source fidelity and bounded document synchronization / 来源保真与有界文档同步。

These tests do not exercise business delegation or calculate HM metrics.
/ 这些测试不执行真实业务委派，也不计算 HM 指标。
"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/harness-engineering-patterns'
SPEC = importlib.util.spec_from_file_location('hierarchy_sync', SKILL / 'scripts/sync_collaboration_hierarchy_docs.py')
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


@pytest.fixture
def copied_hierarchy(tmp_path):
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
    assert sync.validate_hierarchy_assets(target) == []
    return target


@pytest.mark.parametrize('mutation', [
    'formula', 'case_outcome', 'duplicate_mapping', 'source_id', 'source_fingerprint',
    'metric_implementation', 'case_integration', 'shared_protocol', 'shared_contract',
])
def test_hierarchy_rejects_source_or_support_drift(copied_hierarchy, mutation):
    target = copied_hierarchy
    path = target / sync.SOURCE_MAP
    source = json.loads(path.read_text(encoding='utf-8'))
    if mutation == 'formula':
        source['metrics'][1]['formula_zh'] = '卡片总数就是责任覆盖'
    elif mutation == 'case_outcome':
        source['execution_cases'][7]['expected_zh'] = '未知时自动通过'
    elif mutation == 'duplicate_mapping':
        row = deepcopy(source['metrics'][0])
        row['id'] = source['metrics'][1]['id']
        source['metrics'][1] = row
    elif mutation == 'source_id':
        source['metrics'][0]['source_id'] = '指标'
    elif mutation == 'source_fingerprint':
        snapshot = target.parent.parent / source['sources'][0]['snapshot_path']
        snapshot.write_bytes(snapshot.read_bytes() + b'\nchanged\n')
    elif mutation == 'metric_implementation':
        source['metrics'][0]['implementation'] = 'reference'
    elif mutation == 'case_integration':
        source['execution_cases'][0]['integration_status'] = 'passed'
    elif mutation == 'shared_protocol':
        source['source_contract_version'] = '3.0.0'
    else:
        doc = target / sync.PROBE
        doc.write_text(doc.read_text(encoding='utf-8').replace('protocol_version: "0.1.0"', 'protocol_version: "3.0.0"'), encoding='utf-8')
    path.write_text(json.dumps(source, ensure_ascii=False), encoding='utf-8')
    assert sync.validate_hierarchy_assets(target)


def test_sync_preserves_authored_prose_and_is_idempotent(copied_hierarchy):
    target = copied_hierarchy
    sentinel = '\nLocal authored note / 本地手写说明。\n'
    for relative in (sync.DESIGN, sync.PROBE):
        path = target / relative
        path.write_text(path.read_text(encoding='utf-8') + sentinel, encoding='utf-8')
    contract = target / sync.CONTRACT
    contract.write_text(contract.read_text(encoding='utf-8') + '\nAdditional contract note / 补充契约说明。\n', encoding='utf-8')
    assert sync.validate_hierarchy_assets(target)
    sync.sync(target)
    assert sync.validate_hierarchy_assets(target) == []
    before = {relative: (target / relative).read_bytes() for relative in (sync.DESIGN, sync.PROBE)}
    assert all(data.decode('utf-8').endswith(sentinel) for data in before.values())
    sync.sync(target)
    assert before == {relative: (target / relative).read_bytes() for relative in before}


def test_missing_block_does_not_partially_rewrite_other_document(copied_hierarchy):
    target = copied_hierarchy
    path = target / sync.PROBE
    path.write_text(path.read_text(encoding='utf-8').replace('<!-- hierarchy:metrics:end -->', ''), encoding='utf-8')
    contract = target / sync.CONTRACT
    contract.write_text(contract.read_text(encoding='utf-8') + '\nPending change / 待同步改动。\n', encoding='utf-8')
    before = (target / sync.DESIGN).read_bytes()
    with pytest.raises(ValueError):
        sync.sync(target)
    assert (target / sync.DESIGN).read_bytes() == before
