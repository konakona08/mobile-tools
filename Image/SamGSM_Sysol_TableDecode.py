from Modules import SamGSM_MF04, SamGSM_SysolRLE
import struct
import os
import sys
from construct import *
from PIL import Image
import argparse

EntryHeader = Struct (
        "width" / Int16ul,
        "height" / Int16ul,
        "unknown" / Int32ul,
        "dest_type" / Int8ul,
        "src_type" / Int8ul,
        "pad" / Int16ul,
        "offset" / Int32ul,
        "anim_ms" / Int16ul,
        "pad2" / Int16ul,
        "unknown2" / Int16ul,
        "unknown3" / Int16ul
)

def parse_entries(bdata, offset, cnt):
    entries = []
    for _ in range(cnt):
        entry = EntryHeader.parse(bdata[offset:offset+EntryHeader.sizeof()])
        entries.append(entry)
        ###### some stupidity makes the values be read in big endian
        entry.width = struct.unpack("<H", entry.width.to_bytes(2, "big"))[0]
        entry.height = struct.unpack("<H", entry.height.to_bytes(2, "big"))[0]
        entry.unknown = struct.unpack("<L", entry.unknown.to_bytes(4, "big"))[0]
        entry.offset = struct.unpack("<L", entry.offset.to_bytes(4, "big"))[0]
        entry.anim_ms = struct.unpack("<H", entry.anim_ms.to_bytes(2, "big"))[0]
        entry.unknown2 = struct.unpack("<H", entry.unknown2.to_bytes(2, "big"))[0]
        entry.unknown3 = struct.unpack("<H", entry.unknown3.to_bytes(2, "big"))[0]
        offset += EntryHeader.sizeof()
    return entries

if __name__ == "__main__":
    ap = argparse.ArgumentParser("samgsm_sysol_itblextract")
    
    ap.add_argument("in_file")
    ap.add_argument("tbl_offset")
    ap.add_argument("cnt", type=int)
    ap.add_argument("out_folder")
    
    args = ap.parse_args()

    if not (os.path.exists(args.out_folder)):
        os.mkdir(args.out_folder)   

    ftmp = open(args.in_file, "rb").read()
    
    entries = parse_entries(ftmp, int(args.tbl_offset, 16), args.cnt)

    for i, entry_info in enumerate(entries):
        entry = entry_info
        print(f"Processing entry {i}")
        #print(entry)
        frame = 0
        try:
            frame_data = ftmp[entry.offset:]
            print(f"dest_type = {entry.dest_type}, src_type = {entry.src_type}, offset = {hex(entry.offset)}")
            if entry.dest_type == 0x3:
                bpp = 16
                out_type = "BGR;16"
            else:
                print(f"Unknown BPP type {entry.dest_type}")
                continue

            out_img_data = bytearray((entry.width+(4 - (entry.width % 4))) * (entry.height+(entry.height%2)) * bpp // 8)

            if entry.src_type == 6:
                size = entry.width * entry.height * bpp // 8
                out_img_data[:]=frame_data[:size]
            elif entry.src_type == 11:
                SamGSM_SysolRLE.decode(frame_data, out_img_data, entry.width * entry.height * bpp // 8)
            elif entry.src_type == 12:
                SamGSM_MF04.decode(frame_data, out_img_data)
            else:
                print(f"Unknown encoding type {entry.src_type}")
                continue
            try:
                Image.frombuffer("RGB", (entry.width, entry.height), out_img_data, "raw", out_type).save(f"{args.out_folder}/IMG_{i}_{frame}.png")
            except Exception as e:
                print("Error writing to image: ", e)
                pass
        except Exception as e:
            print("error: ", e)
            continue
        frame += 1