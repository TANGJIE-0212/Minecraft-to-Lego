"""
converter.py - Minecraft schematic to LEGO brick list
Supports: .schematic (pre-1.13), .schem (WorldEdit 1.13+), .litematic
"""
import io
from collections import Counter, defaultdict
from dataclasses import dataclass

try:
    import nbtlib
    NBT_AVAILABLE = True
except ImportError:
    NBT_AVAILABLE = False

# ── LEGO Color Palette (ldraw_id, name, RGB) ──
LEGO_COLORS = [
    (1,"Blue",(0,87,168)),(2,"Green",(35,120,52)),(3,"Dark Turquoise",(0,143,155)),
    (4,"Red",(196,40,28)),(6,"Brown",(106,44,6)),(7,"Light Gray",(156,156,156)),
    (8,"Dark Gray",(99,95,82)),(9,"Light Blue",(180,210,228)),(10,"Bright Green",(75,151,75)),
    (14,"Yellow",(245,205,48)),(15,"White",(255,255,255)),(19,"Tan",(228,205,158)),
    (25,"Earth Orange",(196,112,38)),(26,"Black",(33,33,33)),(27,"Dark Green",(0,69,26)),
    (28,"Dark Brown",(77,47,28)),(29,"Salmon",(249,167,119)),(36,"Bright Orange",(255,126,20)),
    (37,"Bright Lime",(165,202,24)),(38,"Dark Orange",(169,85,0)),(39,"Very Light Gray",(214,214,214)),
    (40,"Trans-Clear",(252,252,252)),(41,"Trans-Red",(201,26,9)),(43,"Trans-Light Blue",(174,239,236)),
    (44,"Trans-Yellow",(245,205,48)),(45,"Trans-Dark Blue",(0,32,160)),(46,"Trans-Orange",(255,128,13)),
    (47,"Trans-Bright Green",(0,187,40)),(69,"Bright Purple",(129,0,123)),(70,"Dark Red",(114,14,15)),
    (71,"Light Bluish Gray",(175,181,199)),(72,"Dark Bluish Gray",(89,93,96)),
    (73,"Medium Blue",(115,150,200)),(74,"Medium Green",(127,196,117)),(77,"Light Pink",(254,204,207)),
    (85,"Dark Purple",(82,0,115)),(86,"Dark Flesh",(126,96,55)),(92,"Nougat",(213,144,52)),
    (100,"Light Salmon",(254,186,163)),(110,"Violet",(67,84,163)),(112,"Medium Violet",(110,104,187)),
    (115,"Medium Lime",(199,210,60)),(118,"Aqua",(177,227,227)),(124,"Dark Pink",(203,97,140)),
    (135,"Sand Blue",(112,130,160)),(138,"Sand Yellow",(186,169,119)),(140,"Earth Blue",(0,32,96)),
    (141,"Earth Green",(0,69,26)),(151,"Sand Green",(120,144,130)),(191,"Flame Yellowish Orange",(252,172,0)),
    (216,"Rust",(180,76,13)),(226,"Cool Yellow",(253,234,141)),(272,"Dark Blue",(0,32,96)),
    (288,"Dark Green",(39,70,45)),(297,"Pearl Gold",(170,127,46)),(308,"Dark Brown",(53,33,0)),
    (320,"Dark Red",(114,14,15)),(321,"Dark Azure",(70,155,195)),(322,"Medium Azure",(104,195,226)),
    (323,"Light Aqua",(211,242,234)),(324,"Lavender",(205,164,222)),(325,"Medium Lavender",(169,142,214)),
    (330,"Olive Green",(119,119,78)),(335,"Sand Red",(188,127,114)),(351,"Medium Dark Pink",(247,133,177)),
    (353,"Coral",(255,109,98)),(366,"Dust Orange",(224,143,78)),(373,"Sand Purple",(135,124,144)),
    (378,"Sand Green",(114,143,112)),(379,"Sand Blue",(112,130,157)),
]

AIR_BLOCKS = {"air","cave_air","void_air","water","lava"}

ROTATION_MATRICES = [
    (1,0,0, 0,1,0, 0,0,1),
    (0,0,1, 0,1,0, -1,0,0),
    (-1,0,0, 0,1,0, 0,0,-1),
    (0,0,-1, 0,1,0, 1,0,0),
]
STAIR_FACING_ROT = {"north": 0, "west": 1, "south": 2, "east": 3}
LEGACY_STAIR_FACING = ["east", "west", "south", "north"]

