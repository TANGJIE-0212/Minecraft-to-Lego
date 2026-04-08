import gzip, struct, io, os, math

def write_tag_short(buf, name, val):
    buf.write(b'\x02')
    buf.write(struct.pack('>H', len(name)))
    buf.write(name.encode())
    buf.write(struct.pack('>h', val))

def write_tag_string(buf, name, val):
    buf.write(b'\x08')
    buf.write(struct.pack('>H', len(name)))
    buf.write(name.encode())
    buf.write(struct.pack('>H', len(val)))
    buf.write(val.encode())

def write_tag_byte_array(buf, name, data):
    buf.write(b'\x07')
    buf.write(struct.pack('>H', len(name)))
    buf.write(name.encode())
    buf.write(struct.pack('>i', len(data)))
    buf.write(bytes(data))

def make_schematic(filename, w, h, l, blocks, data=None):
    if data is None:
        data = [0]*len(blocks)
    buf = io.BytesIO()
    buf.write(b'\x0a')
    buf.write(struct.pack('>H', 9))
    buf.write(b'Schematic')
    write_tag_short(buf, 'Width', w)
    write_tag_short(buf, 'Height', h)
    write_tag_short(buf, 'Length', l)
    write_tag_string(buf, 'Materials', 'Alpha')
    write_tag_byte_array(buf, 'Blocks', blocks)
    write_tag_byte_array(buf, 'Data', data)
    buf.write(b'\x09')
    buf.write(struct.pack('>H', 8))
    buf.write(b'Entities')
    buf.write(b'\x0a')
    buf.write(struct.pack('>i', 0))
    buf.write(b'\x09')
    buf.write(struct.pack('>H', 12))
    buf.write(b'TileEntities')
    buf.write(b'\x0a')
    buf.write(struct.pack('>i', 0))
    buf.write(b'\x00')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with gzip.open(filename, 'wb') as f:
        f.write(buf.getvalue())
    print(f'Created {filename} ({w}x{h}x{l}, {w*h*l} total blocks)')

# === 1. Small House (8x6x8) ===
w,h,l = 8,6,8
blocks = [0]*(w*h*l)
def sb(x,y,z,bid):
    blocks[y*w*l + z*w + x] = bid

for x in range(8):
    for z in range(8):
        sb(x,0,z, 98)  # stone brick floor

for y in range(1,5):
    for x in range(8):
        sb(x,y,0, 5); sb(x,y,7, 5)
    for z in range(8):
        sb(0,y,z, 5); sb(7,y,z, 5)

for y in [2,3]:
    sb(3,y,0, 20); sb(4,y,0, 20)
    sb(3,y,7, 20); sb(4,y,7, 20)

sb(3,1,0, 64); sb(3,2,0, 64)

for x in range(8):
    for z in range(8):
        sb(x,5,z, 45)

make_schematic('samples/small_house.schematic', w, h, l, blocks)

# === 2. Castle Tower (6x12x6) ===
w,h,l = 6,12,6
blocks = [0]*(w*h*l)
def sb2(x,y,z,bid):
    blocks[y*w*l + z*w + x] = bid

for y in range(10):
    for x in range(6):
        sb2(x,y,0, 98); sb2(x,y,5, 98)
    for z in range(6):
        sb2(0,y,z, 98); sb2(5,y,z, 98)

for x in range(6):
    for z in range(6):
        sb2(x,0,z, 98)

for y in [3,4,7,8]:
    sb2(2,y,0, 102); sb2(3,y,0, 102)
    sb2(2,y,5, 102); sb2(3,y,5, 102)

for x in [0,2,4]:
    for z in [0,2,4]:
        sb2(x,10,z, 98); sb2(x,11,z, 98)

sb2(2,3,2, 50); sb2(3,3,3, 50)

make_schematic('samples/castle_tower.schematic', w, h, l, blocks)

