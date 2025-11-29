from construct import *
import argparse
import os
import struct
from PIL import Image

Entry = Struct(
    "size" / Int32ub,
    "width" / Int8ub,
    "height" / Int8ub,
    "type" / Int16ub,
    "offset" / Int32ub,
    "title" / Bytes(8)
)

def parse_entries(bdata, offset, cnt):
    entries = []
    for _ in range(cnt):
        entry = Entry.parse(bdata[offset:offset+Entry.sizeof()])
        ###### some stupidity makes the values be read in big endian
        entry.size = struct.unpack("<L", entry.size.to_bytes(4, "big"))[0]
        entry.type = struct.unpack("<H", entry.type.to_bytes(2, "big"))[0]
        entry.offset = struct.unpack("<L", entry.offset.to_bytes(4, "big"))[0]
        entries.append(entry)
        offset += Entry.sizeof()
    return entries

if __name__ == "__main__":
    ap = argparse.ArgumentParser("samcdma_imrctblextract")
    
    ap.add_argument("in_file")
    ap.add_argument("imrc_dec_file")
    ap.add_argument("tbl_offset")
    ap.add_argument("cnt", type=int)
    ap.add_argument("out_folder")

    args = ap.parse_args()

    if not (os.path.exists(args.out_folder)):	os.mkdir(args.out_folder)	

    ftmp = open(args.in_file, "rb").read()
    imrc_data = open(args.imrc_dec_file, "rb").read()
    
    entries = parse_entries(ftmp, int(args.tbl_offset, 16), args.cnt)

    for i, entry in enumerate(entries):
        print(f"Processing entry {i} at offset {entry.offset:08x}")
        data = imrc_data[entry.offset:entry.offset+entry.size]
        ##guess by header the extension
        title = entry.title.decode("utf-8").strip("\x00")
        is_image = False
        if entry.width > 0 and entry.height > 0:
            ext = "png"
            is_image = True
        elif data[0:4] == b'MThd':
            ext = "mid"
        elif data[0:4] == b'\x89PNG':
            ext = "png"
        elif data[0:4] == b'\x11\0\1\0':
            ext = "bar"
        elif struct.unpack(">H", data[0:2])[0] & 0xFF00 == 0xFF00 or data[0:3] == b"ID3":
            ext = "mp3"
        else:
            ext = "bin"
        if is_image:
            Image.frombuffer("RGB", (entry.width, entry.height), data, "raw", "BGR;16").save(f"{args.out_folder}/{title}.{ext}")
        else:
            open(f"{args.out_folder}/{title}.{ext}", "wb").write(data)
