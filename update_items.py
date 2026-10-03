"""
Regenerate the ITEMS database in arc_raiders_lookup.py from the community
ARC Raiders data repo (https://github.com/RaidTheory/arcraiders-data).

Usage:
    python update_items.py                  # downloads the latest data
    python update_items.py path/to/arcraiders-data   # use a local clone
"""

import glob
import io
import json
import os
import re
import sys
import tarfile
import tempfile
import urllib.request
from collections import defaultdict

DATA_URL = "https://github.com/RaidTheory/arcraiders-data/archive/refs/heads/main.tar.gz"
TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arc_raiders_lookup.py")
BEGIN = "# BEGIN GENERATED ITEMS"
END = "# END GENERATED ITEMS"

# Item types worth looking up (weapons, blueprints, keys, mods etc. are skipped
# unless something requires them)
LOOT_TYPES = {"Recyclable", "Trinket", "Topside Material", "Nature",
              "Refined Material", "Basic Material", "Misc", "Quick Use"}
MATERIAL_TYPES = {"Topside Material", "Refined Material", "Basic Material"}
# Projects that run permanently alongside expeditions
PERMANENT_PROJECTS = {"trophy_display_project"}


def download_data():
    print("Downloading latest arcraiders-data...")
    with urllib.request.urlopen(DATA_URL) as resp:
        data = resp.read()
    tmp = tempfile.mkdtemp()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        tar.extractall(tmp)
    return os.path.join(tmp, os.listdir(tmp)[0])


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def en(name):
    return name["en"] if isinstance(name, dict) else name


def build(data_dir):
    items = {}
    for path in glob.glob(os.path.join(data_dir, "items", "*.json")):
        item = load_json(path)
        items[item["id"]] = item

    def name_of(item_id):
        return en(items[item_id]["name"]) if item_id in items else item_id.replace("_", " ").title()

    # base[id] = [(label, qty)] - quests, workshop, Scrappy
    # proj[id] = [(label, qty)] - latest expedition + permanent projects
    base = defaultdict(list)
    proj = defaultdict(list)

    for path in sorted(glob.glob(os.path.join(data_dir, "quests", "*.json"))):
        quest = load_json(path)
        for req in quest.get("requiredItemIds", []):
            base[req["itemId"]].append((f"Quest: {en(quest['name'])}", req["quantity"]))

    for path in sorted(glob.glob(os.path.join(data_dir, "hideout", "*.json"))):
        station = load_json(path)
        label = en(station["name"])
        for level in station.get("levels", []):
            for req in level.get("requirementItemIds", []):
                if label == "Scrappy":
                    base[req["itemId"]].append(("Scrappy (dog) upgrades", req["quantity"]))
                else:
                    base[req["itemId"]].append((f"Workshop: {label} Lv{level['level']}", req["quantity"]))

    projects = load_json(os.path.join(data_dir, "projects.json"))
    expeditions = [p for p in projects if p["id"].startswith("expedition_project") and not p.get("disabled")]
    latest = max(expeditions, key=lambda p: p.get("startDate") or 0)
    exp_label = re.sub(r".*\((.*)\).*", r"\1", en(latest["name"])).replace("Season", "Expedition")
    for p in [latest] + [p for p in projects if p["id"] in PERMANENT_PROJECTS]:
        label = exp_label if p is latest else f"Project: {en(p['name'])}"
        for phase in p.get("phases", []):
            for req in phase.get("requirementItemIds", []):
                proj[req["itemId"]].append((label, req["quantity"]))

    # Which recipes each item is an ingredient in
    used_in = defaultdict(list)
    for item in items.values():
        for ingredient in (item.get("recipe") or {}):
            used_in[ingredient].append(en(item["name"]))

    def merge(reqs):
        """Combine requirements with the same label, summing quantities."""
        totals = {}
        for label, qty in reqs:
            totals[label] = totals.get(label, 0) + qty
        return totals

    def describe(reqs):
        totals = merge(reqs)
        return " + ".join(f"{label} x{qty}" for label, qty in totals.items()), sum(totals.values())

    def crafting_reason(item_id):
        recipes = sorted(set(used_in[item_id]))
        if len(recipes) <= 2:
            return "Crafting: " + ", ".join(recipes)
        return f"Crafting material ({len(recipes)} recipes)"

    def recycle_reason(item):
        parts = item.get("recyclesInto") or {}
        reason = "Recycles into " + ", ".join(f"{q}x {name_of(i)}" for i, q in parts.items())
        sell_value = item.get("value", 0)
        recycle_value = sum(items[i].get("value", 0) * q for i, q in parts.items() if i in items)
        if sell_value > recycle_value:
            reason += f" (selling pays more: {sell_value:,} vs {recycle_value:,} coins)"
        return reason

    wanted = {i for i, item in items.items() if item["type"] in LOOT_TYPES}
    wanted |= {i for i in list(base) + list(proj) if i in items and i != "coins"}

    entries = {"SELL": [], "RECYCLE": [], "KEEP": []}
    for item_id in wanted:
        item = items[item_id]
        name = en(item["name"])
        crafted = bool(used_in[item_id])
        if base[item_id] or proj[item_id]:
            all_reason, all_qty = describe(base[item_id] + proj[item_id])
            if crafted:
                all_reason += " + crafting"
            entry = {"status": "KEEP", "reason": all_reason, "qty": all_qty}
            if proj[item_id]:
                if base[item_id]:
                    no_reason, no_qty = describe(base[item_id])
                    if crafted:
                        no_reason += " + crafting"
                    entry["expedition"] = {"only": False, "no_exp_reason": no_reason, "no_exp_qty": no_qty}
                elif crafted:
                    entry["expedition"] = {"only": False, "no_exp_reason": crafting_reason(item_id), "no_exp_qty": 0}
                else:
                    entry["expedition"] = {"only": True}
            entries["KEEP"].append((name, entry))
        elif crafted:
            entries["KEEP"].append((name, {"status": "KEEP", "reason": crafting_reason(item_id), "qty": 0}))
        elif item["type"] == "Trinket" or not item.get("recyclesInto"):
            reason = f"Sells for {item.get('value', 0):,} coins"
            if item["type"] == "Quick Use":
                reason = f"Consumable - use it, or sell for {item.get('value', 0):,} coins"
            entries["SELL"].append((name, {"status": "SELL", "reason": reason}))
        else:
            reason = recycle_reason(item)
            if item["type"] == "Quick Use":
                reason = "Consumable - use it, or r" + reason[1:]
            entries["RECYCLE"].append((name, {"status": "RECYCLE", "reason": reason}))

    return entries, exp_label


