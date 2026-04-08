import { read as readNbt } from "https://cdn.jsdelivr.net/npm/nbtify@2.2.0/+esm";
import { gunzipSync } from "https://cdn.jsdelivr.net/npm/fflate@0.8.2/esm/browser.js";

const LEGO_COLORS = [
  [1,"Blue",[0,87,168]],[2,"Green",[35,120,52]],[3,"Dark Turquoise",[0,143,155]],[4,"Red",[196,40,28]],[6,"Brown",[106,44,6]],[7,"Light Gray",[156,156,156]],[8,"Dark Gray",[99,95,82]],[9,"Light Blue",[180,210,228]],[10,"Bright Green",[75,151,75]],[14,"Yellow",[245,205,48]],[15,"White",[255,255,255]],[19,"Tan",[228,205,158]],[25,"Earth Orange",[196,112,38]],[26,"Black",[33,33,33]],[27,"Dark Green",[0,69,26]],[28,"Dark Brown",[77,47,28]],[29,"Salmon",[249,167,119]],[36,"Bright Orange",[255,126,20]],[37,"Bright Lime",[165,202,24]],[38,"Dark Orange",[169,85,0]],[39,"Very Light Gray",[214,214,214]],[40,"Trans-Clear",[252,252,252]],[41,"Trans-Red",[201,26,9]],[43,"Trans-Light Blue",[174,239,236]],[44,"Trans-Yellow",[245,205,48]],[45,"Trans-Dark Blue",[0,32,160]],[46,"Trans-Orange",[255,128,13]],[47,"Trans-Bright Green",[0,187,40]],[69,"Bright Purple",[129,0,123]],[70,"Dark Red",[114,14,15]],[71,"Light Bluish Gray",[175,181,199]],[72,"Dark Bluish Gray",[89,93,96]],[73,"Medium Blue",[115,150,200]],[74,"Medium Green",[127,196,117]],[77,"Light Pink",[254,204,207]],[85,"Dark Purple",[82,0,115]],[86,"Dark Flesh",[126,96,55]],[92,"Nougat",[213,144,52]],[100,"Light Salmon",[254,186,163]],[110,"Violet",[67,84,163]],[112,"Medium Violet",[110,104,187]],[115,"Medium Lime",[199,210,60]],[118,"Aqua",[177,227,227]],[124,"Dark Pink",[203,97,140]],[135,"Sand Blue",[112,130,160]],[138,"Sand Yellow",[186,169,119]],[140,"Earth Blue",[0,32,96]],[141,"Earth Green",[0,69,26]],[151,"Sand Green",[120,144,130]],[191,"Flame Yellowish Orange",[252,172,0]],[216,"Rust",[180,76,13]],[226,"Cool Yellow",[253,234,141]],[272,"Dark Blue",[0,32,96]],[288,"Dark Green",[39,70,45]],[297,"Pearl Gold",[170,127,46]],[308,"Dark Brown",[53,33,0]],[320,"Dark Red",[114,14,15]],[321,"Dark Azure",[70,155,195]],[322,"Medium Azure",[104,195,226]],[323,"Light Aqua",[211,242,234]],[324,"Lavender",[205,164,222]],[325,"Medium Lavender",[169,142,214]],[330,"Olive Green",[119,119,78]],[335,"Sand Red",[188,127,114]],[351,"Medium Dark Pink",[247,133,177]],[353,"Coral",[255,109,98]],[366,"Dust Orange",[224,143,78]],[373,"Sand Purple",[135,124,144]],[378,"Sand Green",[114,143,112]],[379,"Sand Blue",[112,130,157]],
];

