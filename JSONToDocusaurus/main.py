#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Configuration: adjust these paths as needed
DATA_DIR = Path('../../Starforge/Assets/')
OUTPUT_DIR = Path('../../../Documentation/LuminDocs/docs/starforge-docs')
ENUM_DATA_DIR = Path('../../LuminaryEngine/Engine/Gameplay')

# JSON filenames and corresponding output directories
PAGES = {
    'items': ('Items/items.json', OUTPUT_DIR / "items.md"),
    'recipes': ('Recipes/recipes.json', OUTPUT_DIR / "recipes.md"),
    'spiritessence': ('SpiritEssence/spiritessence.json', OUTPUT_DIR / "spiritessences.md"),
    'stations': (None, OUTPUT_DIR / 'crafting-stations.md'),  # special case
}

# Per-enum file definitions: map enum name to its C# file
ENUM_FILES = {
    'ItemType': ENUM_DATA_DIR / 'Items/ItemType.cs',
    'SpiritType': ENUM_DATA_DIR / 'Spirits/SpiritType.cs',
    'SpiritTier': ENUM_DATA_DIR / 'Spirits/SpiritTier.cs',
}

# Ensure docs directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path):
    """Load JSON, handling potential UTF-8 BOM."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def parse_cs_enums(enum_files):
    """
    Parse C# enums from individual files. Returns a dict:
    { enum_name: { int_value: name, ... } }
    """
    enums = {}
    for enum_name, filepath in enum_files.items():
        mapping = {}
        if filepath.exists():
            text = filepath.read_text(encoding='utf-8-sig')
            pattern = rf'enum\s+{enum_name}\s*\{{([^}}]+)\}}'
            m = re.search(pattern, text)
            if m:
                body = m.group(1)
                value = 0
                for part in body.split(','):
                    line = part.strip()
                    if not line:
                        continue
                    if '=' in line:
                        name_str, val_str = map(str.strip, line.split('='))
                        name = name_str
                        try:
                            value = int(val_str)
                        except ValueError:
                            value = int(val_str, 0)
                    else:
                        name = re.split(r'\s', line)[0]
                    mapping[value] = name
                    value += 1
        enums[enum_name] = mapping
    return enums

# Load all enum mappings
enum_maps = parse_cs_enums(ENUM_FILES)

# Helper to format "Name (Id)"
def fmt_enum(enum_name, id_val):
    mapping = enum_maps.get(enum_name, {})
    name = mapping.get(id_val)
    return f"{name or id_val} ({id_val})"


def slugify(text: str) -> str:
    """URL-friendly slug: lowercase alphanum and hyphens."""
    text = text.lower().replace(':', '-')
    return re.sub(r'[^a-z0-9-]+', '-', text).strip('-')


def front_matter(doc_id: str, title: str, slug: str, description: str, sidebar_position: int) -> str:
    return f"""---
id: {doc_id}
title: {title}
slug: /{slug}
sidebar_label: {title}
sidebar_position: {sidebar_position}
description: {description}
---