MC_BLOCK_MAP = {
    "stone":(72,"brick"),"cobblestone":(8,"brick"),"stone_bricks":(71,"brick"),
    "cracked_stone_bricks":(8,"brick"),"mossy_stone_bricks":(151,"brick"),
    "smooth_stone":(7,"brick"),"polished_granite":(86,"brick"),"granite":(25,"brick"),
    "diorite":(7,"brick"),"polished_diorite":(15,"brick"),"andesite":(72,"brick"),
    "polished_andesite":(8,"brick"),"deepslate":(72,"brick"),"deepslate_bricks":(8,"brick"),
    "cobbled_deepslate":(8,"brick"),"calcite":(15,"brick"),"tuff":(72,"brick"),
    "bedrock":(26,"brick"),"gravel":(8,"brick"),"sand":(19,"brick"),
    "sandstone":(19,"brick"),"smooth_sandstone":(138,"brick"),"red_sandstone":(25,"brick"),
    "dirt":(86,"brick"),"coarse_dirt":(28,"brick"),"podzol":(28,"brick"),
    "mud":(28,"brick"),"clay":(8,"brick"),"grass_block":(37,"brick"),
    "mycelium":(85,"brick"),
    "oak_planks":(19,"brick"),"oak_log":(86,"brick"),"oak_wood":(86,"brick"),
    "stripped_oak_log":(19,"brick"),"spruce_planks":(28,"brick"),"spruce_log":(28,"brick"),
    "birch_planks":(15,"brick"),"birch_log":(19,"brick"),"jungle_planks":(92,"brick"),
    "jungle_log":(86,"brick"),"acacia_planks":(25,"brick"),"acacia_log":(28,"brick"),
    "dark_oak_planks":(28,"brick"),"dark_oak_log":(26,"brick"),
    "mangrove_planks":(4,"brick"),"cherry_planks":(29,"brick"),"bamboo_planks":(14,"brick"),
    "crimson_planks":(4,"brick"),"warped_planks":(3,"brick"),
    "white_wool":(15,"brick"),"orange_wool":(36,"brick"),"magenta_wool":(124,"brick"),
    "light_blue_wool":(9,"brick"),"yellow_wool":(14,"brick"),"lime_wool":(37,"brick"),
    "pink_wool":(77,"brick"),"gray_wool":(72,"brick"),"light_gray_wool":(7,"brick"),
    "cyan_wool":(3,"brick"),"purple_wool":(85,"brick"),"blue_wool":(1,"brick"),
    "brown_wool":(6,"brick"),"green_wool":(2,"brick"),"red_wool":(4,"brick"),
    "black_wool":(26,"brick"),
    "white_concrete":(15,"brick"),"orange_concrete":(36,"brick"),"magenta_concrete":(69,"brick"),
    "light_blue_concrete":(9,"brick"),"yellow_concrete":(14,"brick"),"lime_concrete":(37,"brick"),
    "pink_concrete":(77,"brick"),"gray_concrete":(72,"brick"),"light_gray_concrete":(7,"brick"),
    "cyan_concrete":(3,"brick"),"purple_concrete":(85,"brick"),"blue_concrete":(1,"brick"),
    "brown_concrete":(6,"brick"),"green_concrete":(2,"brick"),"red_concrete":(4,"brick"),
    "black_concrete":(26,"brick"),
    "terracotta":(86,"brick"),"white_terracotta":(15,"brick"),"orange_terracotta":(25,"brick"),
    "magenta_terracotta":(124,"brick"),"light_blue_terracotta":(73,"brick"),
    "yellow_terracotta":(226,"brick"),"lime_terracotta":(115,"brick"),
    "pink_terracotta":(100,"brick"),"gray_terracotta":(8,"brick"),
    "light_gray_terracotta":(7,"brick"),"cyan_terracotta":(378,"brick"),
    "purple_terracotta":(373,"brick"),"blue_terracotta":(379,"brick"),
    "brown_terracotta":(335,"brick"),"green_terracotta":(141,"brick"),
    "red_terracotta":(335,"brick"),"black_terracotta":(26,"brick"),
    "glass":(40,"brick"),"glass_pane":(40,"plate"),
    "white_stained_glass":(40,"brick"),"orange_stained_glass":(46,"brick"),
    "light_blue_stained_glass":(43,"brick"),"yellow_stained_glass":(44,"brick"),
    "lime_stained_glass":(47,"brick"),"cyan_stained_glass":(43,"brick"),
    "blue_stained_glass":(45,"brick"),"red_stained_glass":(41,"brick"),
    "coal_ore":(26,"brick"),"iron_ore":(86,"brick"),"copper_ore":(25,"brick"),
    "gold_ore":(14,"brick"),"redstone_ore":(4,"brick"),"emerald_ore":(2,"brick"),
    "lapis_ore":(1,"brick"),"diamond_ore":(9,"brick"),
    "iron_block":(7,"brick"),"gold_block":(14,"brick"),"diamond_block":(9,"brick"),
    "emerald_block":(2,"brick"),"lapis_block":(1,"brick"),"redstone_block":(4,"brick"),
    "copper_block":(25,"brick"),"netherite_block":(26,"brick"),
    "netherrack":(4,"brick"),"nether_bricks":(26,"brick"),"red_nether_bricks":(4,"brick"),
    "soul_sand":(28,"brick"),"basalt":(72,"brick"),"blackstone":(26,"brick"),
    "quartz_block":(15,"brick"),"smooth_quartz":(15,"brick"),"glowstone":(14,"brick"),
    "shroomlight":(14,"brick"),"magma_block":(4,"brick"),
    "end_stone":(226,"brick"),"end_stone_bricks":(226,"brick"),
    "purpur_block":(112,"brick"),"obsidian":(26,"brick"),"crying_obsidian":(85,"brick"),
    "bricks":(4,"brick"),"bookshelf":(19,"brick"),"prismarine":(3,"brick"),
    "prismarine_bricks":(9,"brick"),"dark_prismarine":(27,"brick"),
    "sea_lantern":(40,"brick"),"hay_block":(14,"brick"),"honeycomb_block":(36,"brick"),
    "amethyst_block":(85,"brick"),"snow_block":(15,"brick"),
    "ice":(9,"brick"),"packed_ice":(9,"brick"),"blue_ice":(1,"brick"),
    "oak_stairs":(19,"slope"),"spruce_stairs":(28,"slope"),"birch_stairs":(15,"slope"),
    "jungle_stairs":(92,"slope"),"acacia_stairs":(25,"slope"),"dark_oak_stairs":(28,"slope"),
    "stone_stairs":(72,"slope"),"cobblestone_stairs":(8,"slope"),
    "stone_brick_stairs":(71,"slope"),"sandstone_stairs":(19,"slope"),
    "quartz_stairs":(15,"slope"),"brick_stairs":(4,"slope"),
    "nether_brick_stairs":(26,"slope"),"purpur_stairs":(112,"slope"),
    "oak_slab":(19,"plate"),"spruce_slab":(28,"plate"),"birch_slab":(15,"plate"),
    "stone_slab":(72,"plate"),"cobblestone_slab":(8,"plate"),
    "stone_brick_slab":(71,"plate"),"sandstone_slab":(19,"plate"),
    "quartz_slab":(15,"plate"),"brick_slab":(4,"plate"),
    "jungle_slab":(92,"plate"),"acacia_slab":(25,"plate"),"dark_oak_slab":(28,"plate"),
    "mangrove_slab":(4,"plate"),"cherry_slab":(29,"plate"),"bamboo_slab":(14,"plate"),
    "crimson_slab":(4,"plate"),"warped_slab":(3,"plate"),
    "smooth_stone_slab":(7,"plate"),"smooth_sandstone_slab":(138,"plate"),
    "red_sandstone_slab":(25,"plate"),"nether_brick_slab":(26,"plate"),
    "purpur_slab":(112,"plate"),"prismarine_slab":(3,"plate"),
    "prismarine_brick_slab":(9,"plate"),"dark_prismarine_slab":(27,"plate"),
    "deepslate_brick_slab":(8,"plate"),"cobbled_deepslate_slab":(8,"plate"),
    "polished_deepslate_slab":(72,"plate"),"blackstone_slab":(26,"plate"),
    "polished_blackstone_slab":(26,"plate"),"polished_blackstone_brick_slab":(26,"plate"),
    "end_stone_brick_slab":(226,"plate"),"mossy_stone_brick_slab":(151,"plate"),
    "mossy_cobblestone_slab":(151,"plate"),"andesite_slab":(72,"plate"),
    "granite_slab":(25,"plate"),"diorite_slab":(7,"plate"),
    "polished_andesite_slab":(8,"plate"),"polished_granite_slab":(86,"plate"),
    "polished_diorite_slab":(15,"plate"),"red_nether_brick_slab":(4,"plate"),
    "mangrove_stairs":(4,"slope"),"cherry_stairs":(29,"slope"),"bamboo_stairs":(14,"slope"),
    "crimson_stairs":(4,"slope"),"warped_stairs":(3,"slope"),
    "smooth_sandstone_stairs":(138,"slope"),"red_sandstone_stairs":(25,"slope"),
    "prismarine_stairs":(3,"slope"),"prismarine_brick_stairs":(9,"slope"),
    "dark_prismarine_stairs":(27,"slope"),"deepslate_brick_stairs":(8,"slope"),
    "cobbled_deepslate_stairs":(8,"slope"),"polished_deepslate_stairs":(72,"slope"),
    "blackstone_stairs":(26,"slope"),"polished_blackstone_stairs":(26,"slope"),
    "polished_blackstone_brick_stairs":(26,"slope"),"end_stone_brick_stairs":(226,"slope"),
    "mossy_stone_brick_stairs":(151,"slope"),"mossy_cobblestone_stairs":(151,"slope"),
    "andesite_stairs":(72,"slope"),"granite_stairs":(25,"slope"),"diorite_stairs":(7,"slope"),
    "polished_andesite_stairs":(8,"slope"),"polished_granite_stairs":(86,"slope"),
    "polished_diorite_stairs":(15,"slope"),"red_nether_brick_stairs":(4,"slope"),
    "oak_leaves":(37,"plate"),"spruce_leaves":(2,"plate"),"birch_leaves":(10,"plate"),
    "jungle_leaves":(2,"plate"),"acacia_leaves":(37,"plate"),"dark_oak_leaves":(2,"plate"),
    "mangrove_leaves":(2,"plate"),"cherry_leaves":(29,"plate"),
}