const AIR_BLOCKS = new Set(["air", "cave_air", "void_air", "water", "lava"]);
const MC_BLOCK_MAP = {
  stone:[72,"brick"], cobblestone:[8,"brick"], stone_bricks:[71,"brick"], cracked_stone_bricks:[8,"brick"], mossy_stone_bricks:[151,"brick"], smooth_stone:[7,"brick"], polished_granite:[86,"brick"], granite:[25,"brick"], diorite:[7,"brick"], polished_diorite:[15,"brick"], andesite:[72,"brick"], polished_andesite:[8,"brick"], deepslate:[72,"brick"], deepslate_bricks:[8,"brick"], cobbled_deepslate:[8,"brick"], calcite:[15,"brick"], tuff:[72,"brick"], bedrock:[26,"brick"], gravel:[8,"brick"], sand:[19,"brick"], sandstone:[19,"brick"], smooth_sandstone:[138,"brick"], red_sandstone:[25,"brick"], dirt:[86,"brick"], coarse_dirt:[28,"brick"], podzol:[28,"brick"], mud:[28,"brick"], clay:[8,"brick"], grass_block:[37,"brick"], mycelium:[85,"brick"], oak_planks:[19,"brick"], oak_log:[86,"brick"], oak_wood:[86,"brick"], stripped_oak_log:[19,"brick"], spruce_planks:[28,"brick"], spruce_log:[28,"brick"], birch_planks:[15,"brick"], birch_log:[19,"brick"], jungle_planks:[92,"brick"], jungle_log:[86,"brick"], acacia_planks:[25,"brick"], acacia_log:[28,"brick"], dark_oak_planks:[28,"brick"], dark_oak_log:[26,"brick"], mangrove_planks:[4,"brick"], cherry_planks:[29,"brick"], bamboo_planks:[14,"brick"], crimson_planks:[4,"brick"], warped_planks:[3,"brick"], white_wool:[15,"brick"], orange_wool:[36,"brick"], magenta_wool:[124,"brick"], light_blue_wool:[9,"brick"], yellow_wool:[14,"brick"], lime_wool:[37,"brick"], pink_wool:[77,"brick"], gray_wool:[72,"brick"], light_gray_wool:[7,"brick"], cyan_wool:[3,"brick"], purple_wool:[85,"brick"], blue_wool:[1,"brick"], brown_wool:[6,"brick"], green_wool:[2,"brick"], red_wool:[4,"brick"], black_wool:[26,"brick"], white_concrete:[15,"brick"], orange_concrete:[36,"brick"], magenta_concrete:[69,"brick"], light_blue_concrete:[9,"brick"], yellow_concrete:[14,"brick"], lime_concrete:[37,"brick"], pink_concrete:[77,"brick"], gray_concrete:[72,"brick"], light_gray_concrete:[7,"brick"], cyan_concrete:[3,"brick"], purple_concrete:[85,"brick"], blue_concrete:[1,"brick"], brown_concrete:[6,"brick"], green_concrete:[2,"brick"], red_concrete:[4,"brick"], black_concrete:[26,"brick"], terracotta:[86,"brick"], white_terracotta:[15,"brick"], orange_terracotta:[25,"brick"], magenta_terracotta:[124,"brick"], light_blue_terracotta:[73,"brick"], yellow_terracotta:[226,"brick"], lime_terracotta:[115,"brick"], pink_terracotta:[100,"brick"], gray_terracotta:[8,"brick"], light_gray_terracotta:[7,"brick"], cyan_terracotta:[378,"brick"], purple_terracotta:[373,"brick"], blue_terracotta:[379,"brick"], brown_terracotta:[335,"brick"], green_terracotta:[141,"brick"], red_terracotta:[335,"brick"], black_terracotta:[26,"brick"], glass:[40,"brick"], glass_pane:[40,"plate"], white_stained_glass:[40,"brick"], orange_stained_glass:[46,"brick"], light_blue_stained_glass:[43,"brick"], yellow_stained_glass:[44,"brick"], lime_stained_glass:[47,"brick"], cyan_stained_glass:[43,"brick"], blue_stained_glass:[45,"brick"], red_stained_glass:[41,"brick"], coal_ore:[26,"brick"], iron_ore:[86,"brick"], copper_ore:[25,"brick"], gold_ore:[14,"brick"], redstone_ore:[4,"brick"], emerald_ore:[2,"brick"], lapis_ore:[1,"brick"], diamond_ore:[9,"brick"], iron_block:[7,"brick"], gold_block:[14,"brick"], diamond_block:[9,"brick"], emerald_block:[2,"brick"], lapis_block:[1,"brick"], redstone_block:[4,"brick"], copper_block:[25,"brick"], netherite_block:[26,"brick"], netherrack:[4,"brick"], nether_bricks:[26,"brick"], red_nether_bricks:[4,"brick"], soul_sand:[28,"brick"], basalt:[72,"brick"], blackstone:[26,"brick"], quartz_block:[15,"brick"], smooth_quartz:[15,"brick"], glowstone:[14,"brick"], shroomlight:[14,"brick"], magma_block:[4,"brick"], end_stone:[226,"brick"], end_stone_bricks:[226,"brick"], purpur_block:[112,"brick"], obsidian:[26,"brick"], crying_obsidian:[85,"brick"], bricks:[4,"brick"], bookshelf:[19,"brick"], prismarine:[3,"brick"], prismarine_bricks:[9,"brick"], dark_prismarine:[27,"brick"], sea_lantern:[40,"brick"], hay_block:[14,"brick"], honeycomb_block:[36,"brick"], amethyst_block:[85,"brick"], snow_block:[15,"brick"], ice:[9,"brick"], packed_ice:[9,"brick"], blue_ice:[1,"brick"], oak_stairs:[19,"slope"], spruce_stairs:[28,"slope"], birch_stairs:[15,"slope"], jungle_stairs:[92,"slope"], acacia_stairs:[25,"slope"], dark_oak_stairs:[28,"slope"], stone_stairs:[72,"slope"], cobblestone_stairs:[8,"slope"], stone_brick_stairs:[71,"slope"], sandstone_stairs:[19,"slope"], quartz_stairs:[15,"slope"], brick_stairs:[4,"slope"], nether_brick_stairs:[26,"slope"], purpur_stairs:[112,"slope"], oak_slab:[19,"plate"], spruce_slab:[28,"plate"], birch_slab:[15,"plate"], stone_slab:[72,"plate"], cobblestone_slab:[8,"plate"], stone_brick_slab:[71,"plate"], sandstone_slab:[19,"plate"], quartz_slab:[15,"plate"], brick_slab:[4,"plate"], oak_leaves:[37,"plate"], spruce_leaves:[2,"plate"], birch_leaves:[10,"plate"], jungle_leaves:[2,"plate"], acacia_leaves:[37,"plate"], dark_oak_leaves:[2,"plate"], mangrove_leaves:[2,"plate"], cherry_leaves:[29,"plate"],
};

