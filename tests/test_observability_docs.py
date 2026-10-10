"""Observability asset integrity / 可观测性资产完整性。

Fault injection checks provenance, coverage, identity and navigation, not the
specified business scenarios. / 故障注入检验来源、覆盖、身份及导航，不执行业务场景。
"""

import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil

import pytest

SKILL = Path(__file__).resolve().parents[1] / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/validate_observability_docs.py'))
validate = MODULE['validate_observability_assets']
SOURCE_MAP = MODULE['SOURCE_MAP']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


@pytest.fixture
def assets(tmp_path):
    target = tmp_path / 'skill'
    documents = [MODULE[k] for k in ('EXECUTION', 'PROBE', 'CONTRACT', 'DESIGN', 'CARD')]
    paths = set(documents + [SOURCE_MAP, 'references/registry.json'])
    paths.update(s['snapshot_path'] for s in load(SKILL / SOURCE_MAP)['sources'])
    for relative in documents:
        for link in re.findall(r'\]\(([^)]+)\)', (SKILL / relative).read_text(encoding='utf-8')):
            if not link.startswith('#') and not re.match(r'[a-zA-Z][\w+.-]*:', link):
                paths.add((Path(relative).parent / link.split('#')[0]).as_posix())
    for relative in paths:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, path)
    return target


def test_validation_is_readonly(assets):
    before = {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}
    assert validate(assets) == []
    assert before == {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_source_requirement_cannot_be_hidden_by_omitting_mapping(assets, group):
    path = assets / SOURCE_MAP
    source = load(path)
    source['inventories'][group].pop()
    save(path, source)
    assert any('definition mapping drift: ' + group in e for e in validate(assets))


@pytest.mark.parametrize('group', MODULE['GROUPS'])
def test_citation_does_not_replace_definition(assets, group):
    source = load(assets / SOURCE_MAP)
    item = source['inventories'][group][0]
    path = assets / item['target_document']
    content = path.read_text(encoding='utf-8')
    content = re.sub(r'^\| ' + re.escape(item['id']) + r' \|.*\n', '', content, flags=re.M)
    path.write_text(content + '\nCitation / 引用: ' + item['id'], encoding='utf-8')
    assert any('definitions: ' + group in e for e in validate(assets))


def test_source_byte_change_is_detected(assets):
    source = load(assets / SOURCE_MAP)
    path = assets / source['sources'][0]['snapshot_path']
    path.write_bytes(path.read_bytes() + b'changed')
    assert any('snapshot digest drift' in e for e in validate(assets))


@pytest.mark.parametrize('group', ['metrics', 'probes'])
def test_preserving_id_is_insufficient_when_source_requirement_is_lost(assets, group):
    source = load(assets / SOURCE_MAP)
    item = source['inventories'][group][0]
    snapshot = assets / source['sources'][1]['snapshot_path']
    raw = snapshot.read_text(encoding='utf-8').splitlines()[item['source_line'] - 1]
    cells = [c.strip() for c in raw.split('|')[1:-1]]
    requirement = cells[1 if group == 'metrics' else 2]
    path = assets / MODULE['PROBE']
    lines = path.read_text(encoding='utf-8').splitlines()
    lines = [line.replace(requirement, 'omitted / 遗漏') if line.startswith('| ' + item['id'] + ' |') else line
             for line in lines]
    path.write_text('\n'.join(lines), encoding='utf-8')
    assert any('source requirement drift: ' + item['id'] in e for e in validate(assets))


def test_local_boundary_cases_cannot_disappear(assets):
    path = assets / MODULE['PROBE']
    path.write_text(re.sub(r'^\| OBX05 \|.*\n', '', path.read_text(encoding='utf-8'), flags=re.M), encoding='utf-8')
    assert any('local acceptance coverage drift' in e for e in validate(assets))


def test_requirement_removal_detected_with_updated_digest_and_map(assets):
    path = assets / SOURCE_MAP
    source = load(path)
    item = source['sources'][1]
    snapshot = assets / item['snapshot_path']
    content = re.sub(r'^\| PROBE_RUN_001 \|.*\n', '', snapshot.read_text(encoding='utf-8'), flags=re.M)
    snapshot.write_text(content, encoding='utf-8')
    item['sha256'] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    source['inventories']['probes'] = MODULE['source_inventory'](content, 'probes')
    save(path, source)
    assert any('unexpected definition count: probes' in e for e in validate(assets))


@pytest.mark.parametrize('field,value', [('acceptance_status', 'passed'), ('metric_implementation', 'deployed')])
def test_asset_pass_cannot_claim_business_acceptance(assets, field, value):
    path = assets / SOURCE_MAP
    source = load(path)
    source[field] = value
    save(path, source)
    assert any('unsupported runtime' in e for e in validate(assets))


@pytest.mark.parametrize('mutation', ['cell_identity', 'maturity', 'readiness', 'shared_version', 'alias_pattern'])
def test_identity_and_implementation_boundaries(assets, mutation):
    path = assets / 'references/registry.json'
    registry = load(path)
    cell = next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_ORCHESTRATION')
    if mutation == 'cell_identity':
        cell['pattern_ref'] = 'PATTERN_OBSERVABILITY_0001'
    elif mutation == 'maturity':
        cell['maturity'] = 'operational'
    elif mutation == 'readiness':
        registry['observability_specification']['implementation_status'] = 'deployed'
    elif mutation == 'shared_version':
        next(p for p in registry['patterns'] if p['id'] == 'PATTERN_0052')['source_version'] = '0.1.0'
    else:
        registry['patterns'].append({'id': 'PATTERN_OBSERVABILITY_0002'})
    save(path, registry)
    assert validate(assets)


def test_snapshot_cannot_escape_evidence_root(assets):
    path = assets / SOURCE_MAP
    source = load(path)
    source['sources'][0]['snapshot_path'] = '../outside.txt'
    (assets.parent / 'outside.txt').write_text('outside', encoding='utf-8')
    save(path, source)
    assert any('outside skill' in e for e in validate(assets))


def test_broken_entry_anchor_is_detected(assets):
    path = assets / MODULE['DESIGN']
    path.write_text(path.read_text(encoding='utf-8').replace('observability-execution-flow.md#execution-steps',
                                                          'observability-execution-flow.md#absent'), encoding='utf-8')
    assert any('missing anchor' in e for e in validate(assets))


@pytest.mark.parametrize('payload', ['null', '[]', '{bad'])
def test_malformed_manifest_returns_diagnostic(assets, payload):
    (assets / SOURCE_MAP).write_text(payload, encoding='utf-8')
    assert validate(assets)
