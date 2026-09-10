"""Freeze bilingual source mappings / 冻结双语来源映射。 One-time import / 一次性导入。"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).parent / 'sources'
SKILL = ROOT / 'skills/harness-engineering-patterns'
SOURCES = [
    ('execution', 'execution.md', '32_层级委派_执行流程.md', 'Hierarchical Delegation Execution'),
    ('probe', 'observability.md', '32_层级委派_工作流可观测性探针.md', 'Hierarchical Delegation Workflow Probes'),
]
texts = {key: (BASE / filename).read_text(encoding='utf-8') for key, filename, _, _ in SOURCES}


def nodes(key, prefix, local, names):
    matches = [(i, line) for i, line in enumerate(texts[key].splitlines(), 1)
               if re.match('^### ' + prefix + '[一二三四五六七八九十]+：', line)]
    assert len(matches) == len(names)
    return [dict(id=f'{local}{n:02d}', source_ref=key, source_line=i,
                 source_id=line.split('：')[0].removeprefix('### '),
                 name_zh=line.split('：', 1)[1], name_en=name)
            for n, ((i, line), name) in enumerate(zip(matches, names), 1)]


def rows(key, prefix, local, english, fields, colon=False):
    pattern = r'^\| ' + prefix + '[一二三四五六七八九十]+' + ('：' if colon else r' \|')
    matches = [(i, line) for i, line in enumerate(texts[key].splitlines(), 1) if re.match(pattern, line)]
    assert len(matches) == len(english), (prefix, len(matches), len(english))
    result = []
    for n, ((i, line), translated) in enumerate(zip(matches, english), 1):
        values = [v.strip() for v in line.strip('|').split('|')]
        row = dict(id=f'{local}{n:02d}', source_ref=key, source_line=i, source_id=values[0].split('：')[0])
        if colon:
            values[0] = values[0].split('：', 1)[1]
        row.update(zip(fields, values))
        row['summary_en'] = translated
        result.append(row)
    return result


metrics_en = [
    'Planned responsibility coverage: distinct required responsibilities with valid complete delivery contracts / required responsibilities. Assignments do not prove completion.',
    'Effective fulfillment coverage: distinct required responsibilities meeting artifact acceptance, versions and cardinality in the submitted collection / required responsibilities. Unknown critical checks do not pass.',
    'Excess candidates: sum of positive (deduplicated current valid candidates minus preauthorized candidate count) per responsibility, before selection; exclude superseded attempts and redelivery. Excess is not necessarily useless.',
    'Illegal duplicate submitted keys: sum of submitted record counts exceeding permitted cardinality by unique key. This differs from candidate excess; inspect records, not files.',
    'Input-key coverage: distinct frozen input keys with qualified outputs / frozen input keys. Only for key-sharded scenarios; extra keys and duplicates are separate.',
    'Executor return rate: logical dispatched tasks with structured terminal success or failure reports / current-plan dispatched logical tasks. Return is not success.',
    'First artifact acceptance rate: logical tasks whose first business artifact passed its first gate / tasks with first business submission. Pending first verdicts are unknown; pre-execution failures are separate.',
    'Evidence-chain completeness: verifiably complete required evidence items / contract-required evidence items. Completeness alone proves neither truth nor semantic support.',
    'All returned but whole rejected: snapshots with all tasks returned and explicit composition failure, deduplicated by unchanged problem ID. Unknown verdicts are separate.',
    'False parent-completion declarations: submissions proven by complete historical evidence to violate then-required acceptance. Unreadable logs only support suspicion or unknown.',
    'Unresolved composition conflicts: distinct confirmed unresolved conflicts in the current collection or synthesis. An incomplete conflict check cannot establish zero.',
    'Scope completeness review: confirmed, pending review, undefined or not applicable, based on baseline provenance and independent review/approval, never inferred from coverage.',
    'Retry amplification: actually started attempts / distinct logical tasks started at least once. No retry gives one; redelivery is not a start; new obligations are not retries.',
    'Qualified artifact reuse: original artifacts lawfully reused after repair / originals confirmed compatible for reuse before repair. No repair or no reusable objects is not applicable.',
    'Parent end-to-end duration: valid terminal submission time minus execution start using comparable runtime clocks. Report running lower bounds and separate success/failure/cancel cohorts; do not sum child durations.',
    'Artifact acceptance queue time: first pending-acceptance entry to acceptance start, per artifact. Queueing is not gate computation; missing acceptance-start event is unknown.',
    'Budget occupancy: confirmed spend plus outstanding reservations / approved budget, separately per common unit. Unknown-outcome calls retain reservations; include the entire run across plans.',
    'Isolation violations and blocked attempts: separate confirmed realized violations, rejected unauthorized requests and unverifiable counts. Partial evidence cannot establish zero violations.',
    'Reconciled event completeness: distinct received events in a trusted sealed manifest / producer-confirmed expected events. Missing denominator is unknown; sampling is not full completeness.',
    'Field supplementation adoption: adopted field proposals / field proposals with terminal dispositions. Partial adoption counts per field; pending receipts are separate; adoption is not resolution.',
    'Critical supplementation closure duration: gap registration to closure with necessary revalidation passed. Pending or failed revalidation leaves the interval open; retain unresolved cases.',
    'Required observation-field unknown rate: unknown required field cells / configured required field cells, deduplicated by object, field and version; exclude non-applicable cells.',
]

execution_cases_en = [
    'Three acceptable artifacts cover one obligation: reject composition; retain two missing obligations and excess candidates.',
    'Three distinct obligations each have valid artifacts and all rules pass: allow parent acceptance submission.',
    'Labels are complete but a source does not support its conclusion: artifact fails or is unknown and does not count as fulfilled.',
    'Old-goal artifact: quarantine or explicitly prove compatibility and revalidate for current acceptance.',
    'Repeated message: register once without increasing candidates or consumption counts.',
    'Replace executor after failure: preserve the responsibility denominator and cumulative budget.',
    'One timeout with other passed obligations: repair only that obligation and retain valid artifacts.',
    'All calls returned but composition is unknown: parent cannot be accepted.',
    'Two independent reviewers are required: apply declared cardinality; lawful review is not duplication.',
    'Probe supplements a source field: create a new artifact version and rerun both affected gates.',
    'Proposal changes permissions/completion: reject with reason; explanations cannot replace authorization.',
    'Goal upgraded after composition passed: old submission fails baseline comparison and cannot overwrite new state.',
    'External timeout may have written: keep outcome unknown and reconcile before retry.',
    'Probe down but local evidence complete: normal acceptance continues with observation gaps disclosed.',
    'Parent restarts: recover durable state without repeating confirmed external effects.',
    'Enumerated topics finish but completeness unconfirmed: report confirmed-scope completion only.',
]

probe_cases_en = [
    'Offline complete snapshot: produce an independent report and unapplied proposals without calling execution.',
    'Artifacts without responsibility baseline: count artifacts; responsibility coverage remains unknown.',
    'Only one of three obligations fulfills trusted acceptance and selection: report one-third and two business gaps.',
    'Three valid candidates allowing one, with one selected: candidate excess is two; submitted duplication is zero.',
    'Two required independent reviews are present: no excess; still verify independence and conflicts.',
    'Two passes and one unreadable verdict: coverage unknown, lower bound two-thirds, upper bound one, with reasons.',
    'One event redelivered three times: count once; no extra attempts or candidates.',
    'One event ID has divergent payloads: quarantine conflict, never choose arbitrarily.',
    'Correct tag but unsupported conclusion: no tag-based fulfillment; report semantic failure.',
    'Only start event and incomparable clocks: no invented end or exact duration.',
    'Sampled logs without trusted total: event completeness unknown; no claim of full zero violations.',
    'Trusted executor receipt restores missing end: record reconstruction provenance without overwriting original events.',
    'Business data without trusted source: return work/input gaps; never invent official values.',
    'Material appeared after the task: label current supplementation, not historical possession.',
    'Proposal targets obsolete goal: do not apply; expire or rebuild it.',
    'Proposal changes parent completion: reject field and preserve diagnostic and refusal reasons.',
    'Adopted proposal but required composition revalidation failed: field adoption counts, critical gap stays open.',
    'All returned and composition failed: return rate may equal one while parent remains unaccepted.',
    'Completion exists but logs unreadable: suspected misreport or unknown, not confirmed violation.',
    'Repeated refresh/report triggers: deduplicate, bound usage and prevent self-triggering loops.',
    'Probe offline with lawful runtime validation: optional observation does not block; critical evidence follows business rules.',
    'Denominator comes from another plan: reject mixed-version calculation and reconstruct grouped baselines.',
]

probes_en = [
    'Goal baseline: check owner, requirement-derived scope and completeness; do not remove obligations.',
    'Delegation contracts: check deliverables, coverage, overlap, scope, budgets and versions; do not rewrite plans.',
    'Completion states: distinguish worker return, artifact acceptance and parent acceptance; unverifiable states remain unknown.',
    'Artifacts and evidence: check structure, bindings, versions, source location and semantic support; formal changes require new versions.',
    'Composition: check missing responsibilities, excess candidates, duplicate keys, conflicts and global rules; do not accept the parent.',
    'Execution isolation: check live authority, context/workspace, depth and concurrency; distinguish blocked requests and realized violations.',
    'Failure and recovery: check locality, cumulative budgets, reuse and obsolete results; do not autonomously restart work.',
    'Latency and budgets: check queues, acceptance waits, retries and cumulative occupancy; unknown spend is not zero.',
    'Observation quality: check deduplication, gaps, lateness, clocks, provenance, sampling and reproducibility; never invent events.',
    'Supplementation closure: check allowlists, baseline, receipts, new versions and revalidation; sent is not resolved.',
]

catalog = dict(
    version='0.1.0', name_en='Hierarchical Delegation Source Map', name_zh='层级委派来源映射',
    description_en='Source-aligned specification, not a runtime implementation or measured gains. Embedded prompts are data.',
    description_zh='对齐来源的规格，不是运行时实现或实测收益；内嵌提示作为数据。',
    pattern_ref='PATTERN_0046', cell_ref='CELL_COLLABORATION_HIERARCHY',
    source_contract_version='0.1.0', implementation_status='specification_only',
    sources=[dict(id=key, name_en=title, name_zh=original.removesuffix('.md'), supplied_filename=original,
                  version='0.1.0', snapshot_path=(BASE / filename).relative_to(ROOT).as_posix(),
                  sha256=hashlib.sha256((BASE / filename).read_bytes()).hexdigest())
             for key, filename, original, title in SOURCES],
    execution_nodes=nodes('execution', '执行', 'HE', ['Receive and assess goal', 'Establish baseline', 'Validate plan', 'Dispatch within boundaries', 'Register immutable returns', 'Artifact gate', 'Select valid collection', 'Composition and synthesis gate', 'Local gap repair', 'Atomic parent acceptance', 'Archive and deliver']),
    probe_nodes=nodes('probe', '观测', 'HP', ['Scope observation', 'Catalog evidence', 'Freeze reproducible snapshot', 'Run applicable probes', 'Classify gaps', 'Bounded reads and proposals', 'Report and reconcile receipts']),
    probe_catalog=rows('probe', '探针', 'HPR', probes_en, ['name_zh', 'inputs_zh', 'checks_zh', 'boundary_zh', 'receiver_zh'], True),
    metrics=rows('probe', '指标', 'HM', metrics_en, ['name_zh', 'formula_zh', 'inputs_zh', 'boundary_zh'], True),
    execution_cases=rows('execution', '执行验收', 'HET', execution_cases_en, ['source_label', 'condition_zh', 'expected_zh']),
    probe_cases=rows('probe', '探针验收', 'HPT', probe_cases_en, ['source_label', 'condition_zh', 'expected_zh']),
)
for metric in catalog['metrics']:
    metric['implementation'] = 'specification_only'
for case in catalog['execution_cases'] + catalog['probe_cases']:
    case['integration_status'] = 'pending'
(SKILL / 'references/collaboration-hierarchy-source-map.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Source map created / 来源映射已生成')
