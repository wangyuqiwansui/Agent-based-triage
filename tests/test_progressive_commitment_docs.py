"""Asset integrity regression tests / 资产完整性回归测试。

Exercise omission, tampering and registration failure paths in isolated copies.
These are not execution of documented business scenarios.
/ 在隔离副本测试遗漏、篡改与注册失败路径，不执行文档中的业务场景。
"""

import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil

import pytest


SKILL = Path(__file__).resolve().parents[1] / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/validate_progressive_commitment_docs.py'))
validate = MODULE['validate_progressive_commitment_assets']
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
    paths.update(source['snapshot_path'] for source in load(SKILL / SOURCE_MAP)['sources'])
    for relative in documents:
        for link in re.findall(r'\]\(([^)]+)\)', (SKILL / relative).read_text(encoding='utf-8')):
            if not link.startswith('#') and not re.match(r'[a-zA-Z][\w+.-]*:', link):
                paths.add((Path(relative).parent / link.split('#')[0]).as_posix())
    for relative in paths:
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, dest)
    return target


def test_validation_is_readonly(assets):
    before = {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}
    assert validate(assets) == []
    assert before == {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_mapping_omission_does_not_hide_source_requirement(assets, group):
    mapping = load(assets / SOURCE_MAP)
    mapping['inventories'][group].pop()
    save(assets / SOURCE_MAP, mapping)
    assert any('definition mapping drift: ' + group in e for e in validate(assets))


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_citation_cannot_replace_definition(assets, group):
    item = load(assets / SOURCE_MAP)['inventories'][group][-1]
    path = assets / item['target_document']
    content = re.sub(rf'^\| {re.escape(item["id"])} \|.*\n', '', path.read_text(encoding='utf-8'), flags=re.M)
    path.write_text(content + '\nReference / 引用: ' + item['id'] + '\n', encoding='utf-8')
    assert any('definitions: ' + group in e for e in validate(assets))


def test_original_formula_change_is_detected(assets):
    path = assets / MODULE['PROBE']
    text = path.read_text(encoding='utf-8').replace('已有权威终态的运行数', '全部已接收运行数')
    path.write_text(text, encoding='utf-8')
    assert any('source formula drift: PM-OUT-01' in e for e in validate(assets))


def test_snapshot_tampering_is_detected(assets):
    source = load(assets / SOURCE_MAP)['sources'][0]
    path = assets / source['snapshot_path']
    path.write_bytes(path.read_bytes() + b'\nchanged\n')
    assert any('snapshot digest drift' in e for e in validate(assets))


def test_source_omission_rejected_even_with_new_hash_and_mapping(assets):
    mapping = load(assets / SOURCE_MAP)
    source = mapping['sources'][1]
    path = assets / source['snapshot_path']
    text = re.sub(r'^\| PM-DQ-01 \|.*\n', '', path.read_text(encoding='utf-8'), flags=re.M)
    path.write_text(text, encoding='utf-8')
    source['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    mapping['inventories']['metrics'] = MODULE['source_inventory'](text, 'metrics')
    save(assets / SOURCE_MAP, mapping)
    assert any('unexpected count or duplicate: metrics' in e for e in validate(assets))


@pytest.mark.parametrize('mutation', ['coordinate', 'maturity', 'new_pattern', 'chain_promotion', 'readiness'])
def test_unsupported_registration_change_rejected(assets, mutation):
    path = assets / 'references/registry.json'
    registry = load(path)
    cell = next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_PARALLEL')
    if mutation == 'coordinate':
        cell['coordinate'] = 'COG_GOVERNANCE__TOP_CHAIN'
    elif mutation == 'maturity':
        cell['maturity'] = 'operational'
    elif mutation == 'new_pattern':
        registry['patterns'].append({'id': 'PATTERN_GOVERNANCE_0003'})
    elif mutation == 'chain_promotion':
        next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_CHAIN')['pattern_ref'] = 'PATTERN_0048'
    else:
        registry['progressive_commitment_specification']['implementation_status'] = 'deployed'
    save(path, registry)
    assert validate(assets)


@pytest.mark.parametrize('field,value', [('acceptance_status', 'passed'), ('metric_implementation', 'deployed')])
def test_document_checks_cannot_claim_runtime_acceptance(assets, field, value):
    mapping = load(assets / SOURCE_MAP)
    mapping[field] = value
    save(assets / SOURCE_MAP, mapping)
    assert any('unsupported runtime' in e for e in validate(assets))


def test_source_path_cannot_escape_skill(assets):
    mapping = load(assets / SOURCE_MAP)
    mapping['sources'][0]['snapshot_path'] = '../outside.txt'
    (assets.parent / 'outside.txt').write_text('outside', encoding='utf-8')
    save(assets / SOURCE_MAP, mapping)
    assert any('outside skill' in e for e in validate(assets))


def test_missing_anchor_rejected(assets):
    path = assets / MODULE['DESIGN']
    path.write_text(path.read_text(encoding='utf-8').replace('#execution-steps', '#absent'), encoding='utf-8')
    assert any('missing anchor' in e for e in validate(assets))


@pytest.mark.parametrize('payload', ['{bad', 'null', '[]'])
def test_malformed_mapping_returns_diagnostic(assets, payload):
    (assets / SOURCE_MAP).write_text(payload, encoding='utf-8')
    assert validate(assets)