const LDRAW_TO_BL = {1:7,2:6,3:39,4:5,6:8,7:9,8:10,9:62,10:36,14:3,15:1,19:2,25:91,26:11,27:80,28:120,29:27,36:4,37:34,38:68,39:49,40:12,41:17,43:15,44:19,45:14,46:98,47:20,69:71,70:59,71:86,72:85,73:42,74:37,77:56,85:89,86:91,92:28,100:26,110:43,112:73,115:76,118:152,124:104,135:55,138:69,140:63,141:80,151:48,191:110,216:27,226:103,272:63,288:80,297:115,308:120,320:59,321:153,322:156,323:152,324:154,325:157,330:155,335:58,351:23,353:220,366:68,373:54,378:48,379:55};
const LEGO_COLOR_RGB = Object.fromEntries(LEGO_COLORS.map(([id,,rgb]) => [id, rgb]));
const LEGO_COLOR_NAME = Object.fromEntries(LEGO_COLORS.map(([id,name]) => [id, name]));
const BRICK_CATALOG = {brick:{"1x1":["3005","Brick 1x1",0.06],"1x2":["3004","Brick 1x2",0.08],"1x3":["3622","Brick 1x3",0.10],"1x4":["3010","Brick 1x4",0.10],"2x2":["3003","Brick 2x2",0.10],"2x3":["3002","Brick 2x3",0.12],"2x4":["3001","Brick 2x4",0.12]},plate:{"1x1":["3024","Plate 1x1",0.03],"1x2":["3023","Plate 1x2",0.04],"1x3":["3623","Plate 1x3",0.05],"1x4":["3710","Plate 1x4",0.05],"2x2":["3022","Plate 2x2",0.06],"2x3":["3021","Plate 2x3",0.07],"2x4":["3020","Plate 2x4",0.08]},slope:{"1x1":["54200","Slope 1x1x2/3",0.06],"1x2":["3040","Slope 45 2x1",0.08],"2x2":["3039","Slope 45 2x2",0.12],"2x4":["3037","Slope 45 2x4",0.15]}};
const LEGO_PREVIEW_HEIGHT = { brick: 1.2, plate: 0.4, slope: 0.8 };
const MC_LEGACY_IDS = {0:"air",1:"stone",2:"grass_block",3:"dirt",4:"cobblestone",5:"oak_planks",7:"bedrock",8:"water",9:"water",10:"lava",11:"lava",12:"sand",13:"gravel",14:"gold_ore",15:"iron_ore",16:"coal_ore",17:"oak_log",18:"oak_leaves",20:"glass",21:"lapis_ore",22:"lapis_block",24:"sandstone",35:"white_wool",41:"gold_block",42:"iron_block",43:"stone_slab",44:"stone_slab",45:"bricks",47:"bookshelf",48:"mossy_stone_bricks",49:"obsidian",53:"oak_stairs",56:"diamond_ore",57:"diamond_block",67:"cobblestone_stairs",79:"ice",80:"snow_block",82:"clay",87:"netherrack",89:"glowstone",98:"stone_bricks",108:"brick_stairs",109:"stone_brick_stairs",112:"nether_bricks",114:"nether_brick_stairs",121:"end_stone",125:"oak_planks",126:"oak_slab",128:"sandstone_stairs",129:"emerald_ore",133:"emerald_block",134:"spruce_stairs",135:"birch_stairs",136:"jungle_stairs",152:"redstone_block",155:"quartz_block",156:"quartz_stairs",159:"terracotta",170:"hay_block",172:"terracotta",174:"packed_ice",179:"red_sandstone",201:"purpur_block",203:"purpur_stairs",206:"end_stone_bricks",251:"white_concrete"};
const COLOR_NAMES = ["white","orange","magenta","light_blue","yellow","lime","pink","gray","light_gray","cyan","purple","blue","brown","green","red","black"];
const COLORED_BLOCK_IDS = {35:"{}_wool",95:"{}_stained_glass",159:"{}_terracotta",160:"{}_stained_glass",251:"{}_concrete"};
const MC_BLOCK_RGB = {stone:[125,125,125],cobblestone:[127,127,127],dirt:[134,96,67],grass_block:[127,178,56],sand:[219,207,163],gravel:[136,126,126],oak_planks:[162,130,78],spruce_planks:[114,84,48],birch_planks:[192,175,121],oak_log:[109,85,50],stone_bricks:[122,122,122],bricks:[151,97,83],obsidian:[20,18,29],netherrack:[97,38,38],quartz_block:[235,229,222],iron_block:[220,220,220],gold_block:[249,236,79],diamond_block:[98,219,214],emerald_block:[0,166,53],lapis_block:[31,67,140],redstone_block:[171,27,6],snow_block:[249,255,254],ice:[145,190,230],clay:[161,166,179],bedrock:[85,85,85],sandstone:[216,202,155]};
const MERGE_SIZES = [[2,4],[2,3],[2,2],[1,4],[1,3],[1,2],[1,1]];
const LDR_PARTS = {"brick:1x1":"3005.dat","brick:1x2":"3004.dat","brick:1x3":"3622.dat","brick:1x4":"3010.dat","brick:2x2":"3003.dat","brick:2x3":"3002.dat","brick:2x4":"3001.dat","plate:1x1":"3024.dat","plate:1x2":"3023.dat","plate:1x3":"3623.dat","plate:1x4":"3710.dat","plate:2x2":"3022.dat","plate:2x3":"3021.dat","plate:2x4":"3020.dat","slope:1x1":"54200.dat","slope:1x2":"3040.dat","slope:2x2":"3039.dat"};

const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const loadingOvl = document.getElementById("loadingOverlay");
const resultsOvl = document.getElementById("resultsOverlay");
const btnBack = document.getElementById("btnBack");
const statsEl = document.getElementById("resultsStats");
const colorBarEl = document.getElementById("colorBar");
const partsBody = document.getElementById("partsBody");
const dlRow = document.getElementById("dlRow");
const mcCanvas = document.getElementById("viewerMc");
const legoCanvas = document.getElementById("viewerLego");

let currentXml = null;
let currentLdrUrl = null;
let currentXmlUrl = null;
let _viewers = [];

function showToast(icon, msg, duration = 4000) {
  const t = document.getElementById("toast");
  document.getElementById("toastMsg").textContent = msg;
  t.querySelector(".toast-icon").textContent = icon;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), duration);
}

uploadZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => { if (fileInput.files[0]) upload(fileInput.files[0]); });
uploadZone.addEventListener("dragover", (e) => { e.preventDefault(); uploadZone.classList.add("drag-over"); });
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  const f = e.dataTransfer.files[0];
  if (f) upload(f);
});
btnBack.addEventListener("click", () => {
  resultsOvl.classList.remove("active");
  disposeViewer();
});

