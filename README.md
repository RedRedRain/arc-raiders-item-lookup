# Arc Raiders Item Lookup

A CLI tool to quickly check if items in Arc Raiders are safe to sell, recycle, or need to be kept for quests, workshop upgrades, and expeditions.

![Python](https://img.shields.io/badge/python-3.8+-blue)

## Features

- **Instant search** with live autocomplete dropdown
- **Color-coded results** — SELL (green), RECYCLE (green), KEEP (red)
- **Fuzzy matching** — finds items even with typos
- **Expedition toggle** — filter out expedition items if you're not doing them
- **150+ items** catalogued with quantities needed and reasons

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
| `expeditions on/off` | Toggle expedition items (default: off) |
| `help` | Show help |
| `quit` | Exit |

### Expedition Toggle

If you're not doing expeditions, the tool defaults to **expeditions off**:
- Expedition-only items (Cooling Fan, Sensors, Exodus Modules, etc.) show as RECYCLE
- Mixed items show reduced quantities (only what's needed for quests/workshop)

Type `expeditions on` to restore full quantities.

## Data Sources

Item data compiled from:
- [ARC Raiders Wiki](https://arcraiders.wiki)
- NeonLightsMedia
- AOEAH
- Skycoach
- TheGamer
- GameRant
