# Arc Raiders Item Lookup

A CLI tool to quickly check if items in Arc Raiders are safe to sell, recycle, or need to be kept for quests, workshop upgrades, and expeditions.

![Python](https://img.shields.io/badge/python-3.8+-blue)

## Features

- **Instant search** with live autocomplete dropdown
- **Color-coded results** — SELL (green), RECYCLE (green), KEEP (red)
- **Fuzzy matching** — finds items even with typos
- **Expedition toggle** — filter out expedition items if you're not doing them
- **300+ items** catalogued with quantities needed and reasons (quests, all workshop levels, Scrappy, crafting)
- **Recycle hints** — shows what each item recycles into, and flags when selling pays more

## Install

```bash
pip install prompt_toolkit
```

## Usage

```bash
python arc_raiders_lookup.py
```

Start typing an item name and suggestions appear automatically. Use arrow keys to browse, Enter to select.

### Commands

| Command | Description |
|---------|-------------|
| `list` | Show all items |
| `list keep` | Items you must keep |
| `list sell` | Items safe to sell |
| `list recycle` | Items safe to recycle |
| `expeditions on/off` | Toggle expedition + project items (default: off) |
| `help` | Show help |
| `quit` | Exit |

### Expedition Toggle

If you're not doing expeditions, the tool defaults to **expeditions off**:
- Expedition/project-only items (Geiger Counter, ARC Performance Steel, etc.) show as RECYCLE
- Mixed items show reduced quantities (only what's needed for quests/workshop)

Type `expeditions on` to include the latest Expedition's requirements plus the permanent Trophy Display project.

> Expeditions are paused after Expedition 5 (ended Sept 2026) until early 2027, so "on" uses Expedition 5's list as a reference.

## Updating Item Data

Item data is generated from [RaidTheory/arcraiders-data](https://github.com/RaidTheory/arcraiders-data). After a game patch, refresh it with:

```bash
python update_items.py
```

This downloads the latest data and rewrites the `ITEMS` table in `arc_raiders_lookup.py`.

## Data Sources

Item data from [RaidTheory/arcraiders-data](https://github.com/RaidTheory/arcraiders-data) and [arctracker.io](https://arctracker.io) (MIT), cross-checked with the [ARC Raiders Wiki](https://arcraiders.wiki).