# ── LDraw → BrickLink color ID mapping ──
LDRAW_TO_BL = {
    1:7, 2:6, 3:39, 4:5, 6:8, 7:9, 8:10, 9:62, 10:36, 14:3, 15:1,
    19:2, 25:91, 26:11, 27:80, 28:120, 29:27, 36:4, 37:34, 38:68,
    39:49, 40:12, 41:17, 43:15, 44:19, 45:14, 46:98, 47:20,
    69:71, 70:59, 71:86, 72:85, 73:42, 74:37, 77:56, 85:89,
    86:91, 92:28, 100:26, 110:43, 112:73, 115:76, 118:152,
    124:104, 135:55, 138:69, 140:63, 141:80, 151:48,
    191:110, 216:27, 226:103, 272:63, 288:80, 297:115,
    308:120, 320:59, 321:153, 322:156, 323:152, 324:154,
    325:157, 330:155, 335:58, 351:23, 353:220, 366:68,
    373:54, 378:48, 379:55,
}

# Fast lookup tables
LEGO_COLOR_RGB  = {c[0]: c[2] for c in LEGO_COLORS}
LEGO_COLOR_NAME = {c[0]: c[1] for c in LEGO_COLORS}

# ── LEGO brick part catalog ──
# type → (w, l) → (part_id, name)
BRICK_CATALOG = {
    "brick": {
        (1,1):("3005","Brick 1x1"),(1,2):("3004","Brick 1x2"),
        (1,3):("3622","Brick 1x3"),(1,4):("3010","Brick 1x4"),
        (1,6):("3009","Brick 1x6"),(1,8):("3008","Brick 1x8"),
        (2,2):("3003","Brick 2x2"),(2,3):("3002","Brick 2x3"),
        (2,4):("3001","Brick 2x4"),(2,6):("2456","Brick 2x6"),
        (2,8):("3007","Brick 2x8"),(2,10):("3006","Brick 2x10"),
    },
    "plate": {
        (1,1):("3024","Plate 1x1"),(1,2):("3023","Plate 1x2"),
        (1,3):("3623","Plate 1x3"),(1,4):("3710","Plate 1x4"),
        (1,6):("3666","Plate 1x6"),(1,8):("3460","Plate 1x8"),
        (2,2):("3022","Plate 2x2"),(2,3):("3021","Plate 2x3"),
        (2,4):("3020","Plate 2x4"),(2,6):("3795","Plate 2x6"),
        (2,8):("3034","Plate 2x8"),(2,10):("3832","Plate 2x10"),
    },
    "slope": {
        (1,1):("54200","Slope 1x1x2/3"),(1,2):("3040","Slope 45 2x1"),
        (2,2):("3039","Slope 45 2x2"),(2,3):("3038","Slope 45 2x3"),
        (2,4):("3037","Slope 45 2x4"),
    },
}