def render(entries, exp_label):
    lines = [
        BEGIN + " - run update_items.py to refresh",
        "# Source: https://github.com/RaidTheory/arcraiders-data (arctracker.io)",
        f"# Expedition data: {exp_label} (latest) + permanent projects",
        "ITEMS = {",
    ]
    headers = {
        "SELL": "SELL - Trinkets / vendor trash",
        "RECYCLE": "RECYCLE - No quest/workshop/crafting use",
        "KEEP": "KEEP - Quests, workshop, Scrappy, crafting, expeditions/projects",
    }
    for status in ("SELL", "RECYCLE", "KEEP"):
        lines.append("    # " + "=" * 60)
        lines.append(f"    # {headers[status]}")
        lines.append("    # " + "=" * 60)
        for name, entry in sorted(entries[status]):
            fields = [f'"status": {status}', f'"reason": {json.dumps(entry["reason"], ensure_ascii=False)}']
            if "qty" in entry:
                fields.append(f'"qty": {entry["qty"]}')
            if "expedition" in entry:
                fields.append(f'"expedition": {json.dumps(entry["expedition"], ensure_ascii=False).replace("false", "False").replace("true", "True")}')
            key = json.dumps(name, ensure_ascii=False) + ":"
            lines.append(f"    {key:<34}{{{', '.join(fields)}}},")
        lines.append("")
    lines[-1] = "}"
    lines.append(END)
    return "\n".join(lines)


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else download_data()
    entries, exp_label = build(data_dir)
    with open(TARGET, encoding="utf-8") as f:
        source = f.read()
    start, end = source.index(BEGIN), source.index(END) + len(END)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(source[:start] + render(entries, exp_label) + source[end:])
    counts = {k: len(v) for k, v in entries.items()}
    print(f"Updated {TARGET}: {sum(counts.values())} items "
          f"({counts['KEEP']} keep, {counts['SELL']} sell, {counts['RECYCLE']} recycle)")


if __name__ == "__main__":
    main()
