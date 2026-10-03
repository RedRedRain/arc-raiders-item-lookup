"""
Arc Raiders Item Lookup Tool
Quick search to check if items are safe to sell/recycle or needed for quests/workshop.
Item data from RaidTheory/arcraiders-data (arctracker.io) - refresh with update_items.py.
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

# Expedition/project toggle - default OFF (user does not do expeditions)
expedition_mode = {"enabled": False}

# BEGIN GENERATED ITEMS - run update_items.py to refresh
# Source: https://github.com/RaidTheory/arcraiders-data (arctracker.io)
# Expedition data: Expedition 5 (latest) + permanent projects
ITEMS = {
    # ============================================================
    # SELL - Trinkets / vendor trash
    # ============================================================
    "\"Leviathan's Crown\" Ship Model":{"status": SELL, "reason": "Sells for 10,000 coins"},
    "\"Sirena Dorata\" Ship Model":   {"status": SELL, "reason": "Sells for 7,000 coins"},
    "\"Twilight Compass\" Ship Model":{"status": SELL, "reason": "Sells for 1,000 coins"},
    "\"Velocity\" Ship Model":        {"status": SELL, "reason": "Sells for 3,000 coins"},
    "\"Wind Sprite\" Ship Model":     {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Agave Juice":                    {"status": SELL, "reason": "Consumable - use it, or sell for 1,800 coins"},
    "Alien Duck":                     {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Blaze Grenade Trap":             {"status": SELL, "reason": "Consumable - use it, or sell for 1,000 coins"},
    "Bloated Tuna Can":               {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Breathtaking Snow Globe":        {"status": SELL, "reason": "Sells for 7,000 coins"},
    "Burnt-Out Candles":              {"status": SELL, "reason": "Sells for 640 coins"},
    "Coffee Pot":                     {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Colorful Shoes (Green)":         {"status": SELL, "reason": "Sells for 7,000 coins"},
    "Colorful Shoes (Red)":           {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Colorful Shoes (Silver)":        {"status": SELL, "reason": "Sells for 10,000 coins"},
    "Damaged Snitch Scanner":         {"status": SELL, "reason": "Sells for 659 coins"},
    "Dart Board":                     {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Dockmaster's Detector":          {"status": SELL, "reason": "Consumable - use it, or sell for 1,000 coins"},
    "Doodly Duck":                    {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Elephant Obelisk":               {"status": SELL, "reason": "Sells for 10,000 coins"},
    "Equatorial Sundial":             {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Expired Pasta":                  {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Faded Photograph":               {"status": SELL, "reason": "Sells for 640 coins"},
    "Familiar Duck":                  {"status": SELL, "reason": "Sells for 7,000 coins"},
    "Film Reel":                      {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Fine Wristwatch":                {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Flashy Duck":                    {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Flushing Terminal Key":          {"status": SELL, "reason": "Sells for 100 coins"},
    "Fruit Mix":                      {"status": SELL, "reason": "Consumable - use it, or sell for 1,800 coins"},
    "Gas Grenade Trap":               {"status": SELL, "reason": "Consumable - use it, or sell for 300 coins"},
    "Gentle Duck":                    {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Light Bulb":                     {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Lure Grenade Trap":              {"status": SELL, "reason": "Consumable - use it, or sell for 1,000 coins"},
    "Marano Market Business Card":    {"status": SELL, "reason": "Sells for 100 coins"},
    "Music Album":                    {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Music Box":                      {"status": SELL, "reason": "Sells for 5,000 coins"},
    "Painted Box":                    {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Playing Cards":                  {"status": SELL, "reason": "Sells for 5,000 coins"},
    "Poster of Natural Wonders":      {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Pottery":                        {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Raider Flag":                    {"status": SELL, "reason": "Sells for 100 coins"},
    "Red Coral Jewelry":              {"status": SELL, "reason": "Sells for 5,000 coins"},
    "Resin":                          {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Rosary":                         {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Rubber Duck":                    {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Sextant":                        {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Silver Teaspoon Set":            {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Smoke Grenade Trap":             {"status": SELL, "reason": "Consumable - use it, or sell for 640 coins"},
    "Snowball":                       {"status": SELL, "reason": "Consumable - use it, or sell for 10 coins"},
    "Statuette":                      {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Tellurion":                      {"status": SELL, "reason": "Sells for 7,000 coins"},
    "Torn Book":                      {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Train Model":                    {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Tropical Duck":                  {"status": SELL, "reason": "Sells for 1,000 coins"},
    "Vase":                           {"status": SELL, "reason": "Sells for 3,000 coins"},
    "Vintage Steering Wheel":         {"status": SELL, "reason": "Sells for 2,000 coins"},
    "Volcanic Rock":                  {"status": SELL, "reason": "Sells for 270 coins"},

    # ============================================================
    # RECYCLE - No quest/workshop/crafting use
    # ============================================================
    "ARC Coolant":                    {"status": RECYCLE, "reason": "Recycles into 16x Chemicals (selling pays more: 1,000 vs 800 coins)"},
    "ARC Flex Rubber":                {"status": RECYCLE, "reason": "Recycles into 16x Rubber Parts (selling pays more: 1,000 vs 800 coins)"},
    "ARC Thermo Lining":              {"status": RECYCLE, "reason": "Recycles into 16x Fabric (selling pays more: 1,000 vs 800 coins)"},
    "Acoustic Guitar":                {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 4x Metal Parts, 6x Wires (selling pays more: 7,000 vs 1,500 coins)"},
    "Adrenaline Shot":                {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Plastic Parts (selling pays more: 300 vs 110 coins)"},
    "Alarm Clock":                    {"status": RECYCLE, "reason": "Recycles into 6x Plastic Parts, 1x Processor (selling pays more: 1,000 vs 860 coins)"},
    "Assessor Matrix":                {"status": RECYCLE, "reason": "Recycles into 3x Advanced ARC Powercell, 1x Advanced Mechanical Components (selling pays more: 5,000 vs 3,670 coins)"},
    "Bandage":                        {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 2x Fabric (selling pays more: 250 vs 100 coins)"},
    "Barricade Kit":                  {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 4x Metal Parts (selling pays more: 640 vs 300 coins)"},
    "Binoculars":                     {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 4x Plastic Parts, 2x Rubber Parts (selling pays more: 640 vs 340 coins)"},
    "Blue Light Stick":               {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals (selling pays more: 150 vs 50 coins)"},
    "Broken Flashlight":              {"status": RECYCLE, "reason": "Recycles into 2x Battery, 6x Metal Parts (selling pays more: 1,000 vs 950 coins)"},
    "Broken Guidance System":         {"status": RECYCLE, "reason": "Recycles into 4x Processor"},
    "Broken Handheld Radio":          {"status": RECYCLE, "reason": "Recycles into 3x Sensors, 2x Wires (selling pays more: 2,000 vs 1,900 coins)"},
    "Broken Taser":                   {"status": RECYCLE, "reason": "Recycles into 2x Battery, 2x Wires (selling pays more: 1,000 vs 900 coins)"},
    "Burned Arc Circuitry":           {"status": RECYCLE, "reason": "Recycles into 2x ARC Alloy (selling pays more: 640 vs 400 coins)"},
    "Camera Lens":                    {"status": RECYCLE, "reason": "Recycles into 8x Plastic Parts (selling pays more: 640 vs 480 coins)"},
    "Candle Holder":                  {"status": RECYCLE, "reason": "Recycles into 8x Metal Parts (selling pays more: 640 vs 600 coins)"},
    "Candleberries":                  {"status": RECYCLE, "reason": "Recycles into 2x Assorted Seeds (selling pays more: 460 vs 200 coins)"},
    "Coolant":                        {"status": RECYCLE, "reason": "Recycles into 5x Chemicals, 2x Oil (selling pays more: 1,000 vs 850 coins)"},
    "Cooling Coil":                   {"status": RECYCLE, "reason": "Recycles into 6x Chemicals, 2x Steel Spring (selling pays more: 1,000 vs 900 coins)"},
    "Cooling Fan":                    {"status": RECYCLE, "reason": "Recycles into 14x Plastic Parts, 4x Wires (selling pays more: 2,000 vs 1,640 coins)"},
    "Crash Mat":                      {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 6x Fabric, 3x Plastic Parts (selling pays more: 1,200 vs 480 coins)"},
    "Crumpled Plastic Bottle":        {"status": RECYCLE, "reason": "Recycles into 4x Plastic Parts (selling pays more: 270 vs 240 coins)"},
    "Damaged ARC Motion Core":        {"status": RECYCLE, "reason": "Recycles into 2x ARC Alloy (selling pays more: 640 vs 400 coins)"},
    "Damaged ARC Powercell":          {"status": RECYCLE, "reason": "Recycles into 1x ARC Alloy (selling pays more: 293 vs 200 coins)"},
    "Damaged Fireball Burner":        {"status": RECYCLE, "reason": "Recycles into 1x ARC Alloy (selling pays more: 270 vs 200 coins)"},
    "Damaged Hornet Driver":          {"status": RECYCLE, "reason": "Recycles into 2x ARC Alloy (selling pays more: 640 vs 400 coins)"},
    "Damaged Rocketeer Driver":       {"status": RECYCLE, "reason": "Recycles into 3x ARC Alloy (selling pays more: 1,000 vs 600 coins)"},
    "Damaged Tick Pod":               {"status": RECYCLE, "reason": "Recycles into 1x ARC Alloy (selling pays more: 270 vs 200 coins)"},
    "Damaged Wasp Driver":            {"status": RECYCLE, "reason": "Recycles into 1x ARC Alloy (selling pays more: 270 vs 200 coins)"},
    "Deadline":                       {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x ARC Circuitry, 1x Explosive Compound (selling pays more: 6,000 vs 2,000 coins)"},
    "Defibrillator":                  {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Moss, 1x Plastic Parts (selling pays more: 1,000 vs 560 coins)"},
    "Degraded ARC Rubber":            {"status": RECYCLE, "reason": "Recycles into 11x Rubber Parts (selling pays more: 640 vs 550 coins)"},
    "Diving Goggles":                 {"status": RECYCLE, "reason": "Recycles into 12x Rubber Parts (selling pays more: 640 vs 600 coins)"},
    "Door Blocker":                   {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 2x Metal Parts (selling pays more: 270 vs 150 coins)"},
    "Dried-Out ARC Resin":            {"status": RECYCLE, "reason": "Recycles into 9x Plastic Parts (selling pays more: 640 vs 540 coins)"},
    "Explosive Mine":                 {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Oil, 1x Sensors (selling pays more: 1,500 vs 800 coins)"},
    "Fertilizer":                     {"status": RECYCLE, "reason": "Recycles into 2x Assorted Seeds (selling pays more: 1,000 vs 200 coins)"},
    "Firecracker":                    {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 3x Plastic Parts (selling pays more: 270 vs 180 coins)"},
    "Fireworks Box":                  {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Explosive Compound (selling pays more: 2,000 vs 1,000 coins)"},
    "Flame Spray":                    {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Canister, 1x Fireball Burner (selling pays more: 2,000 vs 940 coins)"},
    "Fossilized Lightning":           {"status": RECYCLE, "reason": "Recycles into 3x Explosive Compound (selling pays more: 4,000 vs 3,000 coins)"},
    "Frequency Modulation Box":       {"status": RECYCLE, "reason": "Recycles into 1x Advanced Electrical Components, 1x Speaker Component (selling pays more: 3,000 vs 2,250 coins)"},
    "Frying Pan":                     {"status": RECYCLE, "reason": "Recycles into 8x Metal Parts (selling pays more: 640 vs 600 coins)"},
    "Garlic Press":                   {"status": RECYCLE, "reason": "Recycles into 12x Metal Parts (selling pays more: 1,000 vs 900 coins)"},
    "Gas Mine":                       {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Rubber Parts (selling pays more: 270 vs 100 coins)"},
    "Glitched ARC Circuitry":         {"status": RECYCLE, "reason": "Recycles into 6x ARC Alloy, 1x Exodus Modules (selling pays more: 5,000 vs 3,950 coins)"},
    "Glitched ARC Light Ring":        {"status": RECYCLE, "reason": "Recycles into 1x Advanced Electrical Components, 3x ARC Alloy (selling pays more: 3,000 vs 2,350 coins)"},
    "Glitched ARC Phased Array":      {"status": RECYCLE, "reason": "Recycles into 3x ARC Alloy, 2x Sensors (selling pays more: 2,000 vs 1,600 coins)"},
    "Glitched ARC Power Converter":   {"status": RECYCLE, "reason": "Recycles into 3x ARC Alloy (selling pays more: 640 vs 600 coins)"},
    "Glitched ARC Transmitter":       {"status": RECYCLE, "reason": "Recycles into 1x ARC Alloy, 1x Electrical Components (selling pays more: 1,000 vs 840 coins)"},
    "Green Light Stick":              {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals (selling pays more: 150 vs 50 coins)"},
    "Headphones":                     {"status": RECYCLE, "reason": "Recycles into 7x Rubber Parts, 1x Speaker Component (selling pays more: 1,000 vs 850 coins)"},
    "Heavy Fuze Grenade":             {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Oil, 2x Rubber Parts (selling pays more: 1,600 vs 400 coins)"},
    "Herbal Bandage":                 {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 2x Assorted Seeds, 5x Fabric (selling pays more: 900 vs 450 coins)"},
    "Household Cleaner":              {"status": RECYCLE, "reason": "Recycles into 11x Chemicals (selling pays more: 640 vs 550 coins)"},
    "Humidifier":                     {"status": RECYCLE, "reason": "Recycles into 2x Canister, 2x Wires"},
    "Ice Cream Scooper":              {"status": RECYCLE, "reason": "Recycles into 7x Metal Parts (selling pays more: 640 vs 525 coins)"},
    "Impure ARC Coolant":             {"status": RECYCLE, "reason": "Recycles into 12x Chemicals (selling pays more: 640 vs 600 coins)"},
    "Industrial Charger":             {"status": RECYCLE, "reason": "Recycles into 5x Metal Parts, 1x Voltage Converter (selling pays more: 1,000 vs 875 coins)"},
    "Industrial Magnet":              {"status": RECYCLE, "reason": "Recycles into 2x Magnet, 4x Metal Parts (selling pays more: 1,000 vs 900 coins)"},
    "Jolt Mine":                      {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Battery, 2x Plastic Parts (selling pays more: 850 vs 370 coins)"},
    "Li'l Smoke Grenade":             {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Plastic Parts (selling pays more: 300 vs 110 coins)"},
    "Light Impact Grenade":           {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Plastic Parts (selling pays more: 270 vs 110 coins)"},
    "Metal Brackets":                 {"status": RECYCLE, "reason": "Recycles into 8x Metal Parts (selling pays more: 640 vs 600 coins)"},
    "Microscope":                     {"status": RECYCLE, "reason": "Recycles into 1x Advanced Mechanical Components, 3x Magnet (selling pays more: 3,000 vs 2,650 coins)"},
    "Mini Centrifuge":                {"status": RECYCLE, "reason": "Recycles into 1x Advanced Mechanical Components, 2x Canister (selling pays more: 3,000 vs 2,350 coins)"},
    "Noisemaker":                     {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Speaker Component (selling pays more: 640 vs 500 coins)"},
    "Number Plate":                   {"status": RECYCLE, "reason": "Recycles into 3x Metal Parts (selling pays more: 270 vs 225 coins)"},
    "Photoelectric Cloak":            {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Advanced Electrical Components, 1x Speaker Component (selling pays more: 5,000 vs 2,250 coins)"},
    "Polluted Air Filter":            {"status": RECYCLE, "reason": "Recycles into 6x Fabric, 2x Oil (selling pays more: 1,000 vs 900 coins)"},
    "Power Bank":                     {"status": RECYCLE, "reason": "Recycles into 2x Battery, 2x Wires (selling pays more: 1,000 vs 900 coins)"},
    "Powered Descender":              {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Advanced Electrical Components, 2x ARC Circuitry (selling pays more: 10,000 vs 3,750 coins)"},
    "Projector":                      {"status": RECYCLE, "reason": "Recycles into 1x Processor, 2x Wires (selling pays more: 1,000 vs 900 coins)"},
    "Pulse Mine":                     {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 6x Chemicals (selling pays more: 470 vs 300 coins)"},
    "Radio Relay":                    {"status": RECYCLE, "reason": "Recycles into 2x Sensors, 2x Speaker Component (selling pays more: 3,000 vs 2,000 coins)"},
    "Recorder":                       {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 10x Plastic Parts (selling pays more: 1,000 vs 600 coins)"},
    "Red Light Stick":                {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals (selling pays more: 150 vs 50 coins)"},
    "Remote Control":                 {"status": RECYCLE, "reason": "Recycles into 7x Plastic Parts, 1x Sensors (selling pays more: 1,000 vs 920 coins)"},
    "Remote Raider Flare":            {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Rubber Parts (selling pays more: 270 vs 100 coins)"},
    "Ripped Safety Vest":             {"status": RECYCLE, "reason": "Recycles into 1x Durable Cloth, 1x Magnet (selling pays more: 1,000 vs 940 coins)"},
    "Rocket Thruster":                {"status": RECYCLE, "reason": "Recycles into 6x Metal Parts, 2x Synthesized Fuel (selling pays more: 2,000 vs 1,850 coins)"},
    "Roots":                          {"status": RECYCLE, "reason": "Recycles into 1x Assorted Seeds (selling pays more: 640 vs 100 coins)"},
    "Rubber Pad":                     {"status": RECYCLE, "reason": "Recycles into 18x Rubber Parts (selling pays more: 1,000 vs 900 coins)"},
    "Ruined Accordion":               {"status": RECYCLE, "reason": "Recycles into 18x Rubber Parts, 3x Steel Spring (selling pays more: 2,000 vs 1,800 coins)"},
    "Ruined Augment":                 {"status": RECYCLE, "reason": "Recycles into 2x Plastic Parts, 2x Rubber Parts (selling pays more: 270 vs 220 coins)"},
    "Ruined Baton":                   {"status": RECYCLE, "reason": "Recycles into 6x Metal Parts, 3x Rubber Parts (selling pays more: 640 vs 600 coins)"},
    "Ruined Handcuffs":               {"status": RECYCLE, "reason": "Recycles into 8x Metal Parts (selling pays more: 640 vs 600 coins)"},
    "Ruined Parachute":               {"status": RECYCLE, "reason": "Recycles into 10x Fabric (selling pays more: 640 vs 500 coins)"},
    "Ruined Riot Shield":             {"status": RECYCLE, "reason": "Recycles into 10x Plastic Parts, 6x Rubber Parts (selling pays more: 1,000 vs 900 coins)"},
    "Ruined Tactical Vest":           {"status": RECYCLE, "reason": "Recycles into 5x Fabric, 1x Magnet (selling pays more: 640 vs 550 coins)"},
    "Rusty ARC Steel":                {"status": RECYCLE, "reason": "Recycles into 8x Metal Parts (selling pays more: 640 vs 600 coins)"},
    "Sample Cleaner":                 {"status": RECYCLE, "reason": "Recycles into 14x Assorted Seeds, 2x Electrical Components (selling pays more: 3,000 vs 2,680 coins)"},
    "Seeker Grenade":                 {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Crude Explosives (selling pays more: 640 vs 270 coins)"},
    "Shaker":                         {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 10x Plastic Parts (selling pays more: 1,000 vs 600 coins)"},
    "Shield Recharger":               {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 4x Rubber Parts (selling pays more: 520 vs 200 coins)"},
    "Showstopper":                    {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Electrical Components, 1x Voltage Converter (selling pays more: 2,100 vs 1,140 coins)"},
    "Shrapnel Grenade":               {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Crude Explosives, 1x Metal Parts (selling pays more: 800 vs 345 coins)"},
    "Signal Amplifier":               {"status": RECYCLE, "reason": "Recycles into 2x Electrical Components, 2x Voltage Converter (selling pays more: 3,000 vs 2,280 coins)"},
    "Snap Blast Grenade":             {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Magnet (selling pays more: 800 vs 350 coins)"},
    "Snap Hook":                      {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Power Rod, 3x Rope (selling pays more: 14,000 vs 6,500 coins)"},
    "Spectrometer":                   {"status": RECYCLE, "reason": "Recycles into 1x Advanced Electrical Components, 1x Sensors (selling pays more: 3,000 vs 2,250 coins)"},
    "Spectrum Analyzer":              {"status": RECYCLE, "reason": "Recycles into 1x Exodus Modules, 1x Sensors (selling pays more: 3,500 vs 3,250 coins)"},
    "Spring Cushion":                 {"status": RECYCLE, "reason": "Recycles into 2x Durable Cloth, 2x Steel Spring (selling pays more: 2,000 vs 1,880 coins)"},
    "Sterilized Bandage":             {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Antiseptic, 1x Fabric (selling pays more: 2,000 vs 1,050 coins)"},
    "Surge Coil":                     {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Electrical Components, 1x Sensors (selling pays more: 2,100 vs 1,140 coins)"},
    "Surge Shield Recharger":         {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Electrical Components (selling pays more: 1,200 vs 640 coins)"},
    "Tagging Grenade":                {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Plastic Parts, 1x Sensors (selling pays more: 1,000 vs 560 coins)"},
    "Tattered Arc Lining":            {"status": RECYCLE, "reason": "Recycles into 12x Fabric (selling pays more: 640 vs 600 coins)"},
    "Tattered Clothes":               {"status": RECYCLE, "reason": "Recycles into 11x Fabric (selling pays more: 640 vs 550 coins)"},
    "Telemetry Transceiver":          {"status": RECYCLE, "reason": "Recycles into 1x Advanced Electrical Components, 1x Processor (selling pays more: 3,000 vs 2,250 coins)"},
    "Thermostat":                     {"status": RECYCLE, "reason": "Recycles into 7x Rubber Parts, 1x Sensors (selling pays more: 1,000 vs 850 coins)"},
    "Torn Blanket":                   {"status": RECYCLE, "reason": "Recycles into 12x Fabric (selling pays more: 640 vs 600 coins)"},
    "Trailblazer":                    {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 2x Crude Explosives (selling pays more: 2,200 vs 540 coins)"},
    "Trigger 'Nade":                  {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals, 1x Processor (selling pays more: 1,000 vs 550 coins)"},
    "Turbo Pump":                     {"status": RECYCLE, "reason": "Recycles into 1x Mechanical Components, 3x Oil (selling pays more: 2,000 vs 1,540 coins)"},
    "Unusable Weapon":                {"status": RECYCLE, "reason": "Recycles into 4x Metal Parts, 5x Simple Gun Parts (selling pays more: 2,000 vs 1,950 coins)"},
    "Vita Shot":                      {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 4x Chemicals, 1x Syringe (selling pays more: 2,200 vs 700 coins)"},
    "Vita Spray":                     {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Antiseptic, 1x Canister (selling pays more: 3,400 vs 1,300 coins)"},
    "Water Filter":                   {"status": RECYCLE, "reason": "Recycles into 3x Canister, 2x Rubber Parts"},
    "Water Pump":                     {"status": RECYCLE, "reason": "Recycles into 4x Metal Parts, 2x Oil (selling pays more: 1,000 vs 900 coins)"},
    "White Flag":                     {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 5x Fabric, 1x Plastic Parts (selling pays more: 640 vs 310 coins)"},
    "Wolfpack":                       {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x ARC Motion Core, 1x Explosive Compound (selling pays more: 6,000 vs 2,000 coins)"},
    "Yellow Light Stick":             {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Chemicals (selling pays more: 150 vs 50 coins)"},
    "Zipline":                        {"status": RECYCLE, "reason": "Consumable - use it, or recycles into 1x Metal Parts, 1x Rope (selling pays more: 1,000 vs 575 coins)"},

    # ============================================================
    # KEEP - Quests, workshop, Scrappy, crafting, expeditions/projects
    # ============================================================
    "ARC Alloy":                      {"status": KEEP, "reason": "Quest: Clearer Skies x3 + Workshop: Explosives Station Lv1 x6 + Workshop: Medical Lab Lv1 x6 + Workshop: Utility Station Lv1 x6 + Expedition 5 x80 + crafting", "qty": 101, "expedition": {"only": False, "no_exp_reason": "Quest: Clearer Skies x3 + Workshop: Explosives Station Lv1 x6 + Workshop: Medical Lab Lv1 x6 + Workshop: Utility Station Lv1 x6 + crafting", "no_exp_qty": 21}},
    "ARC Circuitry":                  {"status": KEEP, "reason": "Workshop: Refiner Lv3 x10 + Expedition 5 x20 + crafting", "qty": 30, "expedition": {"only": False, "no_exp_reason": "Workshop: Refiner Lv3 x10 + crafting", "no_exp_qty": 10}},
    "ARC Motion Core":                {"status": KEEP, "reason": "Workshop: Refiner Lv2 x5 + crafting", "qty": 5},
    "ARC Performance Steel":          {"status": KEEP, "reason": "Project: Trophy Display x10", "qty": 10, "expedition": {"only": True}},
    "ARC Powercell":                  {"status": KEEP, "reason": "Quest: A Prime Specimen x2 + Workshop: Refiner Lv1 x5 + crafting", "qty": 7},
    "ARC Synthetic Resin":            {"status": KEEP, "reason": "Project: Trophy Display x10", "qty": 10, "expedition": {"only": True}},
    "Advanced ARC Powercell":         {"status": KEEP, "reason": "Crafting: Energy Clip, Surge Shield Recharger", "qty": 0},
    "Advanced Electrical Components": {"status": KEEP, "reason": "Workshop: Gear Bench Lv3 x5 + Workshop: Utility Station Lv3 x5 + crafting", "qty": 10},
    "Advanced Mechanical Components": {"status": KEEP, "reason": "Workshop: Gunsmith Lv3 x5 + Expedition 5 x5 + crafting", "qty": 10, "expedition": {"only": False, "no_exp_reason": "Workshop: Gunsmith Lv3 x5 + crafting", "no_exp_qty": 5}},
    "Agave":                          {"status": KEEP, "reason": "Crafting: Agave Juice", "qty": 0},
    "Air Freshener":                  {"status": KEEP, "reason": "Crafting: Flame Spray", "qty": 0},
    "Antiseptic":                     {"status": KEEP, "reason": "Quest: Doctor's Orders x2 + Workshop: Medical Lab Lv3 x8 + crafting", "qty": 10},
    "Apricot":                        {"status": KEEP, "reason": "Scrappy (dog) upgrades x15 + crafting", "qty": 15},
    "Assorted Seeds":                 {"status": KEEP, "reason": "Crafting: Shaker", "qty": 0},
    "Bastion Cell":                   {"status": KEEP, "reason": "Quest: Settled in Full x1 + Workshop: Gear Bench Lv3 x6 + Expedition 5 x5 + Project: Trophy Display x5", "qty": 17, "expedition": {"only": False, "no_exp_reason": "Quest: Settled in Full x1 + Workshop: Gear Bench Lv3 x6", "no_exp_qty": 7}},
    "Battery":                        {"status": KEEP, "reason": "Quest: After Rain Comes x2 + Quest: Trash Into Treasure x1 + crafting", "qty": 3},
    "Bicycle Pump":                   {"status": KEEP, "reason": "Quest: The League x1", "qty": 1},
    "Blaze Grenade":                  {"status": KEEP, "reason": "Crafting: Blaze Grenade Trap", "qty": 0},
    "Bombardier Cell":                {"status": KEEP, "reason": "Quest: Bombing Run x1 + Workshop: Refiner Lv3 x6 + Project: Trophy Display x8", "qty": 15, "expedition": {"only": False, "no_exp_reason": "Quest: Bombing Run x1 + Workshop: Refiner Lv3 x6", "no_exp_qty": 7}},
    "Book":                           {"status": KEEP, "reason": "Quest: Building a Library x3", "qty": 3},
    "Canister":                       {"status": KEEP, "reason": "Crafting material (6 recipes)", "qty": 0},
    "Cat Bed":                        {"status": KEEP, "reason": "Scrappy (dog) upgrades x1", "qty": 1},
    "Celeste's Journal":              {"status": KEEP, "reason": "Quest: Celeste’s Journals x2", "qty": 2},
    "Chemicals":                      {"status": KEEP, "reason": "Workshop: Explosives Station Lv1 x50 + crafting", "qty": 50},
    "Comet Igniter":                  {"status": KEEP, "reason": "Quest: Collision Course x1 + crafting", "qty": 1},
    "Complex Gun Parts":              {"status": KEEP, "reason": "Crafting material (3 recipes)", "qty": 0},
    "Cracked Bioscanner":             {"status": KEEP, "reason": "Workshop: Medical Lab Lv2 x2", "qty": 2},
    "Crude Explosives":               {"status": KEEP, "reason": "Workshop: Explosives Station Lv2 x5 + crafting", "qty": 5},
    "Damaged Heat Sink":              {"status": KEEP, "reason": "Workshop: Utility Station Lv2 x2", "qty": 2},
    "Deflated Football":              {"status": KEEP, "reason": "Quest: The League x1", "qty": 1},
    "Dodger's Note":                  {"status": KEEP, "reason": "Quest: Outstanding Balance x1", "qty": 1},
    "Dog Collar":                     {"status": KEEP, "reason": "Scrappy (dog) upgrades x1", "qty": 1},
    "Duct Tape":                      {"status": KEEP, "reason": "Expedition 5 x25 + crafting", "qty": 25, "expedition": {"only": False, "no_exp_reason": "Crafting material (11 recipes)", "no_exp_qty": 0}},
    "Durable Cloth":                  {"status": KEEP, "reason": "Quest: Doctor's Orders x1 + Workshop: Medical Lab Lv2 x5 + Expedition 5 x30 + crafting", "qty": 36, "expedition": {"only": False, "no_exp_reason": "Quest: Doctor's Orders x1 + Workshop: Medical Lab Lv2 x5 + crafting", "no_exp_qty": 6}},
    "Dusty Film Reel":                {"status": KEEP, "reason": "Quest: A Dead End x1", "qty": 1},
    "ESR Analyzer":                   {"status": KEEP, "reason": "Quest: A Reveal in Ruins x1", "qty": 1},
    "Electrical Components":          {"status": KEEP, "reason": "Workshop: Gear Bench Lv2 x5 + Workshop: Utility Station Lv2 x5 + crafting", "qty": 10},
    "Empty Wine Bottle":              {"status": KEEP, "reason": "Crafting: Agave Juice", "qty": 0},
    "Espresso Machine Parts":         {"status": KEEP, "reason": "Quest: Espresso x1", "qty": 1},
    "Exodus Modules":                 {"status": KEEP, "reason": "Project: Trophy Display x5 + crafting", "qty": 5, "expedition": {"only": False, "no_exp_reason": "Crafting material (5 recipes)", "no_exp_qty": 0}},
    "Experimental Seed Sample":       {"status": KEEP, "reason": "Quest: The Root of the Matter x1", "qty": 1},
    "Expired Respirator":             {"status": KEEP, "reason": "Project: Trophy Display x3", "qty": 3, "expedition": {"only": True}},
    "Explosive Compound":             {"status": KEEP, "reason": "Workshop: Explosives Station Lv3 x5 + crafting", "qty": 5},
    "Fabric":                         {"status": KEEP, "reason": "Workshop: Gear Bench Lv1 x30 + Workshop: Medical Lab Lv1 x50 + crafting", "qty": 80},
    "Fireball Burner":                {"status": KEEP, "reason": "Quest: Test Case x1 + Workshop: Refiner Lv2 x8 + crafting", "qty": 9},
    "Firefly Burner":                 {"status": KEEP, "reason": "Quest: Test Case x1 + crafting", "qty": 1},
    "First Wave Compass":             {"status": KEEP, "reason": "Quest: Broken Monument x1", "qty": 1},
    "First Wave Rations":             {"status": KEEP, "reason": "Quest: Broken Monument x1", "qty": 1},
    "First Wave Tape":                {"status": KEEP, "reason": "Quest: Broken Monument x1", "qty": 1},
    "Flow Controller":                {"status": KEEP, "reason": "Quest: Snap and Salvage x1", "qty": 1},
    "Fried Motherboard":              {"status": KEEP, "reason": "Workshop: Utility Station Lv3 x3", "qty": 3},
    "Gas Grenade":                    {"status": KEEP, "reason": "Crafting: Gas Grenade Trap", "qty": 0},
    "Geiger Counter":                 {"status": KEEP, "reason": "Project: Trophy Display x3", "qty": 3, "expedition": {"only": True}},
    "Great Mullein":                  {"status": KEEP, "reason": "Quest: Doctor's Orders x1 + crafting", "qty": 1},
    "Heavy Gun Parts":                {"status": KEEP, "reason": "Crafting material (5 recipes)", "qty": 0},
    "Hornet Driver":                  {"status": KEEP, "reason": "Quest: Test Case x1 + Quest: The Trifecta x2 + Workshop: Gear Bench Lv2 x5 + Project: Trophy Display x15 + crafting", "qty": 23, "expedition": {"only": False, "no_exp_reason": "Quest: Test Case x1 + Quest: The Trifecta x2 + Workshop: Gear Bench Lv2 x5 + crafting", "no_exp_qty": 8}},
    "Industrial Battery":             {"status": KEEP, "reason": "Workshop: Gear Bench Lv3 x3", "qty": 3},
    "Ion Sputter":                    {"status": KEEP, "reason": "Quest: With a View x1", "qty": 1},
    "Laboratory Reagents":            {"status": KEEP, "reason": "Workshop: Explosives Station Lv3 x3", "qty": 3},
    "Lance's Mixtape (5th Edition)":  {"status": KEEP, "reason": "Expedition 5 x2", "qty": 2, "expedition": {"only": True}},
    "Leaper Pulse Unit":              {"status": KEEP, "reason": "Quest: Into the Fray x1 + Workshop: Utility Station Lv3 x4 + Project: Trophy Display x10", "qty": 15, "expedition": {"only": False, "no_exp_reason": "Quest: Into the Fray x1 + Workshop: Utility Station Lv3 x4", "no_exp_qty": 5}},
    "Lemon":                          {"status": KEEP, "reason": "Scrappy (dog) upgrades x3 + crafting", "qty": 3},
    "Lidar Scanner":                  {"status": KEEP, "reason": "Quest: A Lay of the Land x1", "qty": 1},
    "Light Gun Parts":                {"status": KEEP, "reason": "Crafting: Bobcat I, Complex Gun Parts", "qty": 0},
    "Lure Grenade":                   {"status": KEEP, "reason": "Crafting: Lure Grenade Trap", "qty": 0},
    "Magnet":                         {"status": KEEP, "reason": "Expedition 5 x15 + crafting", "qty": 15, "expedition": {"only": False, "no_exp_reason": "Crafting material (6 recipes)", "no_exp_qty": 0}},
    "Magnetic Accelerator":           {"status": KEEP, "reason": "Expedition 5 x3 + Project: Trophy Display x10 + crafting", "qty": 13, "expedition": {"only": False, "no_exp_reason": "Crafting material (8 recipes)", "no_exp_qty": 0}},
    "Magnetron":                      {"status": KEEP, "reason": "Quest: Snap and Salvage x1", "qty": 1},
    "Major Aiva's Mementos":          {"status": KEEP, "reason": "Quest: The Major’s Footlocker x1", "qty": 1},
    "Major Aiva's Patch":             {"status": KEEP, "reason": "Quest: Echoes of Victory Ridge x1", "qty": 1},
    "Matriarch Reactor":              {"status": KEEP, "reason": "Project: Trophy Display x3 + crafting", "qty": 3, "expedition": {"only": False, "no_exp_reason": "Crafting: Aphelion", "no_exp_qty": 0}},
    "Mechanical Components":          {"status": KEEP, "reason": "Workshop: Gunsmith Lv2 x5 + Expedition 5 x20 + crafting", "qty": 25, "expedition": {"only": False, "no_exp_reason": "Workshop: Gunsmith Lv2 x5 + crafting", "no_exp_qty": 5}},
    "Medium Gun Parts":               {"status": KEEP, "reason": "Crafting material (7 recipes)", "qty": 0},
    "Metal Parts":                    {"status": KEEP, "reason": "Workshop: Refiner Lv1 x60 + Workshop: Gunsmith Lv1 x20 + Expedition 5 x150 + crafting", "qty": 230, "expedition": {"only": False, "no_exp_reason": "Workshop: Refiner Lv1 x60 + Workshop: Gunsmith Lv1 x20 + crafting", "no_exp_qty": 80}},
    "Mod Components":                 {"status": KEEP, "reason": "Crafting material (14 recipes)", "qty": 0},
    "Moisture Meter":                 {"status": KEEP, "reason": "Quest: Unexpected Initiative x1", "qty": 1},
    "Moss":                           {"status": KEEP, "reason": "Crafting: Defibrillator", "qty": 0},
    "Motor":                          {"status": KEEP, "reason": "Workshop: Refiner Lv3 x3", "qty": 3},
    "Mushroom":                       {"status": KEEP, "reason": "Scrappy (dog) upgrades x12", "qty": 12},
    "Nutrient Meter":                 {"status": KEEP, "reason": "Quest: Unexpected Initiative x1", "qty": 1},
    "Official Shutdown Documentation":{"status": KEEP, "reason": "Quest: Last Entry x1", "qty": 1},
    "Oil":                            {"status": KEEP, "reason": "Crafting material (3 recipes)", "qty": 0},
    "Old World Books":                {"status": KEEP, "reason": "Quest: Cold Storage x1", "qty": 1},
    "Olives":                         {"status": KEEP, "reason": "Scrappy (dog) upgrades x6", "qty": 6},
    "Plastic Parts":                  {"status": KEEP, "reason": "Workshop: Gear Bench Lv1 x25 + Workshop: Utility Station Lv1 x50 + Expedition 5 x100 + crafting", "qty": 175, "expedition": {"only": False, "no_exp_reason": "Workshop: Gear Bench Lv1 x25 + Workshop: Utility Station Lv1 x50 + crafting", "no_exp_qty": 75}},
    "Pop Trigger":                    {"status": KEEP, "reason": "Workshop: Explosives Station Lv2 x5 + Project: Trophy Display x15 + crafting", "qty": 20, "expedition": {"only": False, "no_exp_reason": "Workshop: Explosives Station Lv2 x5 + crafting", "no_exp_qty": 5}},
    "Portable TV":                    {"status": KEEP, "reason": "Quest: Movie Night x1", "qty": 1},
    "Possibly Toxic Plant":           {"status": KEEP, "reason": "Quest: A New Type of Plant x1", "qty": 1},
    "Power Cable":                    {"status": KEEP, "reason": "Workshop: Gear Bench Lv2 x3", "qty": 3},
    "Power Rod":                      {"status": KEEP, "reason": "Quest: Tribute to Toledo x1 + crafting", "qty": 1},
    "Precision Gimbal":               {"status": KEEP, "reason": "Quest: Safe Harbor x1", "qty": 1},
    "Prickly Pear":                   {"status": KEEP, "reason": "Scrappy (dog) upgrades x6 + crafting", "qty": 6},
    "Processor":                      {"status": KEEP, "reason": "Crafting material (10 recipes)", "qty": 0},
    "Project Heartwood Blueprints":   {"status": KEEP, "reason": "Quest: Stable Housing x1", "qty": 1},
    "Queen Reactor":                  {"status": KEEP, "reason": "Project: Trophy Display x3 + crafting", "qty": 3, "expedition": {"only": False, "no_exp_reason": "Crafting: Equalizer, Jupiter", "no_exp_qty": 0}},
    "Radio":                          {"status": KEEP, "reason": "Expedition 5 x2", "qty": 2, "expedition": {"only": True}},
    "Rocketeer Driver":               {"status": KEEP, "reason": "Quest: Out of the Shadows x1 + Workshop: Explosives Station Lv3 x3 + Expedition 5 x3 + Project: Trophy Display x8 + crafting", "qty": 15, "expedition": {"only": False, "no_exp_reason": "Quest: Out of the Shadows x1 + Workshop: Explosives Station Lv3 x3 + crafting", "no_exp_qty": 4}},
    "Rope":                           {"status": KEEP, "reason": "Crafting: Snap Hook, Zipline", "qty": 0},
    "Rotary Encoder":                 {"status": KEEP, "reason": "Quest: With a View x1", "qty": 1},
    "Rubber Parts":                   {"status": KEEP, "reason": "Workshop: Gunsmith Lv1 x30 + crafting", "qty": 30},
    "Rusted Bolts":                   {"status": KEEP, "reason": "Project: Trophy Display x3", "qty": 3, "expedition": {"only": True}},
    "Rusted Gear":                    {"status": KEEP, "reason": "Workshop: Gunsmith Lv3 x3", "qty": 3},
    "Rusted Shut Medical Kit":        {"status": KEEP, "reason": "Workshop: Medical Lab Lv3 x3", "qty": 3},
    "Rusted Tools":                   {"status": KEEP, "reason": "Workshop: Gunsmith Lv2 x3", "qty": 3},
    "Scout Patrol Note":              {"status": KEEP, "reason": "Quest: Dust on the Wires x1", "qty": 1},
    "Secret Meeting Info":            {"status": KEEP, "reason": "Quest: Furtive Meetings x1", "qty": 1},
    "Sensors":                        {"status": KEEP, "reason": "Crafting material (4 recipes)", "qty": 0},
    "Sentinel Firing Core":           {"status": KEEP, "reason": "Workshop: Gunsmith Lv3 x4", "qty": 4},
    "Shredder Gyro":                  {"status": KEEP, "reason": "Project: Trophy Display x5 + crafting", "qty": 5, "expedition": {"only": False, "no_exp_reason": "Crafting: Dolabra", "no_exp_qty": 0}},
    "Simple Gun Parts":               {"status": KEEP, "reason": "Crafting material (7 recipes)", "qty": 0},
    "Smoke Grenade":                  {"status": KEEP, "reason": "Crafting: Smoke Grenade Trap", "qty": 0},
    "Snitch Scanner":                 {"status": KEEP, "reason": "Quest: The Trifecta x2 + Workshop: Utility Station Lv2 x6", "qty": 8},
    "Speaker Component":              {"status": KEEP, "reason": "Expedition 5 x15 + crafting", "qty": 15, "expedition": {"only": False, "no_exp_reason": "Crafting material (3 recipes)", "no_exp_qty": 0}},
    "Spotter Relay":                  {"status": KEEP, "reason": "Quest: Combat Recon x1 + Project: Trophy Display x10", "qty": 11, "expedition": {"only": False, "no_exp_reason": "Quest: Combat Recon x1", "no_exp_qty": 1}},
    "Stack of Movie Tapes":           {"status": KEEP, "reason": "Quest: Movie Night x1", "qty": 1},
    "Steel Spring":                   {"status": KEEP, "reason": "Crafting material (13 recipes)", "qty": 0},
    "Surveyor Vault":                 {"status": KEEP, "reason": "Quest: Mixed Signals x1 + Workshop: Medical Lab Lv3 x5 + Project: Trophy Display x5", "qty": 11, "expedition": {"only": False, "no_exp_reason": "Quest: Mixed Signals x1 + Workshop: Medical Lab Lv3 x5", "no_exp_qty": 6}},
    "Synthesized Fuel":               {"status": KEEP, "reason": "Workshop: Explosives Station Lv2 x3 + crafting", "qty": 3},
    "Syringe":                        {"status": KEEP, "reason": "Quest: Doctor's Orders x1 + crafting", "qty": 1},
    "Tick Pod":                       {"status": KEEP, "reason": "Workshop: Medical Lab Lv2 x8 + Project: Trophy Display x15 + crafting", "qty": 23, "expedition": {"only": False, "no_exp_reason": "Workshop: Medical Lab Lv2 x8 + crafting", "no_exp_qty": 8}},
    "Toaster":                        {"status": KEEP, "reason": "Workshop: Refiner Lv2 x3", "qty": 3},
    "Turbine Compressor":             {"status": KEEP, "reason": "Crafting: Powered Descender", "qty": 0},
    "Vaporizer Regulator":            {"status": KEEP, "reason": "Crafting: Dolabra", "qty": 0},
    "Very Comfortable Pillow":        {"status": KEEP, "reason": "Scrappy (dog) upgrades x3", "qty": 3},
    "Voltage Converter":              {"status": KEEP, "reason": "Expedition 5 x10 + crafting", "qty": 10, "expedition": {"only": False, "no_exp_reason": "Crafting: Heavy Shield, Showstopper", "no_exp_qty": 0}},
    "Wasp Driver":                    {"status": KEEP, "reason": "Quest: The Trifecta x2 + Workshop: Gunsmith Lv2 x8 + Project: Trophy Display x20", "qty": 30, "expedition": {"only": False, "no_exp_reason": "Quest: The Trifecta x2 + Workshop: Gunsmith Lv2 x8", "no_exp_qty": 10}},
    "Wires":                          {"status": KEEP, "reason": "Quest: After Rain Comes x5 + Quest: Eyes on the Prize x3 + Quest: Flickering Threat x4 + Quest: Trash Into Treasure x6 + crafting", "qty": 18},
}
# END GENERATED ITEMS


def get_effective_item(data):
    """Return (status, reason, qty) adjusted for expedition toggle."""
    if expedition_mode["enabled"] or "expedition" not in data:
        return data["status"], data["reason"], data.get("qty", 0)
    exp = data["expedition"]
    if exp["only"]:
        return RECYCLE, "Expedition/project-only item (expeditions off)", 0
    return KEEP, exp["no_exp_reason"], exp["no_exp_qty"]


class ItemCompleter(Completer):
    """Live autocomplete dropdown showing items + status as you type."""

    def __init__(self):
        self.commands = ["list", "list keep", "list sell", "list recycle",
                         "expeditions on", "expeditions off", "exp on", "exp off",
                         "projects on", "projects off",
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
  {DIM}Data from arcraiders-data (arctracker.io){RESET}

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
        if query.lower() in ("expeditions on", "exp on", "projects on"):
            expedition_mode["enabled"] = True
            print(f"  {CYAN}Expeditions ON - including expedition + Trophy Display project needs{RESET}")
            print_status_counts()
            continue
        if query.lower() in ("expeditions off", "exp off", "projects off"):
            expedition_mode["enabled"] = False
            print(f"  {CYAN}Expeditions OFF - expedition/project-only items marked RECYCLE, quantities reduced{RESET}")
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