def _get_part_info(brick_type, w, l):
    cat = BRICK_CATALOG.get(brick_type, BRICK_CATALOG["brick"])
    key = (min(w, l), max(w, l))
    if key in cat:
        return cat[key]
    return cat.get((1, 1), ("3005", "Brick 1x1"))

# ── Legacy MC block IDs (.schematic format) ──
MC_LEGACY_IDS = {
    0:"air",1:"stone",2:"grass_block",3:"dirt",4:"cobblestone",
    5:"oak_planks",7:"bedrock",8:"water",9:"water",10:"lava",11:"lava",
    12:"sand",13:"gravel",14:"gold_ore",15:"iron_ore",16:"coal_ore",
    17:"oak_log",18:"oak_leaves",20:"glass",21:"lapis_ore",22:"lapis_block",
    24:"sandstone",35:"white_wool",41:"gold_block",42:"iron_block",
    43:"stone_slab",44:"stone_slab",45:"bricks",47:"bookshelf",
    48:"mossy_stone_bricks",49:"obsidian",53:"oak_stairs",
    56:"diamond_ore",57:"diamond_block",67:"cobblestone_stairs",
    79:"ice",80:"snow_block",82:"clay",87:"netherrack",89:"glowstone",
    98:"stone_bricks",108:"brick_stairs",109:"stone_brick_stairs",
    112:"nether_bricks",114:"nether_brick_stairs",121:"end_stone",
    125:"oak_planks",126:"oak_slab",128:"sandstone_stairs",
    129:"emerald_ore",133:"emerald_block",134:"spruce_stairs",
    135:"birch_stairs",136:"jungle_stairs",152:"redstone_block",
    155:"quartz_block",156:"quartz_stairs",159:"terracotta",
    170:"hay_block",172:"terracotta",174:"packed_ice",
    179:"red_sandstone",201:"purpur_block",203:"purpur_stairs",
    206:"end_stone_bricks",251:"white_concrete",
}

COLOR_NAMES = [
    "white","orange","magenta","light_blue","yellow","lime",
    "pink","gray","light_gray","cyan","purple","blue",
    "brown","green","red","black",
]

COLORED_BLOCK_IDS = {
    35:"{}_wool", 95:"{}_stained_glass", 159:"{}_terracotta",
    160:"{}_stained_glass", 251:"{}_concrete",
}

# RGB values for fallback color matching
MC_BLOCK_RGB = {
    "stone":(125,125,125),"cobblestone":(127,127,127),"dirt":(134,96,67),
    "grass_block":(127,178,56),"sand":(219,207,163),"gravel":(136,126,126),
    "oak_planks":(162,130,78),"spruce_planks":(114,84,48),
    "birch_planks":(192,175,121),"oak_log":(109,85,50),
    "stone_bricks":(122,122,122),"bricks":(151,97,83),
    "obsidian":(20,18,29),"netherrack":(97,38,38),
    "quartz_block":(235,229,222),"iron_block":(220,220,220),
    "gold_block":(249,236,79),"diamond_block":(98,219,214),
    "emerald_block":(0,166,53),"lapis_block":(31,67,140),
    "redstone_block":(171,27,6),"snow_block":(249,255,254),
    "ice":(145,190,230),"clay":(161,166,179),"bedrock":(85,85,85),
    "sandstone":(216,202,155),
}


# ═══════════════════════════════════════════════════════
#  Parsing Functions
# ═══════════════════════════════════════════════════════

import gzip
import struct
import uuid
import math

def load_nbt(data: bytes, byteorder: str = "big"):
    """Parse NBT data from raw bytes."""
    if not NBT_AVAILABLE:
        raise ImportError("nbtlib is required. Install with: pip install nbtlib")
    try:
        buf = gzip.decompress(data)
    except Exception:
        buf = data
    return nbtlib.File.parse(io.BytesIO(buf), byteorder=byteorder)


def _read_varint(data, offset):
    """Read a protocol-buffer style varint."""
    result = 0
    shift = 0
    while offset < len(data):
        b = data[offset] & 0xFF
        offset += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, offset


def parse_schem(nbt_data):
    """Parse Sponge Schematic (.schem) → (width, height, length, blocks_dict)."""
    root = nbt_data
    if 'Schematic' in root:
        root = root['Schematic']

    width  = int(root['Width'])
    height = int(root['Height'])
    length = int(root['Length'])

    # Palette & block data can live at root or under a Blocks sub-compound
    if 'Blocks' in root and hasattr(root['Blocks'], 'keys'):
        blk = root['Blocks']
        palette_tag = blk.get('Palette', {})
        raw_data    = blk.get('Data', blk.get('BlockData', []))
    else:
        palette_tag = root.get('Palette', {})
        raw_data    = root.get('BlockData', [])

    palette = {int(idx): str(name) for name, idx in palette_tag.items()}
    raw = bytes(raw_data)

    blocks = {}
    offset = 0
    for y in range(height):
        for z in range(length):
            for x in range(width):
                if offset >= len(raw):
                    break
                bid, offset = _read_varint(raw, offset)
                name = palette.get(bid, "air")
                norm = normalize_block_name(name)
                if norm not in AIR_BLOCKS:
                    blocks[(x, y, z)] = name
    return width, height, length, blocks