# === 3. Creeper Face (8x8x1) ===
w,h,l = 8,8,1
blocks = [0]*(w*h*l)
data = [0]*(w*h*l)
G, B = 35, 35
face = [
    [G,G,G,G,G,G,G,G],
    [G,G,G,G,G,G,G,G],
    [G,B,B,G,G,B,B,G],
    [G,B,B,G,G,B,B,G],
    [G,G,G,B,B,G,G,G],
    [G,G,B,B,B,B,G,G],
    [G,G,B,B,B,B,G,G],
    [G,G,B,G,G,B,G,G],
]
is_black = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,1,1,0,0,1,1,0],
    [0,1,1,0,0,1,1,0],
    [0,0,0,1,1,0,0,0],
    [0,0,1,1,1,1,0,0],
    [0,0,1,1,1,1,0,0],
    [0,0,1,0,0,1,0,0],
]
for y in range(8):
    for x in range(8):
        idx = (7-y)*w*l + x
        blocks[idx] = 35
        data[idx] = 15 if is_black[y][x] else 13

make_schematic('samples/creeper_face.schematic', w, h, l, blocks, data)

# === 4. Garden Bridge (12x5x5) ===
w,h,l = 12,5,5
blocks = [0]*(w*h*l)
def sb4(x,y,z,bid):
    blocks[y*w*l + z*w + x] = bid

for x in range(12):
    for z in range(5):
        sb4(x,0,z, 9)

for x in range(12):
    for z in [1,2,3]:
        sb4(x,1,z, 5)

for z in [1,2,3]:
    sb4(0,2,z, 5); sb4(11,2,z, 5)

for x in range(12):
    sb4(x,2,1, 85); sb4(x,2,3, 85)

sb4(0,3,1, 91); sb4(0,3,3, 91)
sb4(11,3,1, 91); sb4(11,3,3, 91)

for x in [2,4,6,8,10]:
    sb4(x,2,0, 38); sb4(x,2,4, 38)

make_schematic('samples/garden_bridge.schematic', w, h, l, blocks)

COLOR_BLOCK_MAP = {
    (48, 48, 56): (49, 0),
    (80, 80, 88): (98, 0),
    (110, 108, 116): (1, 0),
    (160, 32, 32): (95, 14),
    (32, 48, 160): (95, 11),
    (32, 140, 48): (95, 13),
    (120, 40, 160): (95, 10),
    (220, 180, 40): (41, 0),
    (36, 34, 40): (35, 15),
    (64, 62, 72): (35, 7),
    (200, 128, 112): (17, 0),
    (120, 80, 48): (17, 0),
    (240, 160, 184): (35, 6),
    (232, 125, 160): (35, 2),
    (255, 192, 208): (35, 0),
    (136, 192, 112): (2, 0),
    (255, 180, 200): (35, 6),
    (62, 42, 28): (17, 0),
    (176, 138, 80): (5, 0),
    (180, 36, 36): (35, 14),
    (120, 24, 24): (112, 0),
    (230, 228, 220): (155, 0),
    (140, 140, 136): (98, 0),
    (40, 36, 32): (49, 0),
    (192, 176, 120): (170, 0),
    (240, 236, 220): (155, 0),
    (80, 128, 64): (48, 0),
}


def voxel_index(w, l, x, y, z):
    return y * w * l + z * w + x


def map_rgb_to_block(rgb):
    if rgb not in COLOR_BLOCK_MAP:
        raise ValueError(f'No block mapping defined for RGB {rgb}')
    return COLOR_BLOCK_MAP[rgb]


def make_voxel_schematic(filename, voxels):
    min_x = min(x for x, _, _, _, _, _ in voxels)
    min_y = min(y for _, y, _, _, _, _ in voxels)
    min_z = min(z for _, _, z, _, _, _ in voxels)
    max_x = max(x for x, _, _, _, _, _ in voxels)
    max_y = max(y for _, y, _, _, _, _ in voxels)
    max_z = max(z for _, _, z, _, _, _ in voxels)

    w = max_x - min_x + 1
    h = max_y - min_y + 1
    l = max_z - min_z + 1
    blocks = [0] * (w * h * l)
    data = [0] * (w * h * l)

    for x, y, z, r, g, b in voxels:
        bid, bdata = map_rgb_to_block((r, g, b))
        idx = voxel_index(w, l, x - min_x, y - min_y, z - min_z)
        blocks[idx] = bid
        data[idx] = bdata

    make_schematic(filename, w, h, l, blocks, data)


