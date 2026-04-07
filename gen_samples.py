import gzip, struct, io, os

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

print('\nAll done!')