def parse_schematic(nbt_data):
    """Parse MCEdit Schematic (.schematic) → (w, h, l, blocks)."""
    root = nbt_data
    if 'Schematic' in root:
        root = root['Schematic']

    width  = int(root['Width'])
    height = int(root['Height'])
    length = int(root['Length'])

    block_ids  = list(root['Blocks'])
    block_data = list(root.get('Data', [0] * len(block_ids)))

    blocks = {}
    for y in range(height):
        for z in range(length):
            for x in range(width):
                idx = (y * length + z) * width + x
                if idx >= len(block_ids):
                    break
                bid   = block_ids[idx] & 0xFF
                bdata = block_data[idx] & 0x0F if idx < len(block_data) else 0

                if bid == 0:
                    continue
                if bid in COLORED_BLOCK_IDS:
                    name = COLORED_BLOCK_IDS[bid].format(COLOR_NAMES[bdata & 0x0F])
                elif bid in MC_LEGACY_IDS:
                    name = MC_LEGACY_IDS[bid]
                else:
                    name = f"unknown_{bid}"
                if name.endswith('_stairs'):
                    facing = LEGACY_STAIR_FACING[bdata & 0x3]
                    half = 'top' if (bdata & 0x4) else 'bottom'
                    name = f'{name}[facing={facing},half={half},shape=straight]'
                blocks[(x, y, z)] = name
    return width, height, length, blocks


def _block_state_name(entry, bedrock=False):
    if not hasattr(entry, 'keys'):
        return str(entry)
    name = str(entry.get('name' if bedrock else 'Name', 'air'))
    props = entry.get('states' if bedrock else 'Properties', {})
    if not hasattr(props, 'items') or not props:
        return name
    if bedrock and name.endswith('_stairs'):
        direction = int(props.get('weirdo_direction', 3))
        facing = LEGACY_STAIR_FACING[direction & 0x3]
        half = 'top' if int(props.get('upside_down_bit', 0)) else 'bottom'
        return f'{name}[facing={facing},half={half},shape=straight]'
    values = ','.join(f'{key}={value}' for key, value in props.items())
    return f'{name}[{values}]' if values else name


def _normalize_sparse_blocks(blocks):
    if not blocks:
        return 0, 0, 0, {}
    min_x = min(pos[0] for pos in blocks)
    min_y = min(pos[1] for pos in blocks)
    min_z = min(pos[2] for pos in blocks)
    max_x = max(pos[0] for pos in blocks)
    max_y = max(pos[1] for pos in blocks)
    max_z = max(pos[2] for pos in blocks)
    normalized = {
        (x - min_x, y - min_y, z - min_z): name
        for (x, y, z), name in blocks.items()
    }
    return max_x - min_x + 1, max_y - min_y + 1, max_z - min_z + 1, normalized


def parse_structure_nbt(nbt_data):
    """Parse a Java Structure Block .nbt file."""
    size = nbt_data.get('size', [])
    palette = nbt_data.get('palette', [])
    entries = nbt_data.get('blocks', [])
    if len(size) != 3 or not palette:
        raise ValueError("Invalid Java structure NBT")
    palette_names = [_block_state_name(entry) for entry in palette]
    blocks = {}
    for entry in entries:
        pos = entry.get('pos', []) if hasattr(entry, 'get') else []
        state = int(entry.get('state', -1)) if hasattr(entry, 'get') else -1
        if len(pos) != 3 or state < 0 or state >= len(palette_names):
            continue
        name = palette_names[state]
        if normalize_block_name(name) not in AIR_BLOCKS:
            blocks[tuple(map(int, pos))] = name
    return _normalize_sparse_blocks(blocks)


def parse_mcstructure(nbt_data):
    """Parse a Bedrock Structure Block .mcstructure file."""
    size = nbt_data.get('size', [])
    structure = nbt_data.get('structure', {})
    palette = structure.get('palette', {}).get('default', {}).get('block_palette', [])
    index_layers = structure.get('block_indices', [])
    if len(size) != 3 or not palette or not index_layers:
        raise ValueError("Invalid Bedrock mcstructure")
    width, height, length = map(int, size)
    indices = list(map(int, index_layers[0]))
    palette_names = [_block_state_name(entry, bedrock=True) for entry in palette]
    blocks = {}
    for x in range(width):
        for y in range(height):
            for z in range(length):
                offset = (x * height + y) * length + z
                if offset >= len(indices):
                    continue
                state = indices[offset]
                if state < 0 or state >= len(palette_names):
                    continue
                name = palette_names[state]
                if normalize_block_name(name) not in AIR_BLOCKS:
                    blocks[(x, y, z)] = name
    return _normalize_sparse_blocks(blocks)


def parse_litematic(nbt_data):
    """Parse Litematica (.litematic) → (w, h, l, blocks)."""
    root    = nbt_data
    regions = root.get('Regions', {})

    all_blocks = {}
    min_c = [float('inf')] * 3
    max_c = [float('-inf')] * 3

    for _, region in regions.items():
        pos  = region.get('Position', {})
        size = region.get('Size', {})
        rx, ry, rz = int(pos.get('x', 0)), int(pos.get('y', 0)), int(pos.get('z', 0))
        sx, sy, sz = int(size.get('x', 0)), int(size.get('y', 0)), int(size.get('z', 0))

        ax, ay, az = abs(sx), abs(sy), abs(sz)
        ox = rx if sx >= 0 else rx + sx + 1
        oy = ry if sy >= 0 else ry + sy + 1
        oz = rz if sz >= 0 else rz + sz + 1

        palette      = region.get('BlockStatePalette', [])
        block_states = region.get('BlockStates', [])
        if len(palette) == 0 or len(block_states) == 0:
            continue

        total = ax * ay * az
        bits  = max(2, (len(palette) - 1).bit_length())
        epl   = 64 // bits          # entries per long
        mask  = (1 << bits) - 1

        longs = []
        for v in block_states:
            v = int(v)
            longs.append(v if v >= 0 else v + (1 << 64))

        for y in range(ay):
            for z in range(az):
                for x in range(ax):
                    i        = (y * az + z) * ax + x
                    long_idx = i // epl
                    bit_off  = (i % epl) * bits
                    if long_idx >= len(longs):
                        break
                    pidx = (longs[long_idx] >> bit_off) & mask
                    if pidx >= len(palette):
                        continue

                    bname = _block_state_name(palette[pidx])
                    if normalize_block_name(bname) in AIR_BLOCKS:
                        continue

                    wx, wy, wz = ox + x, oy + y, oz + z
                    all_blocks[(wx, wy, wz)] = bname
                    min_c = [min(min_c[0], wx), min(min_c[1], wy), min(min_c[2], wz)]
                    max_c = [max(max_c[0], wx), max(max_c[1], wy), max(max_c[2], wz)]

    if not all_blocks:
        return 0, 0, 0, {}

    norm = {(x - min_c[0], y - min_c[1], z - min_c[2]): n
            for (x, y, z), n in all_blocks.items()}
    return max_c[0] - min_c[0] + 1, max_c[1] - min_c[1] + 1, max_c[2] - min_c[2] + 1, norm


