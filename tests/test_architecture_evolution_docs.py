"""Architecture evolution provenance checks / 架构演化来源检查。

Exercise tampering, missing provenance and navigation on isolated copies.
/ 在隔离副本验证篡改、来源遗漏与导航，不执行文档中的业务场景。
"""

import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/harness-engineering-patterns'
MODULE = runpy.run_path(str(SKILL / 'scripts/validate_architecture_evolution_docs.py'))
validate = MODULE['validate_architecture_evolution_assets']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


@pytest.fixture
def assets(tmp_path):
    target = tmp_path / 'skill'
    paths = list(MODULE['REFERENCES'].values())
    paths += ['references/registry.json', 'SKILL.md', 'references/pattern-catalog.md',
              'references/matrix-index.md']
    paths += [s['snapshot_path'] for s in load(SKILL / MODULE['SOURCE_MAP'])['sources']]
    for relative in list(MODULE['REFERENCES'].values())[:3]:
        for href in re.findall(r'\]\(([^)]+)\)', (SKILL / relative).read_text(encoding='utf-8')):
            if not href.startswith('#') and not re.match(r'^[a-zA-Z][\w+.-]*:', href):
                paths.append(str(Path(relative).parent / href.split('#')[0]))
    for relative in set(paths):
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, dest)
    return target


def test_validates_without_mutating_assets(assets):
    before = {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}
    assert validate(assets) == []
    assert before == {p.relative_to(assets): p.read_bytes() for p in assets.rglob('*') if p.is_file()}


def test_tampering_cannot_be_hidden_by_rehashing_mapping(assets):
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    source = mapping['sources'][0]
    snapshot = assets / source['snapshot_path']
    snapshot.write_bytes(snapshot.read_bytes() + b'\nchanged\n')
    source['sha256'] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    save(path, mapping)
    assert any('snapshot digest drift' in error for error in validate(assets))


@pytest.mark.parametrize('group', ['execution_chapters', 'execution_steps', 'probe_chapters', 'probe_steps'])
def test_missing_source_section_is_rejected(assets, group):
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    mapping['inventories'][group].pop()
    save(path, mapping)
    assert 'source inventory drift' in validate(assets)


@pytest.mark.parametrize('mutation', ['claim_execution', 'replace_shared_probe', 'promote_cell', 'duplicate_identity'])
def test_registration_cannot_imply_unsupported_capability(assets, mutation):
    path = assets / 'references/registry.json'
    registry = load(path)
    if mutation == 'claim_execution':
        registry['architecture_evolution_specification']['implementation_status'] = 'deployed'
    elif mutation == 'replace_shared_probe':
        next(p for p in registry['patterns'] if p['id'] == 'PATTERN_0052')['source_version'] = '0.2.0'
    elif mutation == 'promote_cell':
        registry['cells'][0]['pattern_ref'] = 'PATTERN_0054'
    else:
        registry['patterns'].append(next(p for p in registry['patterns'] if p['id'] == 'PATTERN_0054'))
    save(path, registry)
    assert validate(assets)


def test_source_path_cannot_escape_skill(assets):
    path = assets / MODULE['SOURCE_MAP']
    mapping = load(path)
    mapping['sources'][0]['snapshot_path'] = '../outside.txt'
    (assets.parent / 'outside.txt').write_text('outside', encoding='utf-8')
    save(path, mapping)
    assert any('outside skill file' in error for error in validate(assets))


def test_broken_anchor_and_missing_document_are_rejected(assets):
    path = assets / MODULE['REFERENCES']['execution_reference']
    path.write_text(path.read_text(encoding='utf-8') + '\n[Broken / 失效](#does-not-exist)\n', encoding='utf-8')
    assert any('missing anchor' in error for error in validate(assets))
    (assets / MODULE['REFERENCES']['interaction_contract_reference']).unlink()
    assert any('missing or outside skill file' in error for error in validate(assets))


def test_visualization_links_registered_documents_and_hashes_their_contents():
    generator = runpy.run_path(str(ROOT / 'scripts/generate_skill_visualization.py'))
    registry = load(SKILL / 'references/registry.json')
    rendered = generator['render_evolution_card'](registry)
    tracked = set(generator['source_files'](SKILL))
    for relative in MODULE['REFERENCES'].values():
        assert f'href="skills/harness-engineering-patterns/{relative}"' in rendered
        assert SKILL / relative in tracked
        assert (SKILL / relative).is_file()
    assert generator['render_evolution_card']({}) == ''