async function upload(file) {
  const ext = (file.name.split(".").pop() || "").toLowerCase();
  if (!["schem", "schematic", "litematic"].includes(ext)) {
    showToast("⚠️", "Unsupported file type. Use .schem, .schematic, or .litematic.");
    return;
  }
  loadingOvl.classList.add("active");
  uploadZone.classList.add("uploading");
  try {
    const data = await convertAndOptimize(file);
    currentXml = data.bricklink_xml || null;
    showResults(data);
    showToast("🧱", "Converted locally in your browser.");
  } catch (error) {
    console.error(error);
    showToast("⚠️", error.message || "Conversion failed.", 5000);
  } finally {
    loadingOvl.classList.remove("active");
    uploadZone.classList.remove("uploading");
    fileInput.value = "";
  }
}

async function convertAndOptimize(file) {
  const root = await readRoot(file);
  const { width, height, length, blocks } = parseFile(file.name, root);
  if (!blocks.size) {
    throw new Error("No blocks found. File may be empty or unsupported.");
  }
  const legoBlocks = new Map();
  for (const [key, name] of blocks.entries()) {
    const mapped = mapBlockToLego(name);
    if (mapped) legoBlocks.set(key, mapped);
  }
  const allBricks = [];
  for (let y = 0; y < height; y++) {
    const layer = new Map();
    for (const [key, value] of legoBlocks.entries()) {
      const [x0, y0, z0] = parseKey3(key);
      if (y0 === y) layer.set(key2(x0, z0), value);
    }
    if (!layer.size) continue;
    for (const brick of optimizeLayer(layer, width, length)) {
      allBricks.push([brick[0], y, brick[1], brick[2], brick[3], brick[4], brick[5]]);
    }
  }
  const partsCounter = new Map();
  const colorCounter = new Map();
  let totalCost = 0;
  for (const [x, y, z, w, l, cid, bt] of allBricks) {
    const [partId, partName, price] = getPartInfo(bt, w, l);
    const pKey = `${partId}|${cid}|${partName}|${bt}`;
    partsCounter.set(pKey, (partsCounter.get(pKey) || 0) + 1);
    colorCounter.set(cid, (colorCounter.get(cid) || 0) + 1);
    totalCost += price;
  }
  const colorSummary = [...colorCounter.entries()].sort((a, b) => b[1] - a[1]).map(([cid, count]) => ({ color_id: cid, name: LEGO_COLOR_NAME[cid] || `#${cid}`, rgb: LEGO_COLOR_RGB[cid] || [128,128,128], count }));
  const brickSummary = [...partsCounter.entries()].map(([key, count]) => {
    const [part_id, cidRaw, part_name, brick_type] = key.split("|");
    const cid = Number(cidRaw);
    return { part_id, part_name, brick_type, color_id: cid, color_name: LEGO_COLOR_NAME[cid] || "", rgb: LEGO_COLOR_RGB[cid] || [128,128,128], count };
  }).sort((a, b) => b.count - a.count);
  const paletteMap = new Map();
  const palette = [];
  let voxels = [];
  for (const [x, y, z, w, l, cid, bt] of allBricks) {
    const rgb = LEGO_COLOR_RGB[cid] || [128,128,128];
    const key = rgb.join(",");
    if (!paletteMap.has(key)) {
      paletteMap.set(key, palette.length);
      palette.push(rgb);
    }
    const h = LEGO_PREVIEW_HEIGHT[bt] || LEGO_PREVIEW_HEIGHT.brick;
    voxels.push([x, y * LEGO_PREVIEW_HEIGHT.brick, z, w, h, l, paletteMap.get(key)]);
  }
  if (voxels.length > 60000) {
    const step = Math.floor(voxels.length / 60000) + 1;
    voxels = voxels.filter((_, i) => i % step === 0);
  }
  const ldrContent = generateLdr(allBricks);
  const bricklinkXml = generateBricklinkXml(partsCounter);
  return { session_id: createSessionId(), dimensions: { width, height, length }, total_blocks: blocks.size, total_bricks: allBricks.length, unique_parts: partsCounter.size, estimated_cost: Math.round(totalCost * 100) / 100, color_summary: colorSummary, brick_summary: brickSummary, voxels, palette, ldr_content: ldrContent, bricklink_xml: bricklinkXml };
}

async function readRoot(file) {
  let buffer = await file.arrayBuffer();
  buffer = await maybeDecompress(buffer);
  const parsed = await readNbt(buffer);
  const root = parsed && typeof parsed === "object" && "data" in parsed ? parsed.data : parsed;
  return unwrapTag(root);
}

async function maybeDecompress(buffer) {
  const bytes = new Uint8Array(buffer);
  const isGzip = bytes.length > 2 && bytes[0] === 0x1f && bytes[1] === 0x8b;
  if (!isGzip) return buffer;
  if ("DecompressionStream" in globalThis) {
    try {
      const stream = new Blob([buffer]).stream().pipeThrough(new DecompressionStream("gzip"));
      return await new Response(stream).arrayBuffer();
    } catch {
      // Fall through to JS decompression for browsers with partial gzip stream support.
    }
  }
  return gunzipSync(bytes).buffer;
}

function unwrapTag(value) {
  if (value == null) return value;
  if (typeof value === "bigint" || typeof value === "number" || typeof value === "string" || typeof value === "boolean") return value;
  if (value instanceof Number || value instanceof String || value instanceof Boolean) return value.valueOf();
  if (ArrayBuffer.isView(value)) return Array.from(value);
  if (Array.isArray(value)) return value.map(unwrapTag);
  if (typeof value === "object") {
    if (typeof value.valueOf === "function") { const prim = value.valueOf(); if (typeof prim === "number" || typeof prim === "bigint" || typeof prim === "string") return prim; }
    const keys = Object.keys(value);
    if ("value" in value && ("type" in value || keys.length <= 2)) return unwrapTag(value.value);
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = unwrapTag(v);
    return out;
  }
  return value;
}

