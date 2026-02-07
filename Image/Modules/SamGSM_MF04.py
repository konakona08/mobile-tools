from io import BytesIO
import struct

def paletteto565(palette):
    new_palette = []
    for a in range(256):
        b,g,r = palette[a*3] & 0xff, palette[a*3+1] & 0xff, palette[a*3+2] & 0xff
        new_palette.append((r >> 3) << 11 | (g >> 2) << 5 | b >> 3)
    return new_palette

def decode(in_data, out_data):
    in_data = BytesIO(in_data)
    assert in_data.read(4) == b"MF04", "Invalid MF04 data"
    width, height, size = struct.unpack(">HHL", in_data.read(8))
    assert len(out_data) >= width * height * 2, "Out buffer has wrong size"
    palette = paletteto565(in_data.read(0x300))
    tableData = in_data.read(size)
    if size % 4:
        in_data.read(4 - (size % 4))

    flags_len = struct.unpack(">L", in_data.read(4))[0]    
    flags = []
    for b in in_data.read(flags_len):
        for p in range(8):
            flags.append((b >> p) & 1)

    lentbl_len = struct.unpack(">H", in_data.read(2))[0]
    lentbl = []

    for l in in_data.read(lentbl_len):
        lentbl.append(l >> 4)
        lentbl.append(l & 15)

    lentbl_offset = 0
    data_offset = 0

    out_offs = 0
    
    for f in flags:
        pixel = palette[tableData[data_offset]]
        if f == 1:
            for c in range(lentbl[lentbl_offset]+2):
                out_data[out_offs+c*2:out_offs+c*2+2] = bytes([pixel&0xff, pixel>>8])
            out_offs += (lentbl[lentbl_offset]+2)*2
            lentbl_offset += 1
            data_offset += 1
        else:
            out_data[out_offs:out_offs+2] = bytes([pixel&0xff, pixel>>8])
            out_offs += 2
            data_offset += 1

        if data_offset >= len(tableData): break
    
    # flip image, swap rows
    for y in range(height//2):
        r1 = y
        r2 = height-y-1
        for x in range(width):
            row_1 = out_data[r1*width*2+x*2:r1*width*2+x*2+2]
            row_2 = out_data[r2*width*2+x*2:r2*width*2+x*2+2]
            out_data[r1*width*2+x*2:r1*width*2+x*2+2] = row_2
            out_data[r2*width*2+x*2:r2*width*2+x*2+2] = row_1