"""


def write_markdown(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_recipe_index(recipes):
    by_id = {}
    by_station = {}
    for rec in recipes:
        rid = rec['recipeId']
        rec_slug = slugify(rid)
        title = rid.replace('_', ' ').replace(':', ' ')
        key = rec['result']['itemId']
        by_id.setdefault(key, []).append((rec_slug, title))
        for inp in rec.get('requiredItems', {}):
            by_id.setdefault(inp, []).append((rec_slug, title))
        for inp in rec.get('requiredSpiritEssences', {}):
            by_id.setdefault(inp, []).append((rec_slug, title))
        station = rec.get('craftingStationTag', 'Unknown')
        by_station.setdefault(station, []).append((rec_slug, title))
    return by_id, by_station


def generate_items_page(by_id, by_station):
    items = load_json(DATA_DIR / PAGES['items'][0])
    md = front_matter('items', 'All Items', 'items', 'Comprehensive list of all items', sidebar_position=1)
    md += '# Items\n\n'
    for item in items:
        name = item['name']
        it_id = item['itemId']
        type_id = item.get('type', 0)

        md += f"## {name}\n"
        md += f"{item['description']}\n\n"
        # Correctly formatted admonition
        md += ":::info\n"
        md += f"**Type:** {fmt_enum('ItemType', type_id)}\n"
        md += ":::\n\n"

        # List recipes using this item
        used = by_id.get(it_id, [])
        if used:
            md += "**Used in Recipes:**\n"
            for rec_slug, rec_title in used:
                md += f"- [{rec_title}](/docs/recipes#{rec_slug})\n"
            md += "\n"
    write_markdown(PAGES['items'][1], md)


def generate_recipes_page(by_id, by_station):
    recipes = load_json(DATA_DIR / PAGES['recipes'][0])
    md = front_matter('recipes', 'All Recipes', 'recipes', 'Comprehensive list of all crafting recipes', sidebar_position=3)
    md += '# Recipes\n\n'
    for rec in recipes:
        rid = rec['recipeId']
        rec_slug = slugify(rid)
        title = rid.replace('_', ' ').replace(':', ' ')
        md += f"## {title}\n"
        res = rec['result']
        result_id = res['itemId']
        label = result_id.replace('_', ' ').title()
        md += f"- **Result:** [{label}](/docs/items#{slugify(result_id)}) x{res['count']}\n"
        if rec.get('requiredSpiritEssences'):
            md += "- **Spirit Essences:**\n"
            for ess, qty in rec['requiredSpiritEssences'].items():
                md += f"  - [{ess.replace('_',' ').title()}](/docs/spirit-essences#{slugify(ess)}) x{qty}\n"
        if rec.get('requiredItems'):
            md += "- **Items:**\n"
            for itm, qty in rec['requiredItems'].items():
                md += f"  - [{itm.replace('_',' ').title()}](/docs/items#{slugify(itm)}) x{qty}\n"
        station = rec.get('craftingStationTag', 'None')
        md += f"- **Crafting Station:** [{station}](/docs/crafting-stations#{slugify(station)})\n\n"
    write_markdown(PAGES['recipes'][1], md)


def generate_spiritessences_page(by_id, by_station):
    essences = load_json(DATA_DIR / PAGES['spiritessence'][0])
    md = front_matter('spirit-essences', 'All Spirit Essences', 'spirit-essences', 'Comprehensive list of all spirit essences', sidebar_position=2)
    md += '# Spirit Essences\n\n'
    for ess in essences:
        name = ess['name']
        eid = ess['essenceId']
        md += f"## {name}\n"
        md += f"{ess['description']}\n\n"
        st_id = ess.get('spiritType', 0)
        tier_id = ess.get('spiritTier', 0)
        md += f":::info **Type**  \n{fmt_enum('SpiritType', st_id)}  \n:::\n\n"
        md += f":::tip **Tier**  \n{fmt_enum('SpiritTier', tier_id)}  \n:::\n\n"
        md += "**Properties:**\n"
        for prop, val in ess.get('spiritProperties', {}).items():
            md += f"- {prop.title()}: x{val}\n"
        used = by_id.get(eid, [])
        if used:
            md += "\n**Used in Recipes:**\n"
            for rec_slug, rec_title in used:
                md += f"- [{rec_title}](/docs/recipes#{rec_slug})\n"
        md += "\n"
    write_markdown(PAGES['spiritessence'][1], md)


def generate_stations_page(by_id, by_station):
    md = front_matter('crafting-stations', 'All Crafting Stations', 'crafting-stations', 'List of crafting stations and available recipes', sidebar_position=4)
    md += '# Crafting Stations\n\n'
    for station, recs in by_station.items():
        md += f"## {station}\n"
        md += "List of recipes available at this station:\n"
        for rec_slug, rec_title in recs:
            md += f"- [{rec_title}](/docs/recipes#{rec_slug})\n"
        md += "\n"
    write_markdown(PAGES['stations'][1], md)


def main():
    recipes = load_json(DATA_DIR / PAGES['recipes'][0])
    by_id, by_station = generate_recipe_index(recipes)
    generate_items_page(by_id, by_station)
    generate_recipes_page(by_id, by_station)
    generate_spiritessences_page(by_id, by_station)
    generate_stations_page(by_id, by_station)
    print('All combined Markdown pages generated.')


if __name__ == '__main__':
    main()