function parseFile(filename, nbtData) {
  const ext = filename.toLowerCase().split(".").pop() || "";
  if (ext === "litematic") return parseLitematic(nbtData);
  if (ext === "schematic") return parseSchematic(nbtData);
  try { return parseSchem(nbtData); } catch { try { return parseSchematic(nbtData); } catch { return parseLitematic(nbtData); } }
}

function parseSchem(nbtData) {
  let root = nbtData;
  if (root.Schematic) root = root.Schematic;
  const width = asNumber(root.Width);
  const height = asNumber(root.Height);
  const length = asNumber(root.Length);
  const blk = isObject(root.Blocks) ? root.Blocks : null;
  const paletteTag = blk?.Palette || root.Palette || {};
  const rawData = blk?.Data || blk?.BlockData || root.BlockData || [];
  const palette = new Map();
  for (const [name, idx] of Object.entries(paletteTag)) palette.set(asNumber(idx), String(name));
  const raw = asByteArray(rawData);
  const blocks = new Map();
  let offset = 0;
  for (let y = 0; y < height; y++) {
    for (let z = 0; z < length; z++) {
      for (let x = 0; x < width; x++) {
        if (offset >= raw.length) break;
        const result = readVarInt(raw, offset);
        offset = result.offset;
        const name = palette.get(result.value) || "air";
        if (!AIR_BLOCKS.has(normalizeBlockName(name))) blocks.set(key3(x, y, z), name);
      }
    }
  }
  return { width, height, length, blocks };
}

function parseSchematic(nbtData) {
  let root = nbtData;
  if (root.Schematic) root = root.Schematic;
  const width = asNumber(root.Width);
  const height = asNumber(root.Height);
  const length = asNumber(root.Length);
  const blockIds = asByteArray(root.Blocks || []);
  const blockData = asByteArray(root.Data || new Uint8Array(blockIds.length));
  const blocks = new Map();
  for (let y = 0; y < height; y++) {
    for (let z = 0; z < length; z++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * length + z) * width + x;
        if (idx >= blockIds.length) break;
        const bid = blockIds[idx] & 0xff;
        const bdata = idx < blockData.length ? blockData[idx] & 0x0f : 0;
        if (bid === 0) continue;
        let name;
        if (COLORED_BLOCK_IDS[bid]) name = COLORED_BLOCK_IDS[bid].replace("{}", COLOR_NAMES[bdata & 0x0f]);
        else if (MC_LEGACY_IDS[bid]) name = MC_LEGACY_IDS[bid];
        else name = `unknown_${bid}`;
        blocks.set(key3(x, y, z), name);
      }
    }
  }
  return { width, height, length, blocks };
}

function parseLitematic(nbtData) {
  const regions = nbtData.Regions || {};
  const allBlocks = new Map();
  const minC = [Infinity, Infinity, Infinity];
  const maxC = [-Infinity, -Infinity, -Infinity];
  for (const region of Object.values(regions)) {
    const pos = region.Position || {};
    const size = region.Size || {};
    const rx = asNumber(pos.x || 0), ry = asNumber(pos.y || 0), rz = asNumber(pos.z || 0);
    const sx = asNumber(size.x || 0), sy = asNumber(size.y || 0), sz = asNumber(size.z || 0);
    const ax = Math.abs(sx), ay = Math.abs(sy), az = Math.abs(sz);
    const ox = sx >= 0 ? rx : rx + sx + 1;
    const oy = sy >= 0 ? ry : ry + sy + 1;
    const oz = sz >= 0 ? rz : rz + sz + 1;
    const palette = region.BlockStatePalette || [];
    const blockStates = region.BlockStates || [];
    if (!palette.length || !blockStates.length) continue;
    const bits = Math.max(2, Math.ceil(Math.log2(palette.length)));
    const entriesPerLong = Math.floor(64 / bits);
    const mask = (1n << BigInt(bits)) - 1n;
    const longs = blockStates.map((value) => {
      const raw = typeof value === "bigint" ? value : BigInt(value);
      return raw >= 0n ? raw : raw + (1n << 64n);
    });
    for (let y = 0; y < ay; y++) {
      for (let z = 0; z < az; z++) {
        for (let x = 0; x < ax; x++) {
          const i = (y * az + z) * ax + x;
          const longIdx = Math.floor(i / entriesPerLong);
          const bitOff = BigInt((i % entriesPerLong) * bits);
          if (longIdx >= longs.length) break;
          const pidx = Number((longs[longIdx] >> bitOff) & mask);
          if (pidx >= palette.length) continue;
          const entry = palette[pidx];
          const bname = typeof entry === "string" ? entry : String((entry && entry.Name) || "air");
          if (bname.includes("air")) continue;
          const wx = ox + x, wy = oy + y, wz = oz + z;
          allBlocks.set(key3(wx, wy, wz), bname);
          minC[0] = Math.min(minC[0], wx); minC[1] = Math.min(minC[1], wy); minC[2] = Math.min(minC[2], wz);
          maxC[0] = Math.max(maxC[0], wx); maxC[1] = Math.max(maxC[1], wy); maxC[2] = Math.max(maxC[2], wz);
        }
      }
    }
  }
  if (!allBlocks.size) return { width: 0, height: 0, length: 0, blocks: new Map() };
  const blocks = new Map();
  for (const [k, name] of allBlocks.entries()) {
    const [x, y, z] = parseKey3(k);
    blocks.set(key3(x - minC[0], y - minC[1], z - minC[2]), name);
  }
  return { width: maxC[0] - minC[0] + 1, height: maxC[1] - minC[1] + 1, length: maxC[2] - minC[2] + 1, blocks };
}

function normalizeBlockName(name) {
  let value = String(name).toLowerCase().trim();
  if (value.includes(":")) value = value.split(":", 2)[1];
  if (value.includes("[")) value = value.split("[", 1)[0];
  return value;
}

function colorDistSq(c1, c2) {
  const dr = c1[0] - c2[0];
  const dg = c1[1] - c2[1];
  const db = c1[2] - c2[2];
  return 2 * dr * dr + 4 * dg * dg + 3 * db * db;
}