def parse_file(filename: str, data: bytes):
    """Auto-detect format and parse the schematic."""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    nbt_data = load_nbt(data, byteorder='little' if ext == 'mcstructure' else 'big')
    if ext == 'mcstructure':
        return parse_mcstructure(nbt_data)
    if ext == 'nbt':
        return parse_structure_nbt(nbt_data)
    if ext == 'litematic':
        return parse_litematic(nbt_data)
    if ext == 'schematic':
        return parse_schematic(nbt_data)
    # .schem – try sponge first, fall back
    try:
        return parse_schem(nbt_data)
    except (KeyError, TypeError):
        try:
            return parse_schematic(nbt_data)
        except (KeyError, TypeError):
            return parse_litematic(nbt_data)


# ═══════════════════════════════════════════════════════
#  Block → LEGO Mapping
# ═══════════════════════════════════════════════════════

def normalize_block_name(name: str) -> str:
    name = name.lower().strip()
    if ':' in name:
        name = name.split(':', 1)[1]
    if '[' in name:
        name = name.split('[', 1)[0]
    return name


def parse_block_state(name: str) -> dict:
    """Extract block state properties from a block name like 'oak_stairs[facing=east,half=bottom]'."""
    name = name.lower().strip()
    props = {}
    bracket_idx = name.find('[')
    if bracket_idx == -1:
        return props
    end = name.find(']', bracket_idx)
    inner = name[bracket_idx + 1: end if end != -1 else None]
    for pair in inner.split(','):
        parts = pair.split('=', 1)
        if len(parts) == 2:
            props[parts[0].strip()] = parts[1].strip()
    return props


def _color_dist_sq(c1, c2):
    dr, dg, db = c1[0] - c2[0], c1[1] - c2[1], c1[2] - c2[2]
    return 2 * dr * dr + 4 * dg * dg + 3 * db * db


def find_closest_lego_color(r, g, b):
    target = (r, g, b)
    best_id, best_d = 71, float('inf')
    for ldraw_id, _, rgb in LEGO_COLORS:
        d = _color_dist_sq(target, rgb)
        if d < best_d:
            best_d = d
            best_id = ldraw_id
    return best_id


def map_block_to_lego(block_name: str):
    """Map MC block → (ldraw_color_id, brick_type, rotation) or None."""
    name = normalize_block_name(block_name)
    if name in AIR_BLOCKS:
        return None
    mapped = None
    if name in MC_BLOCK_MAP:
        mapped = MC_BLOCK_MAP[name]
    elif name in MC_BLOCK_RGB:
        mapped = (find_closest_lego_color(*MC_BLOCK_RGB[name]), "brick")
    else:
        for sfx, btype in [("_stairs", "slope"), ("_slab", "plate"), ("_wall", "brick"),
                            ("_fence", "brick"), ("_door", "plate"), ("_trapdoor", "plate")]:
            if name.endswith(sfx):
                base = name[:-len(sfx)]
                for variant in (base, base + "_planks", base + "_block", base + "s"):
                    if variant in MC_BLOCK_MAP:
                        mapped = (MC_BLOCK_MAP[variant][0], btype)
                        break
                if mapped:
                    break
        if not mapped:
            mapped = (71, "brick")

    if name.endswith('_stairs') and mapped[1] == "slope":
        props = parse_block_state(block_name)
        if props.get('half', 'bottom') == 'top' or props.get('shape', 'straight') != 'straight':
            return (mapped[0], "brick", 0)
        return (mapped[0], "slope", STAIR_FACING_ROT.get(props.get('facing', 'north'), 0))
    return (mapped[0], mapped[1], 0)


# ═══════════════════════════════════════════════════════
#  Brick Optimization – Greedy Layer Merge
# ═══════════════════════════════════════════════════════

# Per-type merge sizes (largest first). Structural pieces (brick/plate) use
# common, easy-to-buy LEGO sizes up to 2x10; slopes only use real slope parts.
# Wider (2-stud) pieces are preferred before long 1-stud pieces for stability.
MERGE_SIZES_BY_TYPE = {
    "brick": [(2,10),(2,8),(2,6),(2,4),(2,3),(2,2),(1,8),(1,6),(1,4),(1,3),(1,2),(1,1)],
    "plate": [(2,10),(2,8),(2,6),(2,4),(2,3),(2,2),(1,8),(1,6),(1,4),(1,3),(1,2),(1,1)],
    "slope": [(2,4),(2,3),(2,2),(1,2),(1,1)],
}