def gothic_cathedral_voxels():
    v = []
    dark_stone = (48, 48, 56)
    stone = (80, 80, 88)
    light_stone = (110, 108, 116)
    stained_r = (160, 32, 32)
    stained_b = (32, 48, 160)
    stained_g = (32, 140, 48)
    stained_p = (120, 40, 160)
    gold = (220, 180, 40)
    dark_floor = (36, 34, 40)
    slate = (64, 62, 72)

    for x in range(20):
        for z in range(12):
            v.append((x, 0, z, *dark_floor))

    for y in range(1, 15):
        for x in range(2, 18):
            if 7 <= x <= 12 and 4 <= y <= 10:
                continue
            color = light_stone if y % 3 == 0 else stone
            v.append((x, y, 0, *color))
            v.append((x, y, 11, *color))

    for y in range(1, 15):
        for z in range(1, 11):
            color = light_stone if y % 3 == 0 else stone
            v.append((2, y, z, *color))
            v.append((17, y, z, *color))

    for i in range(4):
        bx = 4 + i * 3
        edge_z = 11 if bx > 10 else 0
        for y in range(1, 9 - (i % 2)):
            v.append((1, y, edge_z, *dark_stone))
            v.append((18, y, edge_z, *dark_stone))
        v.append((1, 9 - (i % 2), edge_z, *slate))
        v.append((18, 9 - (i % 2), edge_z, *slate))

    for bi in range(3):
        bz = 2 + bi * 4
        for y in range(1, 11):
            v.append((0, y, bz, *dark_stone))
            v.append((0, y, bz + 1, *dark_stone))
            v.append((19, y, bz, *dark_stone))
            v.append((19, y, bz + 1, *dark_stone))
        v.extend([
            (1, 10, bz, *slate), (1, 10, bz + 1, *slate),
            (18, 10, bz, *slate), (18, 10, bz + 1, *slate),
            (1, 11, bz, *slate), (18, 11, bz, *slate),
        ])

    stained = [stained_r, stained_b, stained_g, stained_p]
    for x in range(8, 12):
        for y in range(5, 10):
            color = stained[(x + y) % 4]
            v.append((x, y, 0, *color))
            v.append((x, y, 11, *color))

    center_x, center_y = 10, 12
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            dist = math.sqrt(dx * dx + dy * dy)
            if 0.8 <= dist <= 2.3:
                color = stained[(dx + dy + 4) % 4]
                v.append((center_x + dx, center_y + dy, 0, *color))
    v.append((center_x, center_y, 0, *gold))

    for y in range(15, 21):
        roof_width = max(0, 8 - (y - 15) * 2)
        start_x = 10 - roof_width // 2
        end_x = 10 + math.ceil(roof_width / 2)
        for x in range(start_x, end_x + 1):
            for z in range(1, 11):
                if x == start_x or x == end_x:
                    v.append((x, y, z, *slate))

    for z in range(12):
        v.append((10, 21, z, *dark_stone))

    for y in range(15, 29):
        radius = 2 if y < 22 else 1
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if abs(dx) == radius or abs(dz) == radius:
                    v.append((10 + dx, y, 6 + dz, *dark_stone))
    v.extend([(10, 29, 6, *gold), (10, 30, 6, *gold)])

    for y in range(1, 23):
        for dx in range(3):
            for dz in range(3):
                if dx in (0, 2) or dz in (0, 2):
                    v.append((2 + dx, y, dz, *dark_stone))
                    v.append((15 + dx, y, dz, *dark_stone))

    for y in range(23, 27):
        radius = 1 if y < 25 else 0
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                v.append((3 + dx, y, 1 + dz, *slate))
                v.append((16 + dx, y, 1 + dz, *slate))
    v.extend([(3, 27, 1, *gold), (16, 27, 1, *gold)])

    for y in range(1, 14):
        v.extend([
            (5, y, 3, *light_stone), (5, y, 8, *light_stone),
            (10, y, 3, *light_stone), (10, y, 8, *light_stone),
            (14, y, 3, *light_stone), (14, y, 8, *light_stone),
        ])

    for x in range(8, 13):
        for z in range(9, 11):
            v.append((x, 1, z, *light_stone))
    v.extend([(10, 2, 10, *gold), (10, 3, 10, *gold)])

    for y in range(1, 7):
        for x in range(8, 12):
            if y <= 4:
                continue
            v.append((x, y, 0, *dark_stone))
    v.extend([
        (8, 5, 0, *stone), (11, 5, 0, *stone),
        (9, 6, 0, *stone), (10, 6, 0, *stone),
    ])
    return v


