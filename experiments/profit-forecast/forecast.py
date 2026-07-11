#!/usr/bin/env python3
"""Аудируемый калькулятор вероятности прибыльности MAVO.

Форма (по решению владельца): произведение вероятностей звеньев по группам —
AND-цепочка Ставки «все звенья должны оказаться правдой одновременно». БЕЗ Monte
Carlo: входы (V/A/B) не оцифрованы, строгость на них была бы ложной точностью.

- Наивное произведение = КОНСЕРВАТИВНЫЙ пол: положительная корреляция звеньев
  поднимает совместную вероятность выше произведения. Для go/no-go этого хватает.
- Интервал = [произв p_low, произв p_high]; ширину доминирует слабейшее звено.
- Sensitivity one-at-a-time = рычаги: какой замер купить первым.
- Приоры p_* — self_canon owner-judgment до pre-pilot; это НЕ калиброванные частоты.

Каждая клетка видна: число раскладывается на звенья руками.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
NODES_PATH = ROOT / "nodes.csv"
CONFIGURATIONS_PATH = ROOT / "configurations.json"
GROUPS = ("pilot", "unit", "scale")
PROBABILITY_FIELDS = ("p_low", "p_base", "p_high")

# Денежный слой — сценарии из Расчёт_прибыли.md (доход/мес, микс уже заложен).
# contribution = доход × (1 − доля V+A+B); допущение V+A+B ≤ 40% сбора; фикс 50 000 ₸/мес.
FIXED_MONTHLY = 50_000
VAB_SHARE_ASSUMED = 0.40  # рабочее допущение; kill-порог — V+A+B > сбор
MONEY_SCENARIOS = {
    "пессимизм": 6_800,   # 20 позиций, микс 90/10/0, средний сбор 340 ₸
    "база": 27_000,       # ~50 позиций, микс 60/30/10, средний сбор 540 ₸
    "оптимизм": 62_000,   # 100 позиций, микс 50/35/15, средний сбор 620 ₸
}

GROUP_TITLE = {
    "pilot": "Y_pilot — пилот докажет жизнеспособный клин",
    "unit": "Y_unit — unit-экономика положительна",
    "scale": "Y_scale — связка защищаема на масштабе",
}


def prod(values: list[float]) -> float:
    result = 1.0
    for value in values:
        result *= value
    return result


def pct(value: float) -> str:
    return f"{round(value * 100)}%"


def load_nodes(path: Path = NODES_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        row["active"] = True
    return rows


def load_configurations(path: Path = CONFIGURATIONS_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    configurations = payload.get("configurations")
    if not isinstance(configurations, list) or not configurations:
        raise ValueError(f"{path} must contain a non-empty configurations list")
    return configurations


def configurations_by_id(configurations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for config in configurations:
        config_id = config.get("config_id")
        if not config_id:
            raise ValueError("configuration is missing config_id")
        if config_id in by_id:
            raise ValueError(f"duplicate configuration id: {config_id}")
        by_id[config_id] = config
    return by_id


def config_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "no", "нет"}
    return bool(value)


def node_is_active(node: dict[str, Any]) -> bool:
    return config_bool(node.get("active", True))


def probability_value(node: dict[str, Any], field: str) -> float:
    if not node_is_active(node):
        return 0.0
    return float(node[field])


def checked_probability(value: Any, field: str, node_id: str) -> float:
    number = float(value)
    if number < 0 or number > 1:
        raise ValueError(f"{node_id}.{field} must be in [0, 1], got {number}")
    return number


def apply_configuration(nodes: list[dict[str, Any]], configuration: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply a business decision configuration without mutating the base node table.

    `active=false` means the requirement is dead under this business design. It
    still remains in the goal map and contributes zero to the relevant group.
    """
    configured = [dict(node, active=True, config_reason="baseline") for node in nodes]
    nodes_by_id = {node["node_id"]: node for node in configured}

    for override in configuration.get("node_overrides", []):
        node_id = override.get("node_id")
        if node_id not in nodes_by_id:
            raise ValueError(f"{configuration.get('config_id')}: unknown node override {node_id!r}")

        node = nodes_by_id[node_id]
        if "active" in override:
            node["active"] = config_bool(override["active"])
        if "source_strength" in override:
            node["source_strength"] = override["source_strength"]
        if "status" in override:
            node["status"] = override["status"]
        if "reason" in override:
            node["config_reason"] = override["reason"]

        if not node_is_active(node):
            for field in PROBABILITY_FIELDS:
                node[field] = 0.0
            node.setdefault("status", "отключено конфигурацией")

        for field in PROBABILITY_FIELDS:
            if field in override:
                node[field] = checked_probability(override[field], field, node_id)

    return configured


