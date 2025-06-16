from Modules import SamCDMA_RLE, SamCDMA_RLE12, SamCDMA_LZCMK, SamCDMA_LZSS
from construct import *
import argparse
import os
import struct
from PIL import Image

HugeEntry = Struct(
    "type" / Int8ub,
    "unk" / Int8ub,
    "width" / Int8ub,
    "height" / Int8ub,
    "size" / Int16ub,
    "frames" / Int16ub,
    "speed_ms" / Int16ub,
    "output_type" / Int16ub,
    "smallentry_offset" / Int32ub
)

SmallEntry = Struct(
    "type" / Int8ub,
    "unk" / Int8ub,
    "width" / Int8ub,
    "height" / Int8ub,
    "size" / Int16ub,
    "output_type" / Int16ub,
    "smallentry_offset" / Int32ub
)

def parse_entries(bdata, offset, start_offset, cnt):
    entries = []
    for _ in range(cnt):
        entry = HugeEntry.parse(bdata[offset:offset+HugeEntry.sizeof()])
        ###### some stupidity makes the values be read in big endian
        entry.type = struct.unpack("<B", entry.type.to_bytes(1, "big"))[0]
        entry.unk = struct.unpack("<B", entry.unk.to_bytes(1, "big"))[0]
        entry.width = struct.unpack("<B", entry.width.to_bytes(1, "big"))[0]
        entry.height = struct.unpack("<B", entry.height.to_bytes(1, "big"))[0]
        entry.size = struct.unpack("<H", entry.size.to_bytes(2, "big"))[0]
        entry.frames = struct.unpack("<H", entry.frames.to_bytes(2, "big"))[0]
        entry.speed_ms = struct.unpack("<H", entry.speed_ms.to_bytes(2, "big"))[0]
        entry.output_type = struct.unpack("<H", entry.output_type.to_bytes(2, "big"))[0]
        entry.smallentry_offset = struct.unpack("<L", entry.smallentry_offset.to_bytes(4, "big"))[0]
        tmp_offset = entry.smallentry_offset + start_offset
        if tmp_offset <= len(bdata):
            img_frame_entries = []
            for a in range(entry.frames):
                frame_entry = SmallEntry.parse(bdata[tmp_offset:tmp_offset+SmallEntry.sizeof()])
                ###### some stupidity makes the values be read in big endian
                frame_entry.type = struct.unpack("<B", frame_entry.type.to_bytes(1, "big"))[0]
                frame_entry.unk = struct.unpack("<B", frame_entry.unk.to_bytes(1, "big"))[0]
                frame_entry.width = struct.unpack("<B", frame_entry.width.to_bytes(1, "big"))[0]
                frame_entry.height = struct.unpack("<B", frame_entry.height.to_bytes(1, "big"))[0]
                frame_entry.size = struct.unpack("<H", frame_entry.size.to_bytes(2, "big"))[0]
                frame_entry.output_type = struct.unpack("<H", frame_entry.output_type.to_bytes(2, "big"))[0]
                frame_entry.smallentry_offset = struct.unpack("<L", frame_entry.smallentry_offset.to_bytes(4, "big"))[0]
                frame_entry.smallentry_offset += start_offset
                img_frame_entries.append(frame_entry)
                tmp_offset += SmallEntry.sizeof()
            entries.append([entry, img_frame_entries])
        offset += HugeEntry.sizeof()
    return entries

if __name__ == "__main__":
    ap = argparse.ArgumentParser("samcdma_itblextract")
    
    ap.add_argument("in_file")
    ap.add_argument("tbl_offset")
    ap.add_argument("start_offset")
    ap.add_argument("cnt", type=int)
    ap.add_argument("out_folder")
    
    args = ap.parse_args()

    if not (os.path.exists(args.out_folder)):	os.mkdir(args.out_folder)	

    ftmp = open(args.in_file, "rb").read()
    
    entries = parse_entries(ftmp, int(args.tbl_offset, 16), int(args.start_offset, 16), args.cnt)

    out_img_data = bytearray(240*320*4)

    for i, entry_info in enumerate(entries):
        entry, img_frame_entries = entry_info
        print(f"Processing entry {i}")
        frame = 0
        for frame_entry in img_frame_entries:
            try:
                frame_data = ftmp[frame_entry.smallentry_offset:frame_entry.smallentry_offset+(frame_entry.size*2)]
                if frame_entry.type == 0x0:
                    out_img_data[:]=frame_data
                elif frame_entry.type == 0x1:
                    SamCDMA_RLE.decode(frame_data, out_img_data, frame_entry.width * frame_entry.height * 2)
                elif frame_entry.type == 0x2:
                    SamCDMA_RLE12.decode(frame_data, out_img_data, frame_entry.width * frame_entry.height * 2)
                elif frame_entry.type == 0x3:
                    SamCDMA_LZCMK.decode(frame_data, out_img_data, frame_entry.width * frame_entry.height * 2, False)
                elif frame_entry.type == 0x4:
                    SamCDMA_LZSS.decode(frame_data, out_img_data)
                else:
                    print(f"Unknown frame type {frame_entry.type}")
                    continue
                try:
                    Image.frombuffer("RGB", (frame_entry.width, frame_entry.height), out_img_data, "raw", "BGR;16").save(f"{args.out_folder}/IMG_{i}_{frame}.png")
                except:
                    pass
            except:
                continue
            frame += 1