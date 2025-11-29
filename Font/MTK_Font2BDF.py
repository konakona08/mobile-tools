from construct import *
import struct
from io import BytesIO
from PIL import Image

FontInfo = Struct (
    "height" / Int8ul,
    "width" / Int8ul,
    "ascent" / Int8ul,
    "descent" / Int8ul,
    "equidistant" / Int8ul,
    "char_bytes" / Int8ul,
    "max_chars" / Int16ul,
    "dwidth_ptr" / Int32ul,
    "width_ptr" / Int32ul,
    "offset_ptr" / Int32ul,
    "data_ptr" / Int32ul,
    "range" / Int32ul,
    "range_detail" / Int32ul
)

RangeInfo = Struct (
    "count" / Int32ul,
    "offset" / Int32ul
)

RangeData = Struct (
    "min" / Int16ul,
    "max" / Int16ul,
)

def cvt_1_to_8(data):
    curr_sz = len(data)
    new_sz = len(data)*8
    new_data = bytearray(new_sz)
    for i in range(curr_sz):
        for bit in range(8):
            new_data[i*8+bit] = (data[i] >> bit) & 1
    return new_data

def convert_to_pil_image(data, width, height):
    img = Image.new("1", (width, height))
    for y in range(height):
        for x in range(width):
            if data[y*width+x] == 0:
                img.putpixel((x, y), 0)
            else:
                img.putpixel((x, y), 255)
    return img

if __name__ == "__main__":
    import sys
    fd = open(sys.argv[1], "rb")
    offset = int(sys.argv[2], 16)
    offset_remap = int(sys.argv[3], 16)
    print(offset_remap)
    is_compress = int(sys.argv[4])
    fd.seek(offset)
    font_info = FontInfo.parse(fd.read(FontInfo.sizeof()))
    font_info.dwidth_ptr -= offset_remap
    font_info.width_ptr -= offset_remap
    font_info.offset_ptr -= offset_remap
    font_info.data_ptr -= offset_remap
    font_info.range -= offset_remap
    font_info.range_detail -= offset_remap

    w,h = font_info.width, font_info.height
    a,d = font_info.ascent, font_info.descent
    eq = font_info.equidistant
    
    print(f"Font info: {font_info}")

    widths = []
    fd.seek(font_info.width_ptr)
    for i in range(font_info.max_chars):
        widths.append(struct.unpack("<B", fd.read(1))[0])
    offsets = []
    fd.seek(font_info.offset_ptr)
    for i in range(font_info.max_chars):
        if is_compress:
            offsets.append(struct.unpack("<B", fd.read(1))[0])
        else:
            offsets.append(struct.unpack("<L", fd.read(4))[0])

    fd.seek(font_info.range_detail)
    range_info = RangeInfo.parse(fd.read(RangeInfo.sizeof()))

    range_info.offset -= offset_remap

    print(range_info)

    fd.seek(range_info.offset)
    range_detail = fd.read(range_info.count * RangeData.sizeof())
    range_detail = [RangeData.parse(range_detail[i*RangeData.sizeof():(i+1)*RangeData.sizeof()]) for i in range(range_info.count)]

    count = 0
    for _ in range(range_info.count):
        count += range_detail[_].max - range_detail[_].min + 1
    print(count)

    fd.seek(font_info.data_ptr)
    data = BytesIO(fd.read())

    curr_range = 0
    cur_range_idx = 0
    cur_range_unicode = range_detail[cur_range_idx].min

    for i in range(font_info.max_chars):
        data.seek(offsets[i])
        char_size = ((widths[i]*h)+7)//4
        char_data = data.read(char_size)
        char_data = cvt_1_to_8(char_data)
        cur_range_idx += 1
        convert_to_pil_image(char_data, widths[i], h).save(f"{sys.argv[1]}_ext/{cur_range_unicode}-{cur_range_unicode:04x}.png")
        cur_range_unicode += 1
        if cur_range_unicode > range_detail[curr_range].max:
            curr_range += 1
            if curr_range >= range_info.count:
                break
            cur_range_unicode = range_detail[curr_range].min