def summarize_node(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": node["node_id"],
        "zveno": node["zveno"],
        "gate_role": node["gate_role"],
        "group": node["group"],
        "status": node["status"],
        "source_strength": node["source_strength"],
        "active": node_is_active(node),
        "p_low": probability_value(node, "p_low"),
        "p_base": probability_value(node, "p_base"),
        "p_high": probability_value(node, "p_high"),
        "kill_criterion": node.get("kill_criterion", ""),
        "lever_evidence": node.get("lever_evidence", ""),
        "evidence_stage": node.get("evidence_stage", ""),
        "source": node.get("source", ""),
        "config_reason": node.get("config_reason", ""),
    }


def group_number(nodes: list[dict[str, Any]], group: str) -> dict[str, Any]:
    members = [n for n in nodes if n["group"] == group]
    if not members:
        raise ValueError(f"no nodes for group {group!r}")
    base = prod([probability_value(n, "p_base") for n in members])
    low = prod([probability_value(n, "p_low") for n in members])
    high = prod([probability_value(n, "p_high") for n in members])
    worst = min(members, key=lambda n: probability_value(n, "p_base"))
    ranked = sensitivity(members, base)
    top_node, top_swing = ranked[0]
    return {
        "group": group,
        "title": GROUP_TITLE[group],
        "members": [summarize_node(node) for node in members],
        "base": base,
        "low": low,
        "high": high,
        "worst": summarize_node(worst),
        "top_lever": summarize_node(top_node),
        "top_lever_swing": top_swing,
    }


def sensitivity(members: list[dict[str, Any]], base: float) -> list[tuple[dict[str, Any], float]]:
    """swing звена = как двигает произведение сдвиг этого звена low->high (остальные base)."""
    rows = []
    for node in members:
        p_base = probability_value(node, "p_base")
        rest = base / p_base if p_base else 0.0
        swing = rest * (probability_value(node, "p_high") - probability_value(node, "p_low"))
        rows.append((node, swing))
    return sorted(rows, key=lambda item: -item[1])


def score_nodes(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "groups": {group: group_number(nodes, group) for group in GROUPS},
        "kill_gates": [summarize_node(node) for node in nodes if node["gate_role"] == "hard_gate"],
    }


def score_configuration(nodes: list[dict[str, Any]], configuration: dict[str, Any]) -> dict[str, Any]:
    configured_nodes = apply_configuration(nodes, configuration)
    return {
        "configuration": {
            "config_id": configuration["config_id"],
            "label": configuration.get("label", configuration["config_id"]),
            "decisions": configuration.get("decisions", {}),
            "defeaters": configuration.get("defeaters", []),
        },
        "forecast": score_nodes(configured_nodes),
        "nodes": [summarize_node(node) for node in configured_nodes],
    }


def changed_decisions(from_config: dict[str, Any], to_config: dict[str, Any]) -> list[dict[str, Any]]:
    from_decisions = from_config.get("decisions", {})
    to_decisions = to_config.get("decisions", {})
    changes = []
    for key in sorted(set(from_decisions) | set(to_decisions)):
        before = from_decisions.get(key)
        after = to_decisions.get(key)
        if before != after:
            changes.append({"decision": key, "from": before, "to": after})
    return changes