function findClosestLegoColor(r, g, b) {
  let bestId = 71;
  let bestDistance = Infinity;
  for (const [id,,rgb] of LEGO_COLORS) {
    const d = colorDistSq([r, g, b], rgb);
    if (d < bestDistance) { bestDistance = d; bestId = id; }
  }
  return bestId;
}

function mapBlockToLego(blockName) {
  const name = normalizeBlockName(blockName);
  if (AIR_BLOCKS.has(name)) return null;
  if (MC_BLOCK_MAP[name]) return MC_BLOCK_MAP[name];
  if (MC_BLOCK_RGB[name]) return [findClosestLegoColor(...MC_BLOCK_RGB[name]), "brick"];
  for (const [suffix, brickType] of [["_stairs", "slope"], ["_slab", "plate"], ["_wall", "brick"], ["_fence", "brick"], ["_door", "plate"], ["_trapdoor", "plate"]]) {
    if (name.endsWith(suffix)) {
      const base = name.slice(0, -suffix.length);
      for (const variant of [base, `${base}_planks`, `${base}_block`]) {
        if (MC_BLOCK_MAP[variant]) return [MC_BLOCK_MAP[variant][0], brickType];
      }
    }
  }
  return [71, "brick"];
}

function optimizeLayer(layerCells, width, length) {
  const used = new Set();
  const bricks = [];
  const sortedKeys = [...layerCells.keys()].sort((a, b) => { const [ax, az] = parseKey2(a); const [bx, bz] = parseKey2(b); return ax - bx || az - bz; });
  for (const key of sortedKeys) {
    if (used.has(key)) continue;
    const [x, z] = parseKey2(key);
    const [cid, brickType] = layerCells.get(key);
    let placed = false;
    for (const [mw, ml] of MERGE_SIZES) {
      if (mw === 1 && ml === 1) break;
      const orientations = mw === ml ? [[mw, ml]] : [[mw, ml], [ml, mw]];
      for (const [w, l] of orientations) {
        if (x + w > width || z + l > length) continue;
        let ok = true;
        for (let dx = 0; dx < w && ok; dx++) {
          for (let dz = 0; dz < l; dz++) {
            const pos = key2(x + dx, z + dz);
            if (used.has(pos) || !layerCells.has(pos)) { ok = false; break; }
            const candidate = layerCells.get(pos);
            if (candidate[0] !== cid || candidate[1] !== brickType) { ok = false; break; }
          }
        }
        if (!ok) continue;
        for (let dx = 0; dx < w; dx++) for (let dz = 0; dz < l; dz++) used.add(key2(x + dx, z + dz));
        bricks.push([x, z, w, l, cid, brickType]);
        placed = true;
        break;
      }
      if (placed) break;
    }
    if (!placed) { used.add(key); bricks.push([x, z, 1, 1, cid, brickType]); }
  }
  return bricks;
}

function generateLdr(bricks) {
  const lines = ["0 FILE brickcraft_model.ldr", "0 BrickCraft Converted Model", "0 Name: brickcraft_model.ldr", "0 Author: BrickCraft"];
  for (const [x, y, z, w, l, cid, brickType] of bricks) {
    const part = LDR_PARTS[`${brickType}:${Math.min(w, l)}x${Math.max(w, l)}`] || "3005.dat";
    lines.push(`1 ${cid} ${x * 20} ${-(y * 24)} ${z * 20} 1 0 0 0 1 0 0 0 1 ${part}`);
  }
  lines.push("0");
  return lines.join("\n");
}

function generateBricklinkXml(partsCounter) {
  const lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<INVENTORY>'];
  for (const [key, count] of partsCounter.entries()) {
    const [partId, cidRaw] = key.split("|");
    const color = LDRAW_TO_BL[Number(cidRaw)] || 0;
    lines.push("  <ITEM>", "    <ITEMTYPE>P</ITEMTYPE>", `    <ITEMID>${partId}</ITEMID>`, `    <COLOR>${color}</COLOR>`, `    <MINQTY>${count}</MINQTY>`, "  </ITEM>");
  }
  lines.push("</INVENTORY>");
  return lines.join("\n");
}

function getPartInfo(brickType, w, l) {
  const catalog = BRICK_CATALOG[brickType] || BRICK_CATALOG.brick;
  const key = `${Math.min(w, l)}x${Math.max(w, l)}`;
  return catalog[key] || catalog["1x1"] || ["3005", "Brick 1x1", 0.06];
}

function createSessionId() { if (crypto?.randomUUID) return crypto.randomUUID().replace(/-/g, "").slice(0, 8); return Math.random().toString(16).slice(2, 10); }

