"""
Arc Raiders Item Lookup Tool
Quick search to check if items are safe to sell/recycle or needed for quests/workshop.
Data compiled from: ARC Raiders Wiki, NeonLightsMedia, AOEAH, Skycoach, TheGamer, GameRant.
"""

import difflib
import os

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

# ANSI color codes (for print output)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

SELL = "SELL"
RECYCLE = "RECYCLE"
KEEP = "KEEP"

# Expedition toggle - default OFF (user does not do expeditions)
expedition_mode = {"enabled": False}

# ================================================================
# ITEM DATABASE
# Sources: ARC Raiders Wiki (Workshop, Expedition, Quests, Loot pages),
#          NeonLightsMedia, AOEAH, Skycoach, TheGamer, GameRant
# ================================================================
ITEMS = {
    # ============================================================
    # SELL - Vendor trash / trinkets (sell for coins)
    # ============================================================
    "Agave":                      {"status": SELL, "reason": "Vendor trash"},
    "Air Freshener":              {"status": SELL, "reason": "Vendor trash"},
    "Alien Duck":                 {"status": SELL, "reason": "Trinket (collectible duck)"},
    "Bloated Tuna Can":           {"status": SELL, "reason": "Vendor trash"},
    "Blown Fuses":                {"status": SELL, "reason": "Vendor trash"},
    "Breathtaking Snow Globe":    {"status": SELL, "reason": "Vendor trash"},
    "Burnt-Out Candles":          {"status": SELL, "reason": "Vendor trash"},
    "Coffee Pot":                 {"status": SELL, "reason": "Vendor trash"},
    "Dart Board":                 {"status": SELL, "reason": "Vendor trash"},
    "Doodly Duck":                {"status": SELL, "reason": "Trinket (collectible duck)"},
    "Expired Pasta":              {"status": SELL, "reason": "Vendor trash"},
    "Faded Photograph":           {"status": SELL, "reason": "Vendor trash"},
    "Familiar Duck":              {"status": SELL, "reason": "Trinket (collectible duck)"},
    "Fine Wristwatch":            {"status": SELL, "reason": "Vendor trash"},
    "Flashy Duck":                {"status": SELL, "reason": "Trinket (collectible duck)"},
    "Fruit Mix":                  {"status": SELL, "reason": "Vendor trash"},
    "Gentle Duck":                {"status": SELL, "reason": "Trinket (collectible duck)"},
    "Lance's Mixtape (5th Edition)": {"status": SELL, "reason": "Vendor trash"},
    "Music Album":                {"status": SELL, "reason": "Vendor trash"},
    "Music Box":                  {"status": SELL, "reason": "Vendor trash"},
    "Painted Box":                {"status": SELL, "reason": "Vendor trash"},
    "Playing Cards":              {"status": SELL, "reason": "Vendor trash"},
    "Poster of Natural Wonders":  {"status": SELL, "reason": "Vendor trash"},
    "Pottery":                    {"status": SELL, "reason": "Vendor trash"},
    "Recorder":                   {"status": SELL, "reason": "Vendor trash"},
    "Red Coral Jewelry":          {"status": SELL, "reason": "Vendor trash"},
    "Resin":                      {"status": SELL, "reason": "Vendor trash"},
    "Roots":                      {"status": SELL, "reason": "Vendor trash"},
    "Rosary":                     {"status": SELL, "reason": "Vendor trash"},
    "Rubber Duck":                {"status": SELL, "reason": "Vendor trash"},
    "Silver Teaspoon Set":        {"status": SELL, "reason": "Vendor trash"},
    "Statuette":                  {"status": SELL, "reason": "Vendor trash"},
    "Torn Book":                  {"status": SELL, "reason": "Vendor trash"},
    "Vase":                       {"status": SELL, "reason": "Vendor trash"},
    "Volcanic Rock":              {"status": SELL, "reason": "Vendor trash"},

    # ============================================================
    # RECYCLE - No quest/workshop/expedition use
    # ============================================================
    # ARC damaged/degraded items
    "ARC Coolant":                {"status": RECYCLE, "reason": "No use (not the same as Coolant)"},
    "ARC Flex Rubber":            {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "ARC Performance Steel":      {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "ARC Synthetic Resin":        {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "ARC Thermo Lining":          {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Burned ARC Circuitry":       {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged ARC Motion Core":    {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged ARC Powercell":      {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Fireball Burner":    {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Hornet Driver":      {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Leaper Pulse Unit":  {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Rocketeer Driver":   {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Snitch Scanner":     {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Tick Pod":           {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Damaged Wasp Driver":        {"status": RECYCLE, "reason": "Damaged version - no use"},
    "Degraded ARC Rubber":        {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Dried-Out ARC Resin":        {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Impure ARC Coolant":         {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Rusty ARC Steel":            {"status": RECYCLE, "reason": "No use (sell may give more coins)"},
    "Tattered ARC Lining":        {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},

    # Electronics / tech
    "Alarm Clock":                {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Broken Flashlight":          {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Broken Guidance System":     {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Broken Handheld Radio":      {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Broken Taser":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Camera Lens":                {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Coolant":                    {"status": RECYCLE, "reason": "No use (sell may give more coins)"},
    "Headphones":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Industrial Charger":         {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Industrial Magnet":          {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Portable TV":                {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Power Bank":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Projector":                  {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Radio":                      {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Radio Relay":                {"status": RECYCLE, "reason": "No use (sell may give more coins)"},
    "Remote Control":             {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Rotary Encoder":             {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Sample Cleaner":             {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Signal Amplifier":           {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Spectrometer":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Spectrum Analyzer":          {"status": RECYCLE, "reason": "Recycles into Sensors + Exodus Modules"},
    "Telemetry Transceiver":      {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Thermostat":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},

    # Household / misc
    "Barricade Kit":              {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Bicycle Pump":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Binoculars":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Candle Holder":              {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Crumpled Plastic Bottle":    {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Deflated Football":          {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Diving Goggles":             {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Expired Respirator":         {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Flame Spray":                {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Fossilized Lightning":       {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Frying Pan":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Garlic Press":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Geiger Counter":             {"status": RECYCLE, "reason": "Recycles into 3x Battery + Exodus Modules"},
    "Household Cleaner":          {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ice Cream Scooper":          {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Metal Brackets":             {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Microscope":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Mini Centrifuge":            {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Moss":                       {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Number Plate":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Oil":                        {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Polluted Air Filter":        {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ripped Safety Vest":         {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Rocket Thruster":            {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Rope":                       {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Rubber Pad":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ruined Accordion":           {"status": RECYCLE, "reason": "Recycles into 18x Rubber Parts + 3x Steel Spring"},
    "Ruined Baton":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ruined Handcuffs":           {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ruined Parachute":           {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ruined Riot Shield":         {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Ruined Tactical Vest":       {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Rusted Bolts":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Spotter Relay":              {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Spring Cushion":             {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Tattered Clothes":           {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Torn Blanket":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Turbo Pump":                 {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Unusable Weapon":            {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Water Filter":               {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},
    "Zipline":                    {"status": RECYCLE, "reason": "No quest/workshop/expedition use"},

    # ============================================================
    # KEEP - Quest items
    # ============================================================
    "Magnetron":                  {"status": KEEP, "reason": "Quest: Snap And Salvage", "qty": 1},
    "Power Rod":                  {"status": KEEP, "reason": "Quest: Tribute To Toledo", "qty": 1},
    "Rocketeer Driver":           {"status": KEEP, "reason": "Quest: Out Of The Shadows + Workshop: Explosives x3", "qty": 4},
    "Syringe":                    {"status": KEEP, "reason": "Quest: Doctor's Orders", "qty": 1},
    "Great Mullein":              {"status": KEEP, "reason": "Quest: Doctor's Orders", "qty": 1},
    "Empty Wine Bottle":          {"status": KEEP, "reason": "Quest item", "qty": 1},
    "Film Reel":                  {"status": KEEP, "reason": "Quest: A Dead End", "qty": 1},
    "Agave Juice":                {"status": KEEP, "reason": "Quest item", "qty": 1},
    "Candleberries":              {"status": KEEP, "reason": "Quest item", "qty": 1},

    # ============================================================
    # KEEP - Workshop: Gunsmith (Lv2 + Lv3)
    # ============================================================
    "Mechanical Components":      {"status": KEEP, "reason": "Workshop: Gunsmith Lv2 x5", "qty": 5},
    "Rusted Tools":               {"status": KEEP, "reason": "Workshop: Gunsmith Lv2 x3", "qty": 3},
    "Wasp Driver":                {"status": KEEP, "reason": "Quest: The Trifecta x2 + Workshop: Gunsmith Lv2 x8", "qty": 10},
    "Rusted Gear":                {"status": KEEP, "reason": "Workshop: Gunsmith Lv3 x3", "qty": 3},
    "Advanced Mechanical Components": {"status": KEEP, "reason": "Workshop: Gunsmith Lv3 x5", "qty": 5},
    "Sentinel Firing Core":       {"status": KEEP, "reason": "Workshop: Gunsmith Lv3 x4", "qty": 4},

    # ============================================================
    # KEEP - Workshop: Explosives Station (Lv2 + Lv3)
    # ============================================================
    "Pop Trigger":                {"status": KEEP, "reason": "Workshop: Explosives Lv2 x5", "qty": 5},
    "Crude Explosives":           {"status": KEEP, "reason": "Workshop: Explosives Lv2 x5", "qty": 5},
    "Synthesised Fuel":           {"status": KEEP, "reason": "Workshop: Explosives Lv2 x3", "qty": 3},
    "Laboratory Reagents":        {"status": KEEP, "reason": "Workshop: Explosives Lv3 x3", "qty": 3},
    "Explosive Compound":         {"status": KEEP, "reason": "Workshop: Explosives Lv3 x5", "qty": 5},

    # ============================================================
    # KEEP - Workshop: Gear Bench (Lv2 + Lv3)
    # ============================================================
    "Power Cable":                {"status": KEEP, "reason": "Workshop: Gear Bench Lv2 x3", "qty": 3},
    "Hornet Driver":              {"status": KEEP, "reason": "Quest: The Trifecta x2 + Workshop: Gear Bench Lv2 x5", "qty": 7},
    "Industrial Battery":         {"status": KEEP, "reason": "Workshop: Gear Bench Lv3 x3", "qty": 3},
    "Bastion Cell":               {"status": KEEP, "reason": "Workshop: Gear Bench Lv3 x6", "qty": 6},

    # ============================================================
    # KEEP - Workshop: Refiner (Lv2 + Lv3)
    # ============================================================
    "Fireball Burner":            {"status": KEEP, "reason": "Workshop: Refiner Lv2 x8", "qty": 8},
    "ARC Motion Core":            {"status": KEEP, "reason": "Workshop: Refiner Lv2 x5", "qty": 5},
    "Toaster":                    {"status": KEEP, "reason": "Workshop: Refiner Lv2 x3", "qty": 3},
    "Motor":                      {"status": KEEP, "reason": "Workshop: Refiner Lv3 x3", "qty": 3},
    "ARC Circuitry":              {"status": KEEP, "reason": "Workshop: Refiner Lv3 x10", "qty": 10},
    "Bombardier Cell":            {"status": KEEP, "reason": "Workshop: Refiner Lv3 x6", "qty": 6},

    # ============================================================
    # KEEP - Workshop: Medical Lab (Lv2 + Lv3)
    # ============================================================
    "Tick Pod":                   {"status": KEEP, "reason": "Workshop: Medical Lab Lv2 x8", "qty": 8},
    "Cracked Bioscanner":         {"status": KEEP, "reason": "Workshop: Medical Lab Lv2 x2", "qty": 2},
    "Durable Cloth":              {"status": KEEP, "reason": "Workshop: Medical Lab Lv2 x5 + Expedition 1 x35 + Expedition 2 x35", "qty": 75, "expedition": {"only": False, "no_exp_reason": "Workshop: Medical Lab Lv2 x5", "no_exp_qty": 5}},
    "Rusted Shut Medical Kit":    {"status": KEEP, "reason": "Workshop: Medical Lab Lv3 x3", "qty": 3},
    "Antiseptic":                 {"status": KEEP, "reason": "Quest: Doctor's Orders x2 + Workshop: Medical Lab Lv3 x8", "qty": 10},
    "Surveyor Vault":             {"status": KEEP, "reason": "Quest: Mixed Signals + Workshop: Medical Lab Lv3 x5", "qty": 6},

    # ============================================================
    # KEEP - Workshop: Utility Station (Lv2 + Lv3)
    # ============================================================
    "Snitch Scanner":             {"status": KEEP, "reason": "Quest: The Trifecta x2 + Workshop: Utility Lv2 x6", "qty": 8},
    "Damaged Heat Sink":          {"status": KEEP, "reason": "Workshop: Utility Lv2 x2", "qty": 2},
    "Fried Motherboard":          {"status": KEEP, "reason": "Workshop: Utility Lv3 x3", "qty": 3},
    "Leaper Pulse Unit":          {"status": KEEP, "reason": "Quest: Into The Fray + Workshop: Utility Lv3 x4 + Expedition x3+3", "qty": 11, "expedition": {"only": False, "no_exp_reason": "Quest: Into The Fray + Workshop: Utility Lv3 x4", "no_exp_qty": 5}},

    # ============================================================
    # KEEP - Workshop: Scrappy (dog upgrades)
    # ============================================================
    "Dog Collar":                 {"status": KEEP, "reason": "Scrappy (dog) upgrades x8", "qty": 8},
    "Lemon":                      {"status": KEEP, "reason": "Scrappy (dog) upgrades x3", "qty": 3},
    "Apricot":                    {"status": KEEP, "reason": "Scrappy (dog) upgrades x15", "qty": 15},
    "Prickly Pear":               {"status": KEEP, "reason": "Scrappy (dog) upgrades x3", "qty": 3},
    "Olives":                     {"status": KEEP, "reason": "Scrappy (dog) upgrades x6", "qty": 6},
    "Cat Bed":                    {"status": KEEP, "reason": "Scrappy (dog) upgrades x1", "qty": 1},
    "Mushroom":                   {"status": KEEP, "reason": "Scrappy (dog) upgrades x12", "qty": 12},
    "Very Comfortable Pillow":    {"status": KEEP, "reason": "Scrappy (dog) upgrades x3", "qty": 3},

    # ============================================================
    # KEEP - Expedition 1 items
    # ============================================================
    "Metal Parts":                {"status": KEEP, "reason": "Expedition 1+2 x150+150 + crafting", "qty": 300, "expedition": {"only": False, "no_exp_reason": "Crafting material", "no_exp_qty": 0}},
    "Rubber Parts":               {"status": KEEP, "reason": "Expedition 1 x200 + crafting", "qty": 200, "expedition": {"only": False, "no_exp_reason": "Crafting material", "no_exp_qty": 0}},
    "ARC Alloy":                  {"status": KEEP, "reason": "Quest x3 + Workshop Lv1 x18 + Expedition 1+2 x80+80", "qty": 181, "expedition": {"only": False, "no_exp_reason": "Quest x3 + Workshop Lv1 x18", "no_exp_qty": 21}},
    "Steel Spring":               {"status": KEEP, "reason": "Expedition 1+2 x15+15 + crafting", "qty": 30, "expedition": {"only": False, "no_exp_reason": "Crafting material", "no_exp_qty": 0}},
    "Wires":                      {"status": KEEP, "reason": "Quest x14 + Expedition 1+2 x30+25", "qty": 69, "expedition": {"only": False, "no_exp_reason": "Quest x14", "no_exp_qty": 14}},
    "Electrical Components":      {"status": KEEP, "reason": "Workshop: Gear Bench x5 + Utility x5 + Expedition 1+2 x30+20", "qty": 60, "expedition": {"only": False, "no_exp_reason": "Workshop: Gear Bench x5 + Utility x5", "no_exp_qty": 10}},
    "Cooling Fan":                {"status": KEEP, "reason": "Expedition 1 x5", "qty": 5, "expedition": {"only": True}},
    "Light Bulb":                 {"status": KEEP, "reason": "Expedition 1+2 x5+4", "qty": 9, "expedition": {"only": True}},
    "Battery":                    {"status": KEEP, "reason": "Quest x3 + Expedition 1+2 x30+30", "qty": 63, "expedition": {"only": False, "no_exp_reason": "Quest x3", "no_exp_qty": 3}},
    "Sensors":                    {"status": KEEP, "reason": "Expedition 1 x20", "qty": 20, "expedition": {"only": True}},
    "Exodus Modules":             {"status": KEEP, "reason": "Expedition 1+2 x1+1", "qty": 2, "expedition": {"only": True}},
    "Humidifier":                 {"status": KEEP, "reason": "Expedition 1 x5", "qty": 5, "expedition": {"only": True}},
    "Advanced Electrical Components": {"status": KEEP, "reason": "Workshop: Gear Bench x5 + Utility x5 + Expedition 1+2 x5+5", "qty": 20, "expedition": {"only": False, "no_exp_reason": "Workshop: Gear Bench x5 + Utility x5", "no_exp_qty": 10}},
    "Magnetic Accelerator":       {"status": KEEP, "reason": "Expedition 1 x3", "qty": 3, "expedition": {"only": True}},

    # ============================================================
    # KEEP - Expedition 2 specific items
    # ============================================================
    "Plastic Parts":              {"status": KEEP, "reason": "Expedition 2 x200 + Workshop Lv1 + crafting", "qty": 200, "expedition": {"only": False, "no_exp_reason": "Workshop Lv1 + crafting", "no_exp_qty": 0}},
    "Cooling Coil":               {"status": KEEP, "reason": "Expedition 2 x4", "qty": 4, "expedition": {"only": True}},
    "Shredder Gyro":              {"status": KEEP, "reason": "Expedition 2 x10", "qty": 10, "expedition": {"only": True}},
    "Ion Sputter":                {"status": KEEP, "reason": "Expedition 2 x3", "qty": 3, "expedition": {"only": True}},
    "Frequency Modulation Box":   {"status": KEEP, "reason": "Expedition 2 x5", "qty": 5, "expedition": {"only": True}},

    # ============================================================
    # KEEP - Crafting materials (topside materials / base materials)
    # ============================================================
    "Voltage Converter":          {"status": KEEP, "reason": "Crafts Heavy Shield + Showstopper grenade", "qty": 0},
    "ARC Powercell":              {"status": KEEP, "reason": "Workshop: Refiner Lv1 x5 + crafting", "qty": 5},
    "Advanced ARC Powercell":     {"status": KEEP, "reason": "Rare crafting material", "qty": 0},
    "Chemicals":                  {"status": KEEP, "reason": "Workshop: Explosives Lv1 x50 + crafting", "qty": 50},
    "Fabric":                     {"status": KEEP, "reason": "Workshop: Gear Bench Lv1 x30 + Medical Lv1 x50 + crafting", "qty": 80},
    "Complex Gun Parts":          {"status": KEEP, "reason": "Weapon crafting material", "qty": 0},
    "Simple Gun Parts":           {"status": KEEP, "reason": "Weapon crafting material", "qty": 0},
    "Medium Gun Parts":           {"status": KEEP, "reason": "Weapon crafting material", "qty": 0},
    "Heavy Gun Parts":            {"status": KEEP, "reason": "Weapon crafting material", "qty": 0},
    "Light Gun Parts":            {"status": KEEP, "reason": "Weapon crafting material", "qty": 0},
    "Duct Tape":                  {"status": KEEP, "reason": "Topside crafting material", "qty": 0},
    "Magnet":                     {"status": KEEP, "reason": "Topside crafting material", "qty": 0},
    "Canister":                   {"status": KEEP, "reason": "Topside crafting material", "qty": 0},
    "Processor":                  {"status": KEEP, "reason": "Topside crafting material", "qty": 0},
    "Speaker Component":          {"status": KEEP, "reason": "Topside crafting material", "qty": 0},
    "Mod Components":             {"status": KEEP, "reason": "Weapon mod crafting material", "qty": 0},
    "Assorted Seeds":             {"status": KEEP, "reason": "Basic material (Scrappy brings these)", "qty": 0},
    "Matriarch Reactor":          {"status": KEEP, "reason": "Rare boss drop - crafting", "qty": 0},
    "Queen Reactor":              {"status": KEEP, "reason": "Rare boss drop - crafting", "qty": 0},
    "Water Pump":                 {"status": KEEP, "reason": "Quest item", "qty": 1},
    "Fertilizer":                 {"status": KEEP, "reason": "Quest item", "qty": 1},
}


def get_effective_item(data):
    """Return (status, reason, qty) adjusted for expedition toggle."""
    if expedition_mode["enabled"] or "expedition" not in data:
        return data["status"], data["reason"], data.get("qty", 0)
    exp = data["expedition"]
    if exp["only"]:
        return RECYCLE, "Expedition-only item (expeditions off)", 0
    return KEEP, exp["no_exp_reason"], exp["no_exp_qty"]


class ItemCompleter(Completer):
    """Live autocomplete dropdown showing items + status as you type."""

    def __init__(self):
        self.commands = ["list", "list keep", "list sell", "list recycle",
                         "expeditions on", "expeditions off", "exp on", "exp off",
                         "help", "quit"]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower().strip()
        if not text:
            return

        # Match commands
        for cmd in self.commands:
            if cmd.startswith(text):
                yield Completion(cmd, start_position=-len(document.text_before_cursor),
                                 display=HTML(f"<b>{cmd}</b>"),
                                 display_meta="command")

        # Match item names (substring anywhere)
        for name, data in sorted(ITEMS.items()):
            if text in name.lower():
                yield Completion(name, start_position=-len(document.text_before_cursor),
                                 display=HTML(f"<b>{name}</b>"),
                                 display_meta=_meta_html(data))

        # Fuzzy fallback if no substring matches
        if not any(text in name.lower() for name in ITEMS):
            close = difflib.get_close_matches(text, [n.lower() for n in ITEMS], n=5, cutoff=0.5)
            seen = set()
            for match_lower in close:
                for name, data in ITEMS.items():
                    if name.lower() == match_lower and name not in seen:
                        seen.add(name)
                        yield Completion(name, start_position=-len(document.text_before_cursor),
                                         display=HTML(f"<b>{name}</b> <i>(fuzzy)</i>"),
                                         display_meta=_meta_html(data))


def _meta_html(data):
    """Format the status badge for the autocomplete dropdown."""
    status, reason, qty = get_effective_item(data)
    qty_str = f" (need {qty})" if qty else ""
    if status == KEEP:
        return HTML(f'<style bg="ansired" fg="ansiwhite"> KEEP </style> {reason}{qty_str}')
    elif status == SELL:
        return HTML(f'<style bg="ansigreen" fg="ansiwhite"> SELL </style> {reason}')
    else:
        return HTML(f'<style bg="ansigreen" fg="ansiwhite"> RECYCLE </style> {reason}')


DROPDOWN_STYLE = Style.from_dict({
    "completion-menu":                "bg:#1a1a2e #e0e0e0",
    "completion-menu.completion":     "bg:#1a1a2e #e0e0e0",
    "completion-menu.completion.current": "bg:#16213e #ffffff bold",
    "completion-menu.meta":           "bg:#0f3460 #e0e0e0",
    "completion-menu.meta.current":   "bg:#533483 #ffffff",
    "scrollbar.background":           "bg:#1a1a2e",
    "scrollbar.button":               "bg:#533483",
})


def search_item(query):
    """Search for an item by name."""
    query_lower = query.lower().strip()

    # Exact match
    for name, data in ITEMS.items():
        if name.lower() == query_lower:
            return [(name, data)]

    # Substring match
    matches = [(n, d) for n, d in ITEMS.items() if query_lower in n.lower()]
    if matches:
        return matches

    # Fuzzy match (higher cutoff to avoid garbage)
    close = difflib.get_close_matches(query, list(ITEMS.keys()), n=5, cutoff=0.5)
    if close:
        return [(name, ITEMS[name]) for name in close]

    return []


def format_result(name, data):
    """Format a single item result with colors."""
    status, reason, qty = get_effective_item(data)

    if status == SELL:
        icon = f"{GREEN}{BOLD}  SELL{RESET}"
        detail = f"{GREEN}{reason}{RESET}"
    elif status == RECYCLE:
        icon = f"{GREEN}{BOLD}  RECYCLE{RESET}"
        detail = f"{GREEN}{reason}{RESET}"
    else:
        icon = f"{RED}{BOLD}  KEEP - DO NOT SELL/RECYCLE{RESET}"
        detail = f"{RED}{reason}{RESET}"

    lines = [f"  {BOLD}{name}{RESET} {icon}"]
    lines.append(f"  Reason: {detail}")
    if qty and status == KEEP:
        lines.append(f"  {DIM}Total needed: {qty}{RESET}")
    return "\n".join(lines)


def list_items(filter_status=None):
    """List all items, optionally filtered by status."""
    items = sorted(ITEMS.items(), key=lambda x: x[0])
    if filter_status:
        items = [(n, d) for n, d in items if get_effective_item(d)[0] == filter_status]

    if not items:
        print(f"  {YELLOW}No items found.{RESET}")
        return

    if not filter_status:
        for status, label, color in [(KEEP, "KEEP", RED), (SELL, "SELL", GREEN), (RECYCLE, "RECYCLE", GREEN)]:
            group = [(n, d) for n, d in items if get_effective_item(d)[0] == status]
            if group:
                print(f"\n  {color}{BOLD}--- {label} ({len(group)} items) ---{RESET}")
                for name, data in group:
                    _, _, qty = get_effective_item(data)
                    qty_str = f" (need {qty})" if qty else ""
                    print(f"  {color}  {name}{RESET}{DIM}{qty_str}{RESET}")
    else:
        color = RED if filter_status == KEEP else GREEN
        print(f"\n  {color}{BOLD}--- {filter_status} ({len(items)} items) ---{RESET}")
        for name, data in items:
            _, reason, qty = get_effective_item(data)
            qty_str = f" (need {qty})" if qty else ""
            print(f"  {color}  {name}{RESET} - {DIM}{reason}{qty_str}{RESET}")


def print_help():
    print(f"""
  {BOLD}Arc Raiders Item Lookup{RESET}
  {DIM}Data from ARC Raiders Wiki + community guides{RESET}

  {CYAN}How to use:{RESET}
    Start typing - suggestions appear automatically
    Use {BOLD}Up/Down arrows{RESET} to browse suggestions
    Press {BOLD}Enter{RESET} to select/search
    Dropdown shows {GREEN}SELL{RESET}/{GREEN}RECYCLE{RESET}/{RED}KEEP{RESET} right in suggestions

  {CYAN}Commands:{RESET}
    {BOLD}list{RESET}           Show all items
    {BOLD}list keep{RESET}      Items you must KEEP
    {BOLD}list sell{RESET}      Items safe to SELL
    {BOLD}list recycle{RESET}   Items safe to RECYCLE
    {BOLD}expeditions on/off{RESET}  Toggle expedition items (currently {"ON" if expedition_mode["enabled"] else "OFF"})
    {BOLD}help{RESET}           Show this help
    {BOLD}quit{RESET}           Exit

  {DIM}Item not listed? It's probably safe to recycle,
  but check the wiki first: arcraiders.wiki{RESET}
""")


def print_status_counts():
    """Print item counts and expedition mode status."""
    total = len(ITEMS)
    keep = sum(1 for d in ITEMS.values() if get_effective_item(d)[0] == KEEP)
    sell = sum(1 for d in ITEMS.values() if get_effective_item(d)[0] == SELL)
    recycle = sum(1 for d in ITEMS.values() if get_effective_item(d)[0] == RECYCLE)
    exp_state = f"{GREEN}ON{RESET}" if expedition_mode["enabled"] else f"{YELLOW}OFF{RESET}"
    print(f"  {DIM}Database: {total} items ({keep} keep, {sell} sell, {recycle} recycle){RESET}")
    print(f"  {DIM}Expeditions: {exp_state}{DIM} (type 'expeditions on/off' to toggle){RESET}\n")


def main():
    if os.name == "nt":
        os.system("")

    print_help()
    print_status_counts()

    completer = ItemCompleter()

    while True:
        try:
            query = prompt("  > ", completer=completer, style=DROPDOWN_STYLE,
                           complete_while_typing=True).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            break
        if query.lower() == "help":
            print_help()
            continue
        if query.lower() == "list":
            list_items()
            print()
            continue
        if query.lower() == "list keep":
            list_items(KEEP)
            print()
            continue
        if query.lower() == "list sell":
            list_items(SELL)
            print()
            continue
        if query.lower() == "list recycle":
            list_items(RECYCLE)
            print()
            continue
        if query.lower() in ("expeditions on", "exp on"):
            expedition_mode["enabled"] = True
            print(f"  {CYAN}Expeditions ON - showing full quantities including expedition items{RESET}")
            print_status_counts()
            continue
        if query.lower() in ("expeditions off", "exp off"):
            expedition_mode["enabled"] = False
            print(f"  {CYAN}Expeditions OFF - expedition-only items marked RECYCLE, quantities reduced{RESET}")
            print_status_counts()
            continue

        results = search_item(query)
        if not results:
            print(f"  {YELLOW}'{query}' not in database.{RESET}")
            print(f"  {DIM}If it's a crafting/topside material, keep it to be safe.{RESET}")
            print(f"  {DIM}Check: arcraiders.wiki/wiki/{query.replace(' ', '_')}{RESET}\n")
            continue

        if len(results) == 1:
            print(format_result(results[0][0], results[0][1]))
        else:
            print(f"  {DIM}Found {len(results)} matches:{RESET}")
            for name, data in results:
                print(format_result(name, data))
                print()
        print()


if __name__ == "__main__":
    main()
