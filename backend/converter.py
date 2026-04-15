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
        (2,2):("3003","Brick 2x2"),(2,3):("3002","Brick 2x3"),
        (2,4):("3001","Brick 2x4"),
    },
    "plate": {
        (1,1):("3024","Plate 1x1"),(1,2):("3023","Plate 1x2"),
        (1,3):("3623","Plate 1x3"),(1,4):("3710","Plate 1x4"),
        (2,2):("3022","Plate 2x2"),(2,3):("3021","Plate 2x3"),
        (2,4):("3020","Plate 2x4"),
    },
    "slope": {
        (1,1):("54200","Slope 1x1x2/3"),(1,2):("3040","Slope 45 2x1"),
        (2,2):("3039","Slope 45 2x2"),(2,4):("3037","Slope 45 2x4"),
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

def load_nbt(data: bytes):
    """Parse NBT data from raw bytes."""
    if not NBT_AVAILABLE:
        raise ImportError("nbtlib is required. Install with: pip install nbtlib")
    try:
        buf = gzip.decompress(data)
    except Exception:
        buf = data
    return nbtlib.File.parse(io.BytesIO(buf))


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
                blocks[(x, y, z)] = name
    return width, height, length, blocks


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
        if not palette or not block_states:
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

                    entry = palette[pidx]
                    bname = str(entry.get('Name', 'air')) if hasattr(entry, 'keys') else str(entry)
                    if 'air' in bname:
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
    nbt_data = load_nbt(data)
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
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
    """Map MC block → (ldraw_color_id, brick_type) or None."""
    name = normalize_block_name(block_name)
    if name in AIR_BLOCKS:
        return None
    if name in MC_BLOCK_MAP:
        return MC_BLOCK_MAP[name]
    # Fallback: match by known MC block color
    if name in MC_BLOCK_RGB:
        return (find_closest_lego_color(*MC_BLOCK_RGB[name]), "brick")
    # Try to derive from suffix
    for sfx, btype in [("_stairs", "slope"), ("_slab", "plate"), ("_wall", "brick"),
                        ("_fence", "brick"), ("_door", "plate"), ("_trapdoor", "plate")]:
        if name.endswith(sfx):
            base = name[:-len(sfx)]
            for v in (base, base + "_planks", base + "_block"):
                if v in MC_BLOCK_MAP:
                    return (MC_BLOCK_MAP[v][0], btype)
    return (71, "brick")   # fallback: light bluish gray brick


# ═══════════════════════════════════════════════════════
#  Brick Optimization – Greedy Layer Merge
# ═══════════════════════════════════════════════════════

MERGE_SIZES = [(2, 4), (2, 3), (2, 2), (1, 4), (1, 3), (1, 2), (1, 1)]

def _optimize_layer(layer_cells, width, length):
    """Merge same-color adjacent cells into larger bricks on one Y layer.
    layer_cells: {(x,z): (color_id, brick_type)}
    Returns [(x, z, w, l, color_id, brick_type), ...]
    """
    used   = set()
    bricks = []

    for (x, z) in sorted(layer_cells):
        if (x, z) in used:
            continue
        cid, btype = layer_cells[(x, z)]
        placed = False

        for mw, ml in MERGE_SIZES:
            if mw == 1 and ml == 1:
                break
            orientations = [(mw, ml)] if mw == ml else [(mw, ml), (ml, mw)]
            for w, l in orientations:
                if x + w > width or z + l > length:
                    continue
                ok = True
                for dx in range(w):
                    for dz in range(l):
                        p = (x + dx, z + dz)
                        if p in used or p not in layer_cells:
                            ok = False; break
                        if layer_cells[p] != (cid, btype):
                            ok = False; break
                    if not ok:
                        break
                if ok:
                    for dx in range(w):
                        for dz in range(l):
                            used.add((x + dx, z + dz))
                    bricks.append((x, z, w, l, cid, btype))
                    placed = True
                    break
            if placed:
                break

        if not placed:
            used.add((x, z))
            bricks.append((x, z, 1, 1, cid, btype))

    return bricks


# ═══════════════════════════════════════════════════════
#  Output Generation
# ═══════════════════════════════════════════════════════

_LDR_PARTS = {
    ("brick",1,1):"3005.dat",("brick",1,2):"3004.dat",("brick",1,3):"3622.dat",
    ("brick",1,4):"3010.dat",("brick",2,2):"3003.dat",("brick",2,3):"3002.dat",
    ("brick",2,4):"3001.dat",
    ("plate",1,1):"3024.dat",("plate",1,2):"3023.dat",("plate",1,3):"3623.dat",
    ("plate",1,4):"3710.dat",("plate",2,2):"3022.dat",("plate",2,3):"3021.dat",
    ("plate",2,4):"3020.dat",
    ("slope",1,1):"54200.dat",("slope",1,2):"3040.dat",("slope",2,2):"3039.dat",
}

def generate_ldr(bricks, scale="compact"):
    """Generate LDraw (.ldr) file content."""
    lines = [
        "0 FILE brickcraft_model.ldr",
        "0 BrickCraft Converted Model",
        "0 Name: brickcraft_model.ldr",
        "0 Author: BrickCraft",
    ]
    for x, y, z, w, l, cid, btype in bricks:
        if scale == "official":
            # Official scale: each MC block = 2×2 footprint, 5 plates tall
            # y encodes sub-layers: y%3==0 bottom plate, y%3==1 mid plate, y%3==2 top brick
            mc_y = y // 3
            sub = y % 3
            lx = x * 40
            lz = z * 40
            if sub == 2:
                ly = -(mc_y * 40)           # top brick
            elif sub == 1:
                ly = -(mc_y * 40) + 24      # middle plate
            else:
                ly = -(mc_y * 40) + 32      # bottom plate
        else:
            lx, ly, lz = x * 20, -(y * 24), z * 20
        part = _LDR_PARTS.get((btype, min(w, l), max(w, l)), "3005.dat")
        lines.append(f"1 {cid} {lx} {ly} {lz} 1 0 0 0 1 0 0 0 1 {part}")
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

def convert_and_optimize(filename: str, data: bytes, scale: str = "compact") -> dict:
    """Full pipeline: parse → map → optimize → output.
    scale: "compact" (1×1 brick per block) or "official" (2×2 brick + 2× 2×2 plates per block)
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
    all_bricks = []   # (x, y, z, w, l, color_id, brick_type)

    if scale == "official":
        # Official LEGO Minecraft scale: each MC block = 1× Brick 2×2 + 2× Plate 2×2
        # Creates a 16mm perfect cube (2 studs × 5 plates)
        for (bx, by, bz), (cid, _bt) in lego_blocks.items():
            all_bricks.append((bx, by * 3,     bz, 2, 2, cid, "plate"))
            all_bricks.append((bx, by * 3 + 1, bz, 2, 2, cid, "plate"))
            all_bricks.append((bx, by * 3 + 2, bz, 2, 2, cid, "brick"))
        all_bricks.sort(key=lambda b: (b[1], b[0], b[2]))
    else:
        # Compact mode: optimize layer by layer
        for y in range(height):
            layer = {(bx, bz): val for (bx, by, bz), val in lego_blocks.items() if by == y}
            if layer:
                for (bx, bz, w, l, cid, bt) in _optimize_layer(layer, width, length):
                    all_bricks.append((bx, y, bz, w, l, cid, bt))

    # 4. Statistics
    parts_counter = Counter()
    color_counter = Counter()
    for (x, y, z, w, l, cid, bt) in all_bricks:
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
    for (x, y, z, w, l, cid, bt) in all_bricks:
        rgb = LEGO_COLOR_RGB.get(cid, (128, 128, 128))
        key = tuple(rgb)
        if key not in palette_map:
            palette_map[key] = len(palette)
            palette.append(list(rgb))
        if scale == "official":
            # Render each MC block as a single 2×2×2 cube (only on sub-layer 0)
            if y % 3 == 0:
                mc_y = y // 3
                voxels.append([x * 2, mc_y * 2, z * 2, 2, 2, 2, palette_map[key]])
        else:
            h = 1 if bt == "plate" else (2 if bt == "slope" else 3)
            voxels.append([x, y * 3, z, w, h, l, palette_map[key]])

    # Cap preview data for very large models
    if len(voxels) > 60000:
        step = len(voxels) // 60000 + 1
        voxels = voxels[::step]

    # 6. File outputs
    ldr = generate_ldr(all_bricks, scale)
    xml = generate_bricklink_xml(parts_counter)
    sid = uuid.uuid4().hex[:8]

    return {
        "session_id": sid,
        "dimensions": {"width": width, "height": height, "length": length},
        "total_blocks": len(blocks),
        "total_bricks": len(all_bricks),
        "unique_parts": len(parts_counter),
        "scale": scale,

        "color_summary": color_summary,
        "brick_summary": brick_summary,
        "voxels": voxels,
        "palette": palette,
        "ldr_content": ldr,
        "bricklink_xml": xml,
    }