def cherry_tree_voxels():
    v = []
    trunk = (200, 128, 112)
    bark = (120, 80, 48)
    pink1 = (240, 160, 184)
    pink2 = (232, 125, 160)
    pink3 = (255, 192, 208)
    grass = (136, 192, 112)
    petal = (255, 180, 200)

    for x in range(14):
        for z in range(14):
            v.append((x, 0, z, *grass))

    for px, pz in [(2, 3), (5, 1), (8, 4), (1, 8), (4, 11), (10, 2), (12, 8), (3, 6), (9, 10), (6, 13)]:
        v.append((px, 1, pz, *petal))

    for y in range(1, 8):
        v.extend([
            (6, y, 6, *trunk), (7, y, 6, *trunk),
            (6, y, 7, *trunk), (7, y, 7, *trunk),
        ])

    v.extend([
        (5, 5, 6, *bark), (5, 6, 5, *bark),
        (8, 4, 7, *bark), (8, 5, 8, *bark),
    ])

    for i in range(3):
        v.extend([
            (4 - i, 7 + i, 6, *bark),
            (9 + i, 7 + i, 7, *bark),
            (6, 7 + i, 3 - i, *bark),
            (7, 7 + i, 10 + i, *bark),
        ])

    cx, cy, cz = 7, 11, 7
    for x in range(2, 12):
        for y in range(8, 15):
            for z in range(2, 12):
                dx = x - cx
                dy = (y - cy) * 0.8
                dz = z - cz
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                if dist < 4.5 and ((x * 31 + y * 17 + z * 13) % 100) > 11:
                    color = pink2 if dist < 2.5 else pink1 if dist < 3.8 else pink3
                    v.append((x, y, z, *color))
    return v