function showResults(data) {
  const dim = `${data.dimensions.width}×${data.dimensions.height}×${data.dimensions.length}`;
  statsEl.innerHTML = `
    <div class="rstat"><span class="rstat-val">${data.total_bricks.toLocaleString()}</span><span class="rstat-label">Total Bricks</span></div>
    <div class="rstat"><span class="rstat-val cost">$${data.estimated_cost.toFixed(2)}</span><span class="rstat-label">Est. Cost</span></div>
    <div class="rstat"><span class="rstat-val parts">${data.unique_parts}</span><span class="rstat-label">Unique Parts</span></div>
    <div class="rstat"><span class="rstat-val dim">${dim}</span><span class="rstat-label">Dimensions</span></div>`;
  const total = data.color_summary.reduce((sum, item) => sum + item.count, 0) || 1;
  colorBarEl.innerHTML = data.color_summary.map((item) => {
    const pct = ((item.count / total) * 100).toFixed(1);
    return `<div class="color-bar-seg" style="flex:${item.count};background:rgb(${item.rgb.join(",")})" data-tip="${item.name} - ${item.count} (${pct}%)"></div>`;
  }).join("");
  partsBody.innerHTML = data.brick_summary.map((part) => `
    <tr>
      <td>${part.part_name}<br><span style="color:var(--text-dim);font-size:10px">#${part.part_id}</span></td>
      <td><span class="color-chip" style="background:rgb(${part.rgb.join(",")})"></span>${part.color_name}</td>
      <td style="color:var(--text)">${part.count}</td>
    </tr>`).join("");
  if (currentLdrUrl) URL.revokeObjectURL(currentLdrUrl);
  if (currentXmlUrl) URL.revokeObjectURL(currentXmlUrl);
  currentLdrUrl = URL.createObjectURL(new Blob([data.ldr_content], { type: "text/plain" }));
  currentXmlUrl = URL.createObjectURL(new Blob([data.bricklink_xml], { type: "application/xml" }));
  dlRow.innerHTML = `
    <a class="btn-dl btn-dl-ldr" href="${currentLdrUrl}" download="brickcraft_${data.session_id}.ldr">⬇ Download LDR</a>
    <a class="btn-dl btn-dl-xml" href="${currentXmlUrl}" download="brickcraft_${data.session_id}_bricklink.xml">🛒 BrickLink XML</a>
    <button class="btn-dl btn-dl-order" id="btnOrder">🛒 Order on BrickLink →</button>`;
  document.getElementById("btnOrder").addEventListener("click", orderOnBrickLink);
  resultsOvl.classList.add("active");
  if (data.voxels?.length && typeof THREE !== "undefined") initViewers(data.voxels, data.palette);
}

async function orderOnBrickLink() {
  if (!currentXml) { showToast("⚠️", "No XML data available. Please convert a file first."); return; }
  try { await navigator.clipboard.writeText(currentXml); } catch {
    const ta = document.createElement("textarea");
    ta.value = currentXml;
    ta.style.cssText = "position:fixed;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
  }
  showToast("✅", "XML copied. Paste it into BrickLink Upload, opening now...");
  setTimeout(() => window.open("https://www.bricklink.com/v2/wanted/upload.page", "_blank"), 1200);
}

function disposeViewer() {
  for (const viewer of _viewers) {
    if (viewer.raf) cancelAnimationFrame(viewer.raf);
    if (viewer.resizeObserver) viewer.resizeObserver.disconnect();
    if (viewer.canvas && viewer.onPointerDown) viewer.canvas.removeEventListener("pointerdown", viewer.onPointerDown);
    if (viewer.canvas && viewer.onWheel) viewer.canvas.removeEventListener("wheel", viewer.onWheel);
    if (viewer.onPointerUp) window.removeEventListener("pointerup", viewer.onPointerUp);
    if (viewer.onPointerMove) window.removeEventListener("pointermove", viewer.onPointerMove);
    if (viewer.renderer) viewer.renderer.dispose();
  }
  _viewers = [];
}

function initViewers(voxels, palette) {
  disposeViewer();
  if (mcCanvas) _viewers.push(createViewer(mcCanvas, voxels, palette, "mc"));
  if (legoCanvas) _viewers.push(createViewer(legoCanvas, voxels, palette, "lego"));
}