def _greedy_layer_plan(layer_cells, width, length, size_order, reverse_x=False, reverse_z=False):
    used = set()
    bricks = []
    positions = sorted(
        layer_cells,
        key=lambda pos: (-pos[0] if reverse_x else pos[0], -pos[1] if reverse_z else pos[1]),
    )
    x_step = -1 if reverse_x else 1
    z_step = -1 if reverse_z else 1

    for x, z in positions:
        if (x, z) in used:
            continue
        cid, btype, rot = layer_cells[(x, z)]
        if btype == "slope":
            used.add((x, z))
            bricks.append((x, z, 1, 1, cid, btype, rot))
            continue

        placed = False
        for mw, ml in size_order.get(btype, size_order["brick"]):
            if mw == 1 and ml == 1:
                break
            orientations = [(mw, ml)] if mw == ml else [(mw, ml), (ml, mw)]
            for w, l in orientations:
                cells = [
                    (x + dx * x_step, z + dz * z_step)
                    for dx in range(w)
                    for dz in range(l)
                ]
                if any(px < 0 or px >= width or pz < 0 or pz >= length for px, pz in cells):
                    continue
                if any(
                    pos in used
                    or pos not in layer_cells
                    or layer_cells[pos][:2] != (cid, btype)
                    for pos in cells
                ):
                    continue
                used.update(cells)
                bricks.append((
                    min(px for px, _ in cells), min(pz for _, pz in cells),
                    w, l, cid, btype, rot,
                ))
                placed = True
                break
            if placed:
                break

        if not placed:
            used.add((x, z))
            bricks.append((x, z, 1, 1, cid, btype, rot))
    return bricks


def _staggered_layer_plan(layer_cells, width, length, phase):
    """Preserve the deployed running-bond plan as an optimization candidate."""
    used = set()
    bricks = []
    for x, z in sorted(layer_cells):
        if (x, z) in used:
            continue
        cid, btype, rot = layer_cells[(x, z)]
        if btype == "slope":
            used.add((x, z))
            bricks.append((x, z, 1, 1, cid, btype, rot))
            continue
        left = layer_cells.get((x - 1, z))
        behind = layer_cells.get((x, z - 1))
        cap_w = 3 if phase and (not left or left[:2] != (cid, btype)) else None
        cap_l = 3 if phase and (not behind or behind[:2] != (cid, btype)) else None
        placed = False
        for mw, ml in MERGE_SIZES_BY_TYPE.get(btype, MERGE_SIZES_BY_TYPE["brick"]):
            if mw == 1 and ml == 1:
                break
            orientations = [(mw, ml)] if mw == ml else [(mw, ml), (ml, mw)]
            for w, l in orientations:
                if (cap_w is not None and w > cap_w) or (cap_l is not None and l > cap_l):
                    continue
                cells = [(x + dx, z + dz) for dx in range(w) for dz in range(l)]
                if (
                    x + w > width
                    or z + l > length
                    or any(
                        pos in used
                        or pos not in layer_cells
                        or layer_cells[pos][:2] != (cid, btype)
                        for pos in cells
                    )
                ):
                    continue
                used.update(cells)
                bricks.append((x, z, w, l, cid, btype, rot))
                placed = True
                break
            if placed:
                break
        if not placed:
            used.add((x, z))
            bricks.append((x, z, 1, 1, cid, btype, rot))
    return bricks


def _brick_seams(bricks):
    occupancy = {}
    for index, (x, z, w, l, *_rest) in enumerate(bricks):
        for dx in range(w):
            for dz in range(l):
                occupancy[(x + dx, z + dz)] = index
    seams = set()
    for (x, z), index in occupancy.items():
        if (right := occupancy.get((x + 1, z))) is not None and right != index:
            seams.add(("x", x + 1, z))
        if (forward := occupancy.get((x, z + 1))) is not None and forward != index:
            seams.add(("z", x, z + 1))
    return seams


def _plan_score(bricks, previous_seams):
    one_by_one = sum(
        w == 1 and l == 1 and btype != "slope"
        for _x, _z, w, l, _cid, btype, _rot in bricks
    )
    aligned_seams = len(_brick_seams(bricks) & previous_seams)
    return len(bricks) + one_by_one * 10 + aligned_seams * 2


def _optimize_layer(layer_cells, width, length, previous_bricks=None, phase=0):
    """Choose a low-part plan while avoiding structural 1x1s and aligned seams."""
    previous_seams = _brick_seams(previous_bricks or [])
    size_orders = [MERGE_SIZES_BY_TYPE]
    for prefer_short in (True, False):
        order = {}
        for btype, sizes in MERGE_SIZES_BY_TYPE.items():
            non_unit = [size for size in sizes if size != (1, 1)]
            non_unit.sort(key=lambda size: (size[0] * size[1], size[0]), reverse=not prefer_short)
            order[btype] = non_unit + [(1, 1)]
        size_orders.append(order)
    plans = [
        _greedy_layer_plan(layer_cells, width, length, order, reverse_x, reverse_z)
        for order in size_orders
        for reverse_x, reverse_z in ((False, False), (True, False), (False, True), (True, True))
    ]
    plans.append(_staggered_layer_plan(layer_cells, width, length, phase))
    return min(plans, key=lambda plan: _plan_score(plan, previous_seams))


# ═══════════════════════════════════════════════════════
#  Output Generation
# ═══════════════════════════════════════════════════════

_LDR_PARTS = {
    ("brick",1,1):"3005.dat",("brick",1,2):"3004.dat",("brick",1,3):"3622.dat",
    ("brick",1,4):"3010.dat",("brick",1,6):"3009.dat",("brick",1,8):"3008.dat",
    ("brick",2,2):"3003.dat",("brick",2,3):"3002.dat",("brick",2,4):"3001.dat",
    ("brick",2,6):"2456.dat",("brick",2,8):"3007.dat",("brick",2,10):"3006.dat",
    ("plate",1,1):"3024.dat",("plate",1,2):"3023.dat",("plate",1,3):"3623.dat",
    ("plate",1,4):"3710.dat",("plate",1,6):"3666.dat",("plate",1,8):"3460.dat",
    ("plate",2,2):"3022.dat",("plate",2,3):"3021.dat",("plate",2,4):"3020.dat",
    ("plate",2,6):"3795.dat",("plate",2,8):"3034.dat",("plate",2,10):"3832.dat",
    ("slope",1,1):"54200.dat",("slope",1,2):"3040.dat",
    ("slope",2,2):"3039.dat",("slope",2,3):"3038.dat",("slope",2,4):"3037.dat",
}