def changed_nodes(from_nodes: list[dict[str, Any]], to_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    to_by_id = {node["node_id"]: node for node in to_nodes}
    changes = []
    for before in from_nodes:
        after = to_by_id[before["node_id"]]
        before_summary = summarize_node(before)
        after_summary = summarize_node(after)
        watched_fields = ("active", "p_low", "p_base", "p_high", "source_strength")
        if any(before_summary[field] != after_summary[field] for field in watched_fields):
            changes.append({
                "node_id": before["node_id"],
                "zveno": before["zveno"],
                "from": {field: before_summary[field] for field in watched_fields},
                "to": {field: after_summary[field] for field in watched_fields},
                "from_reason": before_summary["config_reason"],
                "to_reason": after_summary["config_reason"],
            })
    return changes


def compare_configurations(
    nodes: list[dict[str, Any]],
    from_config: dict[str, Any],
    to_config: dict[str, Any],
    basis_group: str = "pilot",
) -> dict[str, Any]:
    if basis_group not in GROUPS:
        raise ValueError(f"basis_group must be one of {GROUPS}, got {basis_group!r}")

    from_nodes = apply_configuration(nodes, from_config)
    to_nodes = apply_configuration(nodes, to_config)
    from_score = score_nodes(from_nodes)
    to_score = score_nodes(to_nodes)
    from_basis = from_score["groups"][basis_group]["base"]
    to_basis = to_score["groups"][basis_group]["base"]
    recommended_config_id = to_config["config_id"] if to_basis >= from_basis else from_config["config_id"]

    group_deltas = {}
    for group in GROUPS:
        before = from_score["groups"][group]["base"]
        after = to_score["groups"][group]["base"]
        group_deltas[group] = {"from": before, "to": after, "delta": after - before}

    return {
        "status": "model_recommendation",
        "basis_group": basis_group,
        "from_config_id": from_config["config_id"],
        "to_config_id": to_config["config_id"],
        "recommended_config_id": recommended_config_id,
        "owner_gate": "owner_accepts_risk_before_canon_patch",
        "honesty_lock": "score moves only by decision configuration or stronger evidence, not prettier canon prose",
        "changed_decisions": changed_decisions(from_config, to_config),
        "changed_nodes": changed_nodes(from_nodes, to_nodes),
        "group_deltas": group_deltas,
        "from_evaluation": score_configuration(nodes, from_config),
        "to_evaluation": score_configuration(nodes, to_config),
        "defeaters": to_config.get("defeaters", []),
    }


def print_forecast_report(nodes: list[dict[str, Any]]) -> None:
    result = score_nodes(nodes)

    print("=" * 70)
    print("ВЕРОЯТНОСТЬ ПРИБЫЛЬНОСТИ MAVO — аудируемый лист (первый заход)")
    print("Приоры: self_canon owner-judgment до pre-pilot. Числа НЕ калиброваны.")
    print("=" * 70)

    # Статус прежде числа: сначала kill-gates и их статус.
    print("\n[KILL-GATES — статус ведёт прежде скаляра]")
    for node in nodes:
        if node["gate_role"] == "hard_gate":
            print(f"  {node['node_id']} {node['zveno']:<20} статус: {node['status']:<9}"
                  f" kill: {node['kill_criterion'][:52]}")
    print("  (вердикт Ставка_MAVO 2026-07-02: kill-критерии НЕ сработали; идея жива, не доказана)")

    # Рычаг считается ВНУТРИ группы: pilot/unit/scale — разные вопросы, их
    # рычаги не сравнимы между собой (иначе одиночное звено ложно лидирует).
    print("\n[РЫЧАГИ — что мерить первым, отдельно по каждому вопросу]")
    for group in GROUPS:
        group_result = result["groups"][group]
        print(f"\n[{GROUP_TITLE[group]}]")
        print(f"  Число (наивный пол): {pct(group_result['base'])}"
              f"   интервал: {pct(group_result['low'])} … {pct(group_result['high'])}")
        print(f"  Слабейшее звено (тянет вниз и расширяет): "
              f"{group_result['worst']['node_id']} {group_result['worst']['zveno']} "
              f"[{pct(group_result['worst']['p_low'])}…{pct(group_result['worst']['p_high'])}]")
        top_node = group_result["top_lever"]
        print(f"  РЫЧАГ №1: {top_node['node_id']} {top_node['zveno']} "
              f"(влияние {group_result['top_lever_swing']:.3f}, измеримо на стадии: {top_node['evidence_stage']})")
        print(f"      закрывает: {top_node['lever_evidence']}")
        print("  Вклад звеньев:")
        for node in group_result["members"]:
            print(f"    {node['node_id']} {node['zveno']:<20} "
                  f"{pct(node['p_base'])}  [{pct(node['p_low'])}…{pct(node['p_high'])}]  "
                  f"{node['gate_role']:<12} стадия:{node['evidence_stage']}")

    # Денежный слой — ОТДЕЛЬНО, не смешан в вероятность (сценарии break-even).
    print("\n[ДЕНЕЖНЫЙ СЛОЙ — сценарии break-even по студиям (при V+A+B ≤ 40% сбора)]")
    print(f"  Фикс {FIXED_MONTHLY:,} ₸/мес; допущение V+A+B ≤ {int(VAB_SHARE_ASSUMED*100)}% сбора"
          f" (kill: V+A+B > сбор)")
    for name, income in MONEY_SCENARIOS.items():
        contribution = income * (1 - VAB_SHARE_ASSUMED)
        breakeven = FIXED_MONTHLY / contribution if contribution else float("inf")
        print(f"  {name:<9} доход {income:>6,} ₸/студия → contribution {contribution:>6,.0f} ₸"
              f" → break-even ~{breakeven:.1f} студий")
    print("  ⚠ V/A/B не оцифрованы — доля 40% сама есть допущение; pre-pilot её и проверяет.")

    print("\n" + "=" * 70)
    print("Число остаётся, но заякорено в self_canon (широкое) и подчинено статусу Ставки.")
    print("Сузить интервал = закрыть верхний рычаг реальным замером, не подкрутить приор.")
    print("=" * 70)


def print_configuration_comparison(comparison: dict[str, Any]) -> None:
    print("=" * 70)
    print("РАДИКАЛЬНАЯ РЕКОМЕНДАЦИЯ ИЗМЕНЕНИЯ КАНОНА — модельный прогон")
    print("=" * 70)
    print(f"Статус: {comparison['status']}")
    print(f"Основа ранжирования: Y_{comparison['basis_group']}")
    print(f"Из: {comparison['from_config_id']}")
    print(f"В:  {comparison['to_config_id']}")
    print(f"Рекомендовано моделью: {comparison['recommended_config_id']}")
    print(f"Замок честности: {comparison['honesty_lock']}")
    print(f"Owner gate: {comparison['owner_gate']}")

    print("\n[ИЗМЕНЕНИЯ РЕШЕНИЙ]")
    for change in comparison["changed_decisions"]:
        print(f"  {change['decision']}: {change['from']} -> {change['to']}")

    print("\n[ЧИСЛА]")
    for group in GROUPS:
        delta = comparison["group_deltas"][group]
        print(f"  Y_{group}: {pct(delta['from'])} -> {pct(delta['to'])} "
              f"(delta {delta['delta']:+.3f})")

    print("\n[КАКИЕ ЗВЕНЬЯ ИЗМЕНИЛИСЬ]")
    for change in comparison["changed_nodes"]:
        print(f"  {change['node_id']} {change['zveno']}: "
              f"active {change['from']['active']} -> {change['to']['active']}, "
              f"p_base {pct(change['from']['p_base'])} -> {pct(change['to']['p_base'])}")
        if change["to_reason"] and change["to_reason"] != "baseline":
            print(f"      почему: {change['to_reason']}")
        elif change["from_reason"] and change["from_reason"] != "baseline":
            print(f"      что устраняет: {change['from_reason']}")

    print("\n[DEFEATERS ДЛЯ НОВОГО НАПРАВЛЕНИЯ]")
    for defeater in comparison["defeaters"]:
        print(f"  - {defeater}")
    print("=" * 70)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit MAVO profit probability and decision configurations.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("FROM_CONFIG", "TO_CONFIG"),
        help="Compare two business configurations from configurations.json.",
    )
    parser.add_argument(
        "--basis-group",
        choices=GROUPS,
        default="pilot",
        help="Which Y_* group ranks the recommendation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nodes = load_nodes()

    if args.compare:
        configs = configurations_by_id(load_configurations())
        from_id, to_id = args.compare
        comparison = compare_configurations(nodes, configs[from_id], configs[to_id], args.basis_group)
        if args.json:
            print(json.dumps(comparison, ensure_ascii=False, indent=2))
        else:
            print_configuration_comparison(comparison)
        return

    result = score_nodes(nodes)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_forecast_report(nodes)


if __name__ == "__main__":
    main()