def japanese_temple_voxels():
    v = []
    dark_wood = (62, 42, 28)
    oak = (176, 138, 80)
    red = (180, 36, 36)
    dark_red = (120, 24, 24)
    stone = (140, 140, 136)
    dark_roof = (40, 36, 32)
    gold = (220, 180, 40)
    tatami = (192, 176, 120)
    paper = (240, 236, 220)
    moss = (80, 128, 64)

    for x in range(16):
        for z in range(14):
            v.append((x, 0, z, *stone))
    for x in range(1, 15):
        for z in range(1, 13):
            v.append((x, 1, z, *stone))

    for px, pz in [(0, 2), (15, 5), (2, 0), (13, 13), (0, 10), (15, 1)]:
        v.append((px, 1, pz, *moss))

    for x in range(2, 14):
        for z in range(2, 12):
            v.append((x, 2, z, *tatami))

    pillars = [(2, 2), (2, 6), (2, 11), (7, 2), (7, 6), (7, 11), (13, 2), (13, 6), (13, 11)]
    for px, pz in pillars:
        for y in range(3, 11):
            v.append((px, y, pz, *red))

    for y in range(3, 11):
        v.extend([
            (2, y, 2, *dark_red), (13, y, 2, *dark_red),
            (2, y, 11, *dark_red), (13, y, 11, *dark_red),
        ])

    for x in range(3, 7):
        for y in range(3, 7):
            v.append((x, y, 2, *paper))
            v.append((x, y, 11, *paper))
    for x in range(8, 13):
        for y in range(3, 7):
            v.append((x, y, 2, *paper))
            v.append((x, y, 11, *paper))
    for z in range(3, 6):
        for y in range(3, 7):
            v.append((2, y, z, *paper))
            v.append((13, y, z, *paper))
    for z in range(7, 11):
        for y in range(3, 7):
            v.append((2, y, z, *paper))
            v.append((13, y, z, *paper))

    for x in range(2, 14):
        v.extend([
            (x, 7, 2, *dark_wood), (x, 7, 11, *dark_wood),
            (x, 10, 2, *dark_wood), (x, 10, 11, *dark_wood),
        ])
    for z in range(2, 12):
        v.extend([
            (2, 7, z, *dark_wood), (13, 7, z, *dark_wood),
            (2, 10, z, *dark_wood), (13, 10, z, *dark_wood),
        ])

    for x in range(3, 13):
        for z in range(3, 11):
            v.append((x, 7, z, *oak))

    for y in range(11, 14):
        overhang = y - 10
        for x in range(1 - overhang, 15 + overhang):
            for z in range(1 - overhang, 13 + overhang):
                if z in (1 - overhang, 12 + overhang) or x in (1 - overhang, 14 + overhang):
                    v.append((x, y, z, *dark_roof))
        for x in range(1 - overhang + 2, 15 + overhang - 2):
            v.append((x, y, 1 - overhang + 2, *dark_roof))
            v.append((x, y, 12 + overhang - 2, *dark_roof))
        for z in range(1 - overhang + 2, 12 + overhang - 1):
            v.append((1 - overhang + 2, y, z, *dark_roof))
            v.append((14 + overhang - 2, y, z, *dark_roof))

    for x in range(1, 15):
        for z in range(1, 13):
            v.append((x, 11, z, *dark_roof))
    for x in range(16):
        v.append((x, 10, 0, *dark_roof))
        v.append((x, 10, 13, *dark_roof))
    for z in range(14):
        v.append((0, 10, z, *dark_roof))
        v.append((15, 10, z, *dark_roof))
    v.extend([
        (0, 11, 0, *dark_roof), (15, 11, 0, *dark_roof),
        (0, 11, 13, *dark_roof), (15, 11, 13, *dark_roof),
    ])

    for y in range(12, 16):
        v.extend([
            (5, y, 4, *red), (10, y, 4, *red),
            (5, y, 9, *red), (10, y, 9, *red),
        ])
    for x in range(3, 13):
        for z in range(3, 11):
            v.append((x, 16, z, *dark_roof))
    for x in range(2, 14):
        v.append((x, 15, 2, *dark_roof))
        v.append((x, 15, 11, *dark_roof))
    for z in range(2, 12):
        v.append((2, 15, z, *dark_roof))
        v.append((13, 15, z, *dark_roof))
    v.extend([
        (2, 16, 2, *dark_roof), (13, 16, 2, *dark_roof),
        (2, 16, 11, *dark_roof), (13, 16, 11, *dark_roof),
    ])

    for x in range(5, 11):
        v.append((x, 17, 7, *dark_roof))
    v.extend([
        (6, 18, 7, *dark_roof), (7, 18, 7, *dark_roof),
        (8, 18, 7, *dark_roof), (9, 18, 7, *dark_roof),
        (7, 19, 7, *dark_roof), (8, 19, 7, *dark_roof),
        (7, 20, 7, *gold), (8, 20, 7, *gold),
        (7, 21, 7, *gold), (8, 21, 7, *gold),
    ])

    for y in range(3, 9):
        v.append((6, y, 0, *red))
        v.append((9, y, 0, *red))
    for x in range(5, 11):
        v.append((x, 8, 0, *dark_wood))
        v.append((x, 9, 0, *dark_roof))
    v.extend([
        (5, 3, 1, *gold), (10, 3, 1, *gold),
        (5, 4, 1, *paper), (10, 4, 1, *paper),
    ])
    for z in range(0, 2):
        for x in range(7, 9):
            v.append((x, 1, z, *stone))
    return v


make_voxel_schematic('samples/dark_gothic_cathedral.schematic', gothic_cathedral_voxels())
make_voxel_schematic('samples/cherry_tree.schematic', cherry_tree_voxels())
make_voxel_schematic('samples/japanese_temple.schematic', japanese_temple_voxels())

print('\nAll done!')
