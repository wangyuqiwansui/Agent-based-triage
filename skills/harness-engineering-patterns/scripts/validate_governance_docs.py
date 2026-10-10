"""Validate governance specifications / 校验治理规格。

Usage / 用法: python validate_governance_docs.py [skill_dir]
Workflow / 流程: Check source fingerprints, shared protocol, inventories and links.
/ 核验原文指纹、共享协议、完整清单与引用。
Constraints / 约束: Read-only asset checks; never approve actions or claim runtime
acceptance. / 仅执行只读资产检查，不批准动作，不宣称业务运行验收通过。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXECUTION = 'references/governance-execution-flow.md'
PROBE = 'references/governance-observability-probes.md'
CONTRACT = 'references/governance-contract.md'
SOURCE_MAP = 'references/governance-source-map.json'
GROUPS = {
    'execution_steps': ('执', 16, 'execution', EXECUTION),
    'probe_steps': ('探', 12, 'probe', PROBE),
    'metrics': ('指', 36, 'probe', PROBE),
    'execution_cases': ('执验', 26, 'execution', EXECUTION),
    'probe_cases': ('探验', 28, 'probe', PROBE),
}
PATTERNS = {
    'chain': None, 'routing': 'PATTERN_0047', 'parallel': 'PATTERN_0048',
    'orchestration': 'PATTERN_0049', 'loop': None, 'hierarchy': 'PATTERN_0050',
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def shared_contract(text: str) -> str:
    sections = re.findall(r'^## 附录乙[^\n]*\n(.*?)(?=^## 附录丙)', text, re.M | re.S)
    if len(sections) != 1:
        raise ValueError('expected exactly one shared source appendix / 必须有一个共享来源附录')
    return sections[0].strip()


def source_inventory(text: str, group: str) -> list[dict]:
    """Discover definitions independently / 独立扫描原文定义，避免清单自证。"""
    prefix, _, _, target = GROUPS[group]
    pattern = (rf'^### [\d.]+ ({prefix}\d{{2}})：' if group.endswith('_steps')
               else rf'^\| ({prefix}\d{{2}})(?:\s|\|)')
    lines = text.splitlines()
    rows = []
    for index, line in enumerate(lines):
        match = re.match(pattern, line)
        if not match:
            continue
        end = index + 1
        if group.endswith('_steps'):
            while end < len(lines) and not lines[end].startswith('### '):
                end += 1
        excerpt = '\n'.join(lines[index:end]).rstrip()
        row = dict(id=match[1], source_line=index + 1, source_end_line=end,
                   excerpt_sha256=digest(excerpt), target_document=target)
        if group == 'metrics':
            row['metric_id'] = 'MET_GOV_' + match[1][-2:]
        rows.append(row)
    return rows


def _definition_ids(text: str, prefix: str) -> list[str]:
    # Count definitions, not inline citations. / 统计定义行，不统计段落交叉引用。
    return re.findall(rf'^(?:###\s+|\|\s+)(?:[\d.]+\s+)?(?:`|\*\*)?({prefix}\d{{2}})(?!\d)', text, re.M)


def validate_governance_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Check fidelity and declared readiness only / 仅校验保真与声明的就绪状态。"""
    errors = []
    try:
        skill_dir = Path(skill_dir).resolve()
        registry = registry if registry is not None else json.loads(
            (skill_dir / 'references/registry.json').read_text(encoding='utf-8'))
        source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
        specification = registry.get('governance_specification', {})
        expected = dict(version='0.1.0', protocol_id='GOV_BOUNDARY_OBS', protocol_version='1.0.0',
                        implementation_status='specification_only', status='draft',
                        execution_reference=EXECUTION, observability_reference=PROBE,
                        interaction_contract_reference=CONTRACT, source_map_reference=SOURCE_MAP)
        for label, value in (('registry', specification), ('source_map', source)):
            if any(value.get(key) != item for key, item in expected.items()):
                errors.append(f'governance_{label}: specification registration or readiness drift')
            if any(not value.get(key) for key in ('name_en', 'name_zh', 'description_en', 'description_zh')):
                errors.append(f'governance_{label}: missing bilingual metadata')
        cells = [cell for cell in registry['cells'] if cell['capability_ref'] == 'COG_GOVERNANCE']
        if [cell['cell_key'] for cell in cells] != ['governance-' + mode for mode in PATTERNS]:
            errors.append('governance_registry: six-cell topology drift')
        for cell in cells:
            mode = cell['cell_key'].removeprefix('governance-')
            pattern = PATTERNS.get(mode)
            if (cell['pattern_ref'] != pattern
                    or cell['status'] != ('named' if pattern else 'extension_candidate')
                    or cell['maturity'] != ('draft' if pattern else 'seed')):
                errors.append('governance_registry: unsupported identity or maturity change: ' + mode)
        expected_aliases = {
            'pattern': ['PATTERN_GOVERNANCE_0036', 'PATTERN_OBSERVABILITY_0036'],
            'skill': ['SKILL_GOVERNANCE_0036', 'SKILL_OBSERVABILITY_0036'],
            'node': ['NODE_GOVERNANCE_0036', 'NODE_OBSERVABILITY_0036'],
        }
        if source.get('source_aliases') != expected_aliases:
            errors.append('governance_source: provenance aliases changed')
        if [item['id'] for item in source['sources']] != ['execution', 'probe']:
            raise ValueError('expected one execution and one probe snapshot')
        snapshots = {}
        evidence_root = (skill_dir / 'references/sources/governance').resolve()
        for item in source['sources']:
            path = (skill_dir / item['snapshot_path']).resolve()
            if not path.is_relative_to(evidence_root):
                raise ValueError('snapshot outside governance evidence directory')
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                errors.append('governance_source: snapshot digest drift: ' + item['id'])
            text = data.decode('utf-8-sig').replace('\r\n', '\n')
            expected_skill = ('SKILL_GOVERNANCE_0036' if item['id'] == 'execution'
                              else 'SKILL_OBSERVABILITY_0036')
            for field, value in [('version', '0.1.0'), ('protocol_id', 'GOV_BOUNDARY_OBS'),
                                 ('protocol_version', '1.0.0'), ('skill_id', expected_skill)]:
                if not re.search(rf'^{field}: {re.escape(value)}$', text, re.M):
                    errors.append('governance_source: source metadata drift: ' + field)
            snapshots[item['id']] = text
        contracts = [shared_contract(text) for text in snapshots.values()]
        if contracts[0] != contracts[1] or digest(contracts[0]) != source['shared_source_contract_sha256']:
            errors.append('governance_source: shared protocols differ or fingerprint changed')
        documents = {path: (skill_dir / path).read_text(encoding='utf-8')
                     for path in (EXECUTION, PROBE, CONTRACT)}
        for path, content in documents.items():
            if '\ufffd' in content:
                errors.append('governance_document: corrupt Unicode: ' + path)
        for group, (prefix, count, sid, target) in GROUPS.items():
            original = source_inventory(snapshots[sid], group)
            expected_ids = [f'{prefix}{i:02d}' for i in range(1, count + 1)]
            if [row['id'] for row in original] != expected_ids:
                errors.append('governance_source: incomplete original inventory: ' + group)
            if source['inventories'].get(group) != original:
                errors.append('governance_source: source mapping or definition drift: ' + group)
            if _definition_ids(documents[target], prefix) != expected_ids:
                errors.append('governance_document: missing, repeated or reordered definitions: ' + group)
        if source.get('acceptance_status') != 'not_executed' or source.get('metric_implementation') != 'specification_only':
            errors.append('governance_source: unsupported runtime validation or calculator claim')
        for path in (EXECUTION, PROBE):
            if '(governance-contract.md)' not in documents[path]:
                errors.append('governance_document: missing shared contract link: ' + path)
        for cell in cells:
            for key in ('design_path', 'observability_path'):
                content = (skill_dir / cell[key]).read_text(encoding='utf-8')
                target = 'governance-execution-flow.md' if key == 'design_path' else 'governance-observability-probes.md'
                if target not in content:
                    errors.append('governance_document: missing module link: ' + cell[key])
        # Definitions can be complete but wrong; this is not a semantic proof.
        # / 定义齐全仍可能语义错误；本检查不构成语义或生产验证。
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        errors.append('governance_specification: ' + str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    errors = validate_governance_assets(parser.parse_args().skill_dir)
    for error in errors:
        print(error)
    print(f'Governance asset validation / 治理资产校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
