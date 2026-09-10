"""Render/check collaboration registry views / 生成并校验协作注册表视图。

Usage / 用法: python sync_collaboration_docs.py [skill_dir] [--write]
Only marked sections are generated; the registry and schema remain sources.
/ 仅生成标记区块，注册表与 Schema 始终是源数据。
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


EXECUTION = "references/collaboration-execution-flow.md"
PROBES = "references/collaboration-observability-probes.md"
CATALOG = "references/collaboration-protocol.json"
SCHEMA = "schemas/collaboration-record.schema.json"
SOURCE_MAP = "references/collaboration-fulltext-source-map.json"
MODES = {
    "hierarchical_delegation": "CELL_COLLABORATION_HIERARCHY",
    "fan_out_gather": "CELL_COLLABORATION_PARALLEL",
    "adversarial_review": "CELL_COLLABORATION_LOOP",
    "handoff_chain": "CELL_COLLABORATION_CHAIN",
}


def _cell(text: str) -> str:
    return text.replace("|", "&#124;").replace("\n", " ")


def _type(rule: dict) -> str:
    if "$ref" in rule:
        return rule["$ref"].rsplit("/", 1)[-1]
    if "const" in rule:
        return json.dumps(rule["const"], ensure_ascii=False)
    if "enum" in rule:
        return " / ".join(json.dumps(value, ensure_ascii=False) for value in rule["enum"])
    if "anyOf" in rule:
        return " or ".join(_type(item) for item in rule["anyOf"])
    kind = rule.get("type", "JSON")
    if kind == "array":
        kind += "<" + _type(rule["items"]) + ">"
    if kind == "object" and isinstance(rule.get("additionalProperties"), dict):
        kind += "<key, " + _type(rule["additionalProperties"]) + ">"
    details = [f"{key}={rule[key]}" for key in
               ("minLength", "minimum", "minItems", "uniqueItems", "pattern", "format") if key in rule]
    return kind + ("; " + "; ".join(details) if details else "")


def contract_view(schema: dict) -> str:
    lines = [
        "Source contract / 来源契约: `2.0.0`; local executable profile / 本地可执行配置: `3.0.0`. Normative local shape / 本地规范结构: [collaboration-record.schema.json](../schemas/collaboration-record.schema.json).",
        "",
        "Intent follows messages; truth follows references; results follow artifacts; responsibility follows acceptance. Both supplied documents embed the same source contract. The schema below is a stricter local projection, not a verbatim or wire-compatible implementation. / 意图随消息、真值随引用、结果随工件、责任随验收。两份附件内置相同的来源契约。以下 Schema 是更严格的本地投影，不是逐字复制或线格式兼容实现。",
        "",
        "Every listed field is required unless its type explicitly permits null; nested objects reject undeclared fields except public content and declared maps. Empty lists mean none, not unknown. / 下列字段均必填，只有类型明确允许时可为 null；嵌套对象拒绝未声明字段，公开 content 与声明的映射除外。空列表表示没有，不表示未知。",
        "",
        "| Record / 记录 | Field / 字段 | Type and constraints / 类型与约束 |",
        "| --- | --- | --- |",
    ]

    def fields(label: str, shape: dict, prefix: str = "") -> None:
        for key, rule in shape.get("properties", {}).items():
            path = prefix + key
            lines.append(f"| {label} | `{path}` | {_cell(_type(rule))} |")
            if rule.get("type") == "object" and "properties" in rule:
                fields(label, rule, path + ".")
            if rule.get("type") == "array" and "properties" in rule.get("items", {}):
                fields(label, rule["items"], path + "[].")

    fields("Envelope / 信封", schema)
    for name, shape in schema["$defs"].items():
        fields(shape["title"] + f" (`{name}`)", shape)
    lines.extend([
        "",
        "`record_hash` hashes UTF-8 canonical JSON with sorted keys, compact separators and finite numbers, excluding only itself. `content_digest` separately hashes public `content`. Bindings compare id, revision and digest within one tenant, request, run, scope and plan revision. Active attempts also bind worker, delegation epoch and input snapshot. / `record_hash` 对按键排序、紧凑分隔且仅含有限数的 UTF-8 规范 JSON 计算哈希，仅排除自身；`content_digest` 独立哈希公开内容。绑定须核对标识、修订、摘要及租户、请求、运行、范围、计划版本；有效尝试还须绑定执行者、委派代次与输入快照。",
        "",
        "A host verifier must authenticate record actors, source provenance and the current authoritative inventory. An always-true verifier is suitable only for a controlled test fixture. Hashes and self-declared roles cannot establish authority. / 宿主核验器必须验证记录参与者身份、来源与当前权威清单；恒真的核验器仅适用于受控测试夹具。哈希和自报角色不能建立权限。",
        "",
        "Use one stable receipt ID per task, result and stage; a higher revision supersedes the same receipt ID. Conflicting active receipts or adjudications block release. The snapshot fixes current task and result heads and must list the complete applicable evidence and objection inventory. / 每个任务、工件与验收阶段使用一个稳定回执 ID；同 ID 的更高修订取代旧修订。冲突的当前回执或裁决阻断放行。快照固定当前任务与工件版本，并必须列出适用证据与异议的完整清单。",
        "",
        "Arrival, local acceptance, global acceptance, actual delivery and responsibility transfer are distinct facts. `acceptance_ready` indicates configured acceptance gates pass; `allowed` additionally requires the matching actual delivery receipt. Handoff checks an authenticated atomic transfer attestation; the host performs and persists the conditional owner/epoch update. / 材料到达、局部验收、全局验收、实际交付和责任转移分别记录。`acceptance_ready` 表示已配置验收闸门通过；`allowed` 还要求匹配的实际交付凭据。交接核验经认证的原子转移回执，宿主负责执行并持久化有条件的负责人和代次更新。",
        "",
        "Gap routing / 缺口路由: `business_incomplete` returns to execution; `business_evidence` adoption needs a candidate-consuming business recheck; `observation_record` adoption needs an observation repair receipt; `authorization` requires the authority workflow; `unclassified` cannot be auto-repaired. / 业务未完成回执行侧；业务证据采纳须消费候选的业务复验；观测记录采纳须观测修复回执；权限缺口交授权流程；未分类缺口不能自动修复。探针不改变业务成功状态。",
        "",
        "Supplement intake verifies current target, attempt, input, source, field allowlist, authorization, explicit host time and bounded cumulative reads/rounds. `gap_usage` is the host-attested usage immediately before this package. Historical adoption is checked at its recorded disposition time; expiry later does not erase valid history. The host owns idempotent persistence and concurrency control. / 补证接入核验当前目标、尝试、输入、来源、字段白名单、授权、显式宿主时间及累计读取和轮次预算。`gap_usage` 是宿主证明的本包接入前用量。历史采纳按其处置时刻检查，后续过期不抹掉有效历史；幂等持久化和并发控制由宿主负责。",
        "",
        "Role separation follows declared policy; low-risk owner/acceptor sharing is permitted only when separation is not required. Adversarial proposer, reviewer and arbiter remain distinct responsibility subjects, without requiring different model vendors. Business obligations are separate from optional telemetry. Missing optional observation cannot invalidate independently supported business checks. / 角色分离服从声明策略，低风险主责和验收仅在不要求分离时可兼任；对抗提案、评审、裁决仍为独立责任主体，不强制不同模型厂商。业务义务与可选观测分开；缺少额外观测不能取消独立具备依据的业务校验。",
        "",
        "Migration must map source fields explicitly and obtain missing authoritative bindings. Changing a version label or synthesizing identity, attempt, digest, approval or success fields is not migration. Local 2.0.0 records are rejected by profile 3.0.0. / 迁移必须显式映射来源字段并补齐权威绑定；改版本号或伪造身份、尝试、摘要、审批、成功字段不构成迁移。本地旧 2.0.0 记录不能直接通过 3.0.0 配置。",
    ])
    return "\n".join(lines)


def views(skill_dir: Path) -> dict[str, dict[str, str]]:
    source = json.loads((skill_dir / SOURCE_MAP).read_text(encoding="utf-8"))
    schema = json.loads((skill_dir / SCHEMA).read_text(encoding="utf-8"))
    shared = contract_view(schema)
    return {
        EXECUTION: {"contract": shared, "execution_nodes": _source_table(source["execution_nodes"], "nodes"),
                    "execution_cases": _source_table(source["execution_cases"], "cases")},
        PROBES: {"contract": shared, "probe_nodes": _source_table(source["probe_nodes"], "nodes"),
                 "metrics": _source_table(source["source_metrics"], "metrics"),
                 "probe_cases": _source_table(source["probe_cases"], "cases")},
    }


def _source_table(rows: list[dict], kind: str) -> str:
    """Source IDs retain their meanings; local IDs are not aliases / 来源编号保持原意，本地编号不充当别名。"""
    if kind == "metrics":
        lines = ["| ID / 来源 | Metric / 指标 | Formula / 口径 | Unit / 单位 | Support / 支持 | Source boundary / 原文边界 |",
                 "| --- | --- | --- | --- | --- | --- |"]
        for row in rows:
            support = "Reference / 参考计算" if row["implementation"] == "reference" else "Adapter required / 待适配"
            values = [row["id"] + " / " + row["source_id"], row["name_en"] + " / " + row["name_zh"],
                      row["formula_en"] + " / " + row["formula_zh"], row["unit"], support, row["boundary_zh"]]
            lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
    elif kind == "cases":
        lines = ["| Source ID / 来源编号 | Scenario / 场景 | Expected / 预期 | Reference coverage / 参考覆盖 | Integration / 集成 |",
                 "| --- | --- | --- | --- | --- |"]
        for row in rows:
            tests = ", ".join("`" + ref.split("::")[-1] + "`" for ref in row["reference_tests"])
            values = [row["source_id"], row["condition_en"] + " / " + row["condition_zh"],
                      row["expected_en"] + " / " + row["expected_zh"],
                      ("Partial / 部分: " + tests) if tests else "Pending / 待覆盖", "Pending / 待验证"]
            lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
    else:
        lines = ["| Source ID / 来源编号 | Node / 节点 | Related local nodes / 相关本地节点 |", "| --- | --- | --- |"]
        for row in rows:
            lines.append(f"| {row['source_id']} | {row['name_en']} / {row['name_zh']} | {', '.join(row['local_refs'])} |")
    return "\n".join(lines)


def _validate_source_map(skill_dir: Path, source: dict, catalog: dict) -> list[str]:
    errors = []
    project = skill_dir.parent.parent
    snapshots = []
    for item in source["sources"]:
        data = (project / item["snapshot_path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            errors.append("collaboration_source: snapshot digest drift")
        snapshots.append(data.decode("utf-8"))
    appendices = [text[text.index("## 附录甲"):text.index("## 附录乙")] for text in snapshots]
    if len(appendices) != 2 or appendices[0] != appendices[1] or hashlib.sha256(appendices[0].encode()).hexdigest() != source["shared_appendix_sha256"]:
        errors.append("collaboration_source: shared source appendix drift")
    for key, prefix, start, count, source_index in [("source_metrics", "指", 1, 34, 1),
             ("execution_cases", "测", 1, 28, 0), ("probe_cases", "探测", 1, 38, 1),
             ("execution_nodes", "执", 0, 13, 0), ("probe_nodes", "观", 0, 11, 1)]:
        rows = source[key]
        if [row["source_id"] for row in rows] != [f"{prefix}{i:02d}" for i in range(start, start + count)]:
            errors.append("collaboration_source: source ID drift in " + key)
        for row in rows:
            line = snapshots[source_index].splitlines()[row["source_line"] - 1]
            fields = ["condition_zh", "expected_zh"] if key.endswith("cases") else ["name_zh"]
            if key == "source_metrics":
                fields += ["formula_zh", "boundary_zh"]
            if any(row[field] not in line for field in fields) or row["source_id"] not in line:
                errors.append("collaboration_source: source text drift in " + row["source_id"])
            bilingual = ["condition_en", "expected_en"] if key.endswith("cases") else ["name_en"]
            if any(not row.get(field) for field in bilingual):
                errors.append("collaboration_source: missing English explanation")
            if key.endswith("cases"):
                if row["integration_status"] != "pending":
                    errors.append("collaboration_source: unsupported integration claim")
                for ref in row["reference_tests"]:
                    relative, name = ref.split("::")
                    tree = ast.parse((project / relative).read_text("utf-8"))
                    if name not in {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}:
                        errors.append("collaboration_source: missing reference test " + ref)
            if key.endswith("nodes"):
                locals_by_id = {node["id"] for node in catalog[key]}
                if not row["local_refs"] or any(ref not in locals_by_id for ref in row["local_refs"]):
                    errors.append("collaboration_source: unknown related local node")
    if [row["id"] for row in source["source_metrics"]] != [f"CSM{i:02d}" for i in range(1, 35)]:
        errors.append("collaboration_source: stable source metric ID drift")
    return errors


def validate_collaboration_assets(skill_dir: Path, registry: dict | None = None) -> list[str]:
    """Check real references, mode mappings and generated contract equality / 核验引用、模式映射及派生契约一致性。"""
    errors = []
    try:
        registry = registry or json.loads((skill_dir / "references/registry.json").read_text(encoding="utf-8"))
        modules = registry.get("module_protocols", [])
        entries = [item for item in modules if item.get("id") == "MODULE_COLLABORATION"]
        if len(entries) != 1:
            return ["collaboration_registry: exactly one module entry required"]
        entry = entries[0]
        if (entry.get("version") != "3.0.0" or entry.get("source_contract_version") != "2.0.0"
                or entry.get("status") != "draft" or entry.get("mode_cells") != MODES):
            errors.append("collaboration_registry: version, status or mode mapping drift")
        for field, path in {"execution_reference": EXECUTION, "observability_reference": PROBES,
                            "catalog_reference": CATALOG, "schema_reference": SCHEMA,
                            "runtime_reference": "runtime/collaboration_protocol.py",
                            "source_map_reference": SOURCE_MAP,
                            "observation_adapter_reference": "references/collaboration-observation-adapter.md",
                            "observation_runtime_reference": "runtime/collaboration_observability.py"}.items():
            if entry.get(field) != path or not (skill_dir / path).is_file():
                errors.append("collaboration_registry: missing or invalid " + field)
        cells = {item["id"]: item for item in registry["cells"]}
        if any(key not in cells or cells[key]["status"] != "named" for key in MODES.values()):
            errors.append("collaboration_registry: unregistered mode")
        catalog = json.loads((skill_dir / CATALOG).read_text(encoding="utf-8"))
        schema = json.loads((skill_dir / SCHEMA).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        if (catalog["protocol_version"] != "3.0.0" or schema["properties"]["protocol_version"] != {"const": "3.0.0"}
                or catalog["source_contract_version"] != "2.0.0"
                or schema["properties"]["source_contract_version"] != {"const": "2.0.0"}):
            errors.append("collaboration_contract: protocol version drift")
        for key, prefix, count in [("execution_nodes", "CE", 13), ("probe_nodes", "CP", 11),
                                   ("metrics", "CM", 34), ("execution_cases", "CET", 28), ("probe_cases", "CPT", 38)]:
            items = catalog[key]
            if [item["id"] for item in items] != [f"{prefix}{i:02d}" for i in range(1, count + 1)]:
                errors.append("collaboration_catalog: invalid stable IDs in " + key)
            if any(not item.get("name_en") or not item.get("name_zh") for item in items):
                errors.append("collaboration_catalog: bilingual names required in " + key)
        probes = {item["id"] for item in catalog["probe_nodes"]}
        if any(item["probe_ref"] not in probes for item in catalog["metrics"]):
            errors.append("collaboration_catalog: unknown metric probe")
        source = json.loads((skill_dir / SOURCE_MAP).read_text("utf-8"))
        errors.extend(_validate_source_map(skill_dir, source, catalog))
        for relative, sections in views(skill_dir).items():
            text = (skill_dir / relative).read_text(encoding="utf-8")
            for section, expected in sections.items():
                block = f"<!-- collaboration:{section}:start -->\n{expected}\n<!-- collaboration:{section}:end -->"
                if text.count(block) != 1:
                    errors.append(f"collaboration_view: {relative} has stale or missing {section}")
    except (OSError, ValueError, KeyError, TypeError, SchemaError) as error:
        errors.append("collaboration_contract: " + str(error))
    return errors


def sync(skill_dir: Path) -> None:
    """Regenerate bounded derived sections / 重建边界明确的派生区块。"""
    for relative, sections in views(skill_dir).items():
        path = skill_dir / relative
        text = path.read_text(encoding="utf-8")
        for section, content in sections.items():
            start, end = f"<!-- collaboration:{section}:start -->", f"<!-- collaboration:{section}:end -->"
            pattern = re.escape(start) + r".*?" + re.escape(end)
            text, count = re.subn(pattern, lambda _: start + "\n" + content + "\n" + end, text, flags=re.S)
            if count != 1:
                raise ValueError(f"Expected one generated block: {relative} {section}")
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        sync(args.skill_dir)
    errors = validate_collaboration_assets(args.skill_dir)
    for error in errors:
        print(error)
    print(f"Collaboration validation / 协作校验: {len(errors)} errors")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