def generate_ldr(bricks):
    """Generate LDraw (.ldr) file content."""
    lines = [
        "0 FILE brickcraft_model.ldr",
        "0 BrickCraft Converted Model",
        "0 Name: brickcraft_model.ldr",
        "0 Author: BrickCraft",
    ]
    for x, y, z, w, l, cid, btype, rot in bricks:
        lx = (x + (w - 1) / 2) * 20
        ly = -(y * 24)
        lz = (z + (l - 1) / 2) * 20
        part = _LDR_PARTS.get((btype, min(w, l), max(w, l)), "3005.dat")
        output_rot = rot if btype == "slope" else (1 if w > l else 0)
        matrix = ROTATION_MATRICES[output_rot]
        matrix_text = " ".join(map(str, matrix))
        lines.append(f"1 {cid} {lx} {ly} {lz} {matrix_text} {part}")
    lines.append("0")
    return "\n".join(lines)


def generate_bricklink_xml(parts_counter):
    """Generate BrickLink Wanted List XML."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<INVENTORY>"]
    for (part_id, cid, _name, _btype), count in parts_counter.items():
        bl_color = LDRAW_TO_BL.get(cid, 0)
        lines += [
            "  <ITEM>",
            "    <ITEMTYPE>P</ITEMTYPE>",
            f"    <ITEMID>{part_id}</ITEMID>",
            f"    <COLOR>{bl_color}</COLOR>",
            f"    <MINQTY>{count}</MINQTY>",
            "  </ITEM>",
        ]
    lines.append("</INVENTORY>")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
#  Main Conversion Pipeline
# ═══════════════════════════════════════════════════════

def convert_and_optimize(filename: str, data: bytes) -> dict:
    """Full pipeline: parse → map → optimize → output.
    Each MC block becomes one 1×1 LEGO cell, then same-color cells are merged
    into larger, commonly-stocked bricks/plates with brick-bond seam staggering.
    """

    # 1. Parse
    width, height, length, blocks = parse_file(filename, data)
    if not blocks:
        return {"error": "No blocks found. File may be empty or unsupported.", "total_blocks": 0}

    # 2. Map to LEGO
    lego_blocks = {}
    for pos, bname in blocks.items():
        m = map_block_to_lego(bname)
        if m:
            lego_blocks[pos] = m

    # 3. Build brick list
    all_bricks = []   # (x, y, z, w, l, color_id, brick_type, rotation)

    # Optimize layer by layer and compare seams with the layer below.
    previous_layer_bricks = []
    for y in range(height):
        layer = {(bx, bz): val for (bx, by, bz), val in lego_blocks.items() if by == y}
        if layer:
            layer_bricks = _optimize_layer(layer, width, length, previous_layer_bricks, phase=y % 2)
            for (bx, bz, w, l, cid, bt, rot) in layer_bricks:
                all_bricks.append((bx, y, bz, w, l, cid, bt, rot))
            previous_layer_bricks = layer_bricks
        else:
            previous_layer_bricks = []

    # 4. Statistics
    parts_counter = Counter()
    color_counter = Counter()
    for (x, y, z, w, l, cid, bt, _rot) in all_bricks:
        pid, pname = _get_part_info(bt, w, l)
        parts_counter[(pid, cid, pname, bt)] += 1
        color_counter[cid] += 1

    color_summary = [
        {"color_id": cid, "name": LEGO_COLOR_NAME.get(cid, f"#{cid}"),
         "rgb": list(LEGO_COLOR_RGB.get(cid, (128, 128, 128))), "count": cnt}
        for cid, cnt in color_counter.most_common()
    ]

    brick_summary = [
        {"part_id": pid, "part_name": pn, "brick_type": bt,
         "color_id": cid, "color_name": LEGO_COLOR_NAME.get(cid, ""),
         "rgb": list(LEGO_COLOR_RGB.get(cid, (128, 128, 128))), "count": cnt}
        for (pid, cid, pn, bt), cnt in parts_counter.most_common()
    ]

    # 5. 3D preview data (compact)
    palette_map = {}
    palette = []
    voxels = []
    for (x, y, z, w, l, cid, bt, _rot) in all_bricks:
        rgb = LEGO_COLOR_RGB.get(cid, (128, 128, 128))
        key = tuple(rgb)
        if key not in palette_map:
            palette_map[key] = len(palette)
            palette.append(list(rgb))
        h = 1 if bt == "plate" else (2 if bt == "slope" else 3)
        voxels.append([x, y * 3, z, w, h, l, palette_map[key]])

    # Cap preview data for very large models
    if len(voxels) > 60000:
        step = len(voxels) // 60000 + 1
        voxels = voxels[::step]

    # 6. File outputs
    ldr = generate_ldr(all_bricks)
    xml = generate_bricklink_xml(parts_counter)
    sid = uuid.uuid4().hex[:8]

    return {
        "session_id": sid,
        "dimensions": {"width": width, "height": height, "length": length},
        "total_blocks": len(blocks),
        "total_bricks": len(all_bricks),
        "unique_parts": len(parts_counter),

        "color_summary": color_summary,
        "brick_summary": brick_summary,
        "voxels": voxels,
        "palette": palette,
        "ldr_content": ldr,
        "bricklink_xml": xml,
    }