function createViewer(canvas, voxels, palette, style) {
  const width = canvas.clientWidth || 600;
  const height = canvas.clientHeight || 600;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(style === "lego" ? 36 : 42, width / height, 0.1, 10000);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setSize(width, height, false);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = style === "lego" ? 0.88 : 1.04;
  if (style === "lego") {
    scene.background = new THREE.Color(0xf0f2f6);
    const hemi = new THREE.HemisphereLight(0xffffff, 0xd9dfeb, 1.0);
    scene.add(hemi);
    const key = new THREE.DirectionalLight(0xffffff, 0.92);
    key.position.set(2.4, 4.6, 3.2);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xf8fbff, 0.42);
    fill.position.set(-3.2, 2.1, 2.5);
    scene.add(fill);
    const rim = new THREE.DirectionalLight(0xffffff, 0.32);
    rim.position.set(-2.5, 3.2, -3.5);
    scene.add(rim);
    const bounce = new THREE.DirectionalLight(0xfff4ea, 0.14);
    bounce.position.set(0, -2, 1.4);
    scene.add(bounce);
  } else {
    scene.background = new THREE.Color(0x4d74bd);
    scene.fog = new THREE.Fog(0x4d74bd, 80, 210);
    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const sun = new THREE.DirectionalLight(0xfff3d8, 1.12);
    sun.position.set(2.5, 4.2, 2.1);
    scene.add(sun);
    const sky = new THREE.DirectionalLight(0xb7d7ff, 0.58);
    sky.position.set(-2, 2.8, -2);
    scene.add(sky);
    const groundBounce = new THREE.DirectionalLight(0x86b66a, 0.18);
    groundBounce.position.set(0, -1.5, 0.5);
    scene.add(groundBounce);
  }

  let minX = Infinity, minY = Infinity, minZ = Infinity, maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  for (const v of voxels) { minX = Math.min(minX, v[0]); maxX = Math.max(maxX, v[0] + v[3]); minY = Math.min(minY, v[1]); maxY = Math.max(maxY, v[1] + v[4]); minZ = Math.min(minZ, v[2]); maxZ = Math.max(maxZ, v[2] + v[5]); }
  const spanX = maxX - minX;
  const spanY = maxY - minY;
  const spanZ = maxZ - minZ;
  const footprint = Math.max(spanX, spanZ) || 1;
  const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2, cz = (minZ + maxZ) / 2;
  const size = Math.max(spanX, spanY, spanZ) || 10;
  const groups = {};
  for (const v of voxels) { const pi = v[6]; if (!groups[pi]) groups[pi] = []; groups[pi].push(v); }
  const dummy = new THREE.Object3D();
  for (const [pi, list] of Object.entries(groups)) {
    const rgb = palette[Number(pi)] || [128,128,128];
    const material = style === "lego"
      ? new THREE.MeshStandardMaterial({
          color: new THREE.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255),
          roughness: 0.52,
          metalness: 0.0
        })
      : new THREE.MeshLambertMaterial({
          color: new THREE.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255),
          flatShading: true
        });
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const mesh = new THREE.InstancedMesh(geometry, material, list.length);
    const gap = style === "lego" ? 0.94 : 0.985;
    list.forEach((v, i) => {
      const [x, y, z, w, h, l] = v;
      dummy.position.set(x + w / 2 - cx, y + h / 2 - cy, z + l / 2 - cz);
      dummy.scale.set(w * gap, h * gap, l * gap);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    });
    scene.add(mesh);
  }
  const groundY = minY - cy;
  const gridSize = Math.max(footprint * 1.8, Math.min(size * 1.15, footprint * 2.4), 12);
  const gridDivisions = Math.max(14, Math.min(36, Math.round(gridSize)));
  const grid = new THREE.GridHelper(
    gridSize,
    gridDivisions,
    style === "lego" ? 0xc5cfde : 0x3f5da3,
    style === "lego" ? 0xe7edf7 : 0x253870
  );
  grid.position.y = groundY;
  grid.material.opacity = style === "lego" ? 0.72 : 0.46;
  grid.material.transparent = true;
  scene.add(grid);
  if (style === "lego") {
    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(gridSize * 1.08, gridSize * 1.08),
      new THREE.MeshBasicMaterial({ color: 0xf7f8fb, opacity: 0.98, transparent: true })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = groundY - 0.06;
    scene.add(floor);
    const shadow = new THREE.Mesh(
      new THREE.CircleGeometry(Math.max(footprint * 0.5, 6), 48),
      new THREE.MeshBasicMaterial({ color: 0x000000, opacity: 0.1, transparent: true })
    );
    shadow.rotation.x = -Math.PI / 2;
    shadow.position.y = groundY + 0.02;
    scene.add(shadow);
  } else {
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(gridSize * 1.05, gridSize * 1.05),
      new THREE.MeshBasicMaterial({ color: 0x4b6f42, opacity: 0.18, transparent: true })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = groundY - 0.03;
    scene.add(ground);
  }
  const targetY = groundY + spanY * (style === "lego" ? 0.49 : 0.46);
  const vFov = THREE.MathUtils.degToRad(camera.fov);
  const hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect);
  const verticalFit = Math.max(spanY * (style === "lego" ? 0.74 : 0.68), 7) / Math.tan(vFov / 2);
  const horizontalFit = Math.max(footprint * 1.08, 7) / Math.tan(hFov / 2);
  const fitRadius = Math.max(verticalFit, horizontalFit) * (style === "lego" ? 0.9 : 0.88);
  let theta = Math.PI * (style === "lego" ? 0.8 : 0.74);
  let phi = Math.PI * (style === "lego" ? 0.135 : 0.17);
  let radius = fitRadius;
  function updateCam() {
    camera.position.set(
      radius * Math.cos(phi) * Math.sin(theta),
      targetY + radius * Math.sin(phi),
      radius * Math.cos(phi) * Math.cos(theta)
    );
    camera.lookAt(0, targetY, 0);
  }
  updateCam();
  let isDragging = false, prevX = 0, prevY = 0;
  const onPointerDown = (e) => { isDragging = true; prevX = e.clientX; prevY = e.clientY; };
  const onPointerUp = () => { isDragging = false; };
  const onPointerMove = (e) => {
    if (!isDragging) return;
    theta -= (e.clientX - prevX) * 0.008;
    phi += (e.clientY - prevY) * 0.008;
    phi = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, phi));
    prevX = e.clientX; prevY = e.clientY;
    updateCam();
  };
  const onWheel = (e) => {
    e.preventDefault();
    radius *= e.deltaY > 0 ? 1.08 : 0.93;
    radius = Math.max(fitRadius * 0.55, Math.min(fitRadius * 2.8, radius));
    updateCam();
  };
  canvas.addEventListener("pointerdown", onPointerDown);
  window.addEventListener("pointerup", onPointerUp);
  window.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("wheel", onWheel, { passive: false });
  const resizeObserver = new ResizeObserver(() => {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  });
  resizeObserver.observe(canvas);
  const viewer = { canvas, renderer, resizeObserver, onPointerDown, onPointerUp, onPointerMove, onWheel, raf: 0 };
  function animate() {
    viewer.raf = requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  animate();
  return viewer;
}

function readVarInt(data, offset) {
  let result = 0, shift = 0;
  while (offset < data.length) {
    const b = data[offset] & 0xff;
    offset += 1;
    result |= (b & 0x7f) << shift;
    if (!(b & 0x80)) break;
    shift += 7;
  }
  return { value: result, offset };
}

function asNumber(value) {
  if (typeof value === "bigint") return Number(value);
  if (typeof value === "number") return value;
  if (value == null) return 0;
  const primitive = typeof value.valueOf === "function" ? value.valueOf() : value;
  if (typeof primitive === "bigint") return Number(primitive);
  if (typeof primitive === "number") return primitive;
  const parsed = Number(String(primitive).trim().replace(/[bsilfd]$/i, ""));
  return Number.isFinite(parsed) ? parsed : 0;
}
function asByteArray(value) { if (ArrayBuffer.isView(value)) return Uint8Array.from(value); if (Array.isArray(value)) return Uint8Array.from(value.map((v) => asNumber(v))); return Uint8Array.from([]); }
function isObject(value) { return value && typeof value === "object" && !Array.isArray(value); }
function key3(x, y, z) { return `${x},${y},${z}`; }
function key2(x, z) { return `${x},${z}`; }
function parseKey3(key) { return key.split(",").map((v) => Number(v)); }
function parseKey2(key) { return key.split(",").map((v) => Number(v)); }