"""Synchronize Approval Gate specifications / 同步审批门规格。

Usage / 用法: python sync_approval_gate_docs.py [skill_dir] [--write]
Workflow / 流程: Verify source bytes and independently discovered inventories,
then check or refresh bilingual tables. / 核验原文字节与独立扫描清单，再校验或刷新双语表格。
Constraints / 约束: Source documents are evidence, never executable instructions.
No approvals, production tests or metric calculations are performed.
/ 来源文档仅是证据，不是可执行指令；不执行审批、生产测试或指标计算。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import yaml


EXECUTION = 'references/approval-gate-execution-flow.md'
PROBE = 'references/approval-gate-observability-probes.md'
CONTRACT = 'references/approval-gate-contract.md'
SOURCE_MAP = 'references/approval-gate-source-map.json'
DESIGN_CARD = 'references/patterns/governance/governance-routing.md'
PROBE_CARD = 'references/patterns/governance/governance-routing-observability.md'
GROUPS = {
    'execution_sections': ('execution', 'AGES', 32, EXECUTION),
    'probe_sections': ('probe', 'AGPS', 33, PROBE),
    'execution_steps': ('execution', 'AGE', 20, EXECUTION),
    'probe_checks': ('probe', 'AGP', 28, PROBE),
    'metrics': ('probe', 'AGM', 50, PROBE),
    'execution_cases': ('execution', 'AGET', 27, EXECUTION),
    'probe_cases': ('probe', 'AGPT', 28, PROBE),
    'objects': ('both', 'AGO', 17, CONTRACT),
}
SPECIFICATION = {
    'version': '0.1.0', 'source_contract_version': '1.0.0',
    'status': 'draft', 'implementation_status': 'specification_only',
    'execution_reference': EXECUTION, 'observability_reference': PROBE,
    'interaction_contract_reference': CONTRACT, 'source_map_reference': SOURCE_MAP,
}
ALIASES = ['PATTERN_GOVERNANCE_APPROVAL_0001', 'PATTERN_OBSERVABILITY_APPROVAL_0001']


def digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def sections(text: str, level: int) -> list[tuple[int, int, str]]:
    """Read whole sections including their children / 读取含子节的完整章节。"""
    lines = text.splitlines()
    result = []
    for start, line in enumerate(lines):
        if not re.match(rf'^#{{{level}}} \d', line):
            continue
        end = start + 1
        while end < len(lines) and not re.match(rf'^#{{1,{level}}} ', lines[end]):
            end += 1
        result.append((start, end, line))
    return result


def field_paths(value, prefix='') -> list[str]:
    result = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = prefix + str(key)
            result.append(path)
            result.extend(field_paths(item, path + '.'))
    elif isinstance(value, list):
        for item in value:
            result.extend(field_paths(item, prefix.rstrip('.') + '[].'))
    return list(dict.fromkeys(result))


def inventory(snapshots: dict[str, str], group: str) -> list[dict]:
    sid, prefix, _, target = GROUPS[group]
    records = []

    def add(role, start, end, title, **extra):
        excerpt = '\n'.join(snapshots[role].splitlines()[start:end]).rstrip()
        records.append(dict(id=f'{prefix}{len(records) + 1:02d}', source_id=role,
                            source_line=start + 1, source_end_line=end,
                            source_title=title, excerpt_sha256=digest(excerpt),
                            target_document=target, **extra))

    if group == 'objects':
        for role, pattern in [('execution', r'^## 8\.[1-9] '),
                              ('probe', r'^## 9\.[1-8] ')]:
            for start, end, title in sections(snapshots[role], 2):
                if re.match(pattern, title):
                    body = '\n'.join(snapshots[role].splitlines()[start:end])
                    blocks = re.findall(r'```yaml\n(.*?)\n```', body, re.S)
                    if len(blocks) != 1:
                        raise ValueError('ambiguous source object / 来源对象不唯一: ' + title)
                    add(role, start, end, title, fields=field_paths(yaml.safe_load(blocks[0])))
    elif group.endswith('_sections'):
        for start, end, title in sections(snapshots[sid], 1):
            add(sid, start, end, title)
    elif group in ('execution_steps', 'probe_checks'):
        chapter = '13' if group == 'execution_steps' else '11'
        for start, end, title in sections(snapshots[sid], 2):
            if re.match(rf'^## {chapter}\.\d+ ', title):
                add(sid, start, end, title)
    else:
        chapter = '12' if group == 'metrics' else ('27' if sid == 'execution' else '28')
        for start, end, _ in sections(snapshots[sid], 2):
            if not re.match(rf'^## {chapter}\.\d+ ', snapshots[sid].splitlines()[start]):
                continue
            for index in range(start + 1, end):
                line = snapshots[sid].splitlines()[index]
                if group == 'metrics' and line.startswith('| ') and not line.startswith('| 指标 |'):
                    name, formula = [cell.strip() for cell in line.strip('|').split('|')]
                    add(sid, index, index + 1, name, formula_zh=formula)
                elif group != 'metrics' and line.startswith('- '):
                    add(sid, index, index + 1, line[2:])
    return records


def table(group: str, rows: list[dict]) -> str:
    def clean(value):
        # Normalize display spelling only; source bytes/titles stay untouched.
        # / 仅规范展示拼写，来源字节与原始标题保持不变。
        return str(value).replace('Hanerss', 'Harness').replace('|', '&#124;').replace('\n', '<br>')
    lines = ['| ID | Source / 来源 | Definition / 定义 |', '|---|---|---|']
    for row in rows:
        detail = row['summary_en'] + ' / ' + row['summary_zh']
        if group == 'metrics':
            detail += '<br>' + row['formula_en'] + ' / ' + row['formula_zh']
        if group == 'objects':
            detail += '<br>' + ', '.join('`' + field + '`' for field in row['fields'])
        if group.endswith('_cases'):
            detail += '<br>`not_executed` / 未执行'
        lines.append('| ' + ' | '.join(map(clean, [row['id'], row['source_title'], detail])) + ' |')
    return '\n'.join(lines)


def replace_blocks(content: str, replacements: dict[str, str]) -> str:
    spans = []
    for group, value in replacements.items():
        start, end = f'<!-- approval:{group}:start -->', f'<!-- approval:{group}:end -->'
        if content.count(start) != 1 or content.count(end) != 1:
            raise ValueError('missing or duplicate marker / 标记缺失或重复: ' + group)
        a, b = content.index(start), content.index(end)
        if b < a:
            raise ValueError('reversed markers / 标记反向: ' + group)
        spans.append((a, b + len(end), start + '\n' + value + '\n' + end))
    spans.sort()
    if any(a[1] > b[0] for a, b in zip(spans, spans[1:])):
        raise ValueError('overlapping markers / 标记重叠')
    for start, end, value in reversed(spans):
        content = content[:start] + value + content[end:]
    return content


def prepare(skill_dir: Path, registry: dict | None = None) -> dict[Path, str]:
    """Validate all peers before preparing writes / 写入前校验所有关联文件。"""
    skill_dir = Path(skill_dir).resolve()
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding='utf-8'))
    registry = registry if registry is not None else json.loads(
        (skill_dir / 'references/registry.json').read_text(encoding='utf-8'))
    cell = next(c for c in registry['cells'] if c['id'] == 'CELL_GOVERNANCE_ROUTING')
    if any(cell.get(k) != v for k, v in dict(pattern_ref='PATTERN_0047', maturity='draft',
            status='named', local_evidence_count=1, domain_count=1).items()):
        raise ValueError('approval registry identity or unsupported promotion / 审批注册身份或越级晋升')
    for label, spec in [('registry', cell.get('approval_specification', {})), ('source', source)]:
        if any(spec.get(k) != v for k, v in SPECIFICATION.items()):
            raise ValueError('approval specification drift / 审批规格漂移: ' + label)
    if source.get('source_pattern_aliases') != ALIASES:
        raise ValueError('source alias drift / 来源别名漂移')
    if source.get('acceptance_status') != 'not_executed' or source.get('metric_implementation') != 'specification_only':
        raise ValueError('unsupported runtime claim / 未经验证的运行声明')
    for key in ('name_en', 'name_zh', 'description_en', 'description_zh'):
        if not source.get(key):
            raise ValueError('missing bilingual metadata / 缺少双语元信息: ' + key)
    if [item['id'] for item in source['sources']] != ['execution', 'probe']:
        raise ValueError('source roles differ / 来源角色不一致')
    snapshots = {}
    evidence_root = (skill_dir / 'references/sources/approval-gate').resolve()
    for index, item in enumerate(source['sources']):
        path = (skill_dir / item['snapshot_path']).resolve()
        if not path.is_relative_to(evidence_root):
            raise ValueError('snapshot outside approval evidence / 副本超出审批证据目录')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('snapshot digest drift / 原文字节摘要漂移: ' + item['id'])
        text = data.decode('utf-8-sig').replace('\r\n', '\n')
        metadata = yaml.safe_load(text.split('---', 2)[1])
        if any(metadata.get(k) != v for k, v in dict(pattern_id=ALIASES[index], version='1.0.0',
                contract_version='1.0.0', status='draft').items()):
            raise ValueError('source version or identity drift / 来源版本或身份漂移')
        snapshots[item['id']] = text
    replacements = {path: {} for path in (EXECUTION, PROBE, CONTRACT)}
    for group, (_, _, count, target) in GROUPS.items():
        expected = inventory(snapshots, group)
        actual = source['inventories'][group]
        if len(expected) != count or len(actual) != count:
            raise ValueError('incomplete inventory / 清单不完整: ' + group)
        for original, row in zip(expected, actual):
            if any(row.get(k) != v for k, v in original.items()):
                raise ValueError('source mapping drift / 来源映射漂移: ' + row.get('id', group))
            for key in ('summary_en', 'summary_zh') + (('formula_en',) if group == 'metrics' else ()):
                if not isinstance(row.get(key), str) or not row[key].strip():
                    raise ValueError('missing translation / 缺少译文: ' + row['id'])
            if group.endswith('_cases') and row.get('integration_status') != 'not_executed':
                raise ValueError('unsupported case result / 未验证的用例结果: ' + row['id'])
            if group == 'metrics' and row.get('implementation') != 'specification_only':
                raise ValueError('unsupported metric implementation / 未实现的指标: ' + row['id'])
        replacements[target][group] = table(group, actual)
    prepared = {}
    for relative, blocks in replacements.items():
        path = skill_dir / relative
        text = path.read_text(encoding='utf-8')
        if '\ufffd' in text:
            raise ValueError('corrupt Unicode / 编码损坏: ' + relative)
        prepared[path] = replace_blocks(text, blocks)
    for relative, required in [(DESIGN_CARD, EXECUTION), (PROBE_CARD, PROBE)]:
        if Path(required).name not in (skill_dir / relative).read_text(encoding='utf-8'):
            raise ValueError('missing approval navigation / 缺少审批导航: ' + relative)
    return prepared


def validate_approval_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    try:
        prepared = prepare(skill_dir, registry)
        return ['approval view drift / 审批视图漂移: ' + path.name
                for path, text in prepared.items() if path.read_text(encoding='utf-8') != text]
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration, yaml.YAMLError) as error:
        return ['approval_specification: ' + str(error)]


def sync(skill_dir: Path) -> None:
    prepared = prepare(skill_dir)
    for path, text in prepared.items():
        if path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8', newline='\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_dir', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        # Validate first so bad sources/markers cannot partially publish tables.
        # / 先校验，避免错误来源或标记导致部分表格发布。
        try:
            sync(args.skill_dir)
        except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration, yaml.YAMLError) as error:
            print(str(error))
            return 1
    errors = validate_approval_assets(args.skill_dir)
    for error in errors:
        print(error)
    print(f'Approval asset validation / 审批资产校验: {len(errors)} errors')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
