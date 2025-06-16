import struct
import os
import sys
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser("anychn_ringoff_dump_smaf_codefont")
    ap.add_argument("code_file")
    ap.add_argument("font_file")
    ap.add_argument("tbl_offset")
    ap.add_argument("font_mem_offset")
    ap.add_argument("cnt", type=int)
    ap.add_argument("out_folder")
    args = ap.parse_args()
    if not (os.path.exists(args.out_folder)): os.mkdir(args.out_folder)
    
    tbl_fd = open(args.code_file, "rb")
    tbl_fd.seek(int(args.tbl_offset, 16))

    font_fd = open(args.font_file, "rb")
    
    offs = []
    for i in range(args.cnt):
        off = struct.unpack("<L", tbl_fd.read(4))[0]
        offs.append(off - int(args.font_mem_offset, 16))
        
    for i, off in enumerate(offs):
        print(f"Processing entry {i} at offset {off:08x}")
        font_fd.seek(off)
        smaf_data = font_fd.read()
        if smaf_data[0:4] != b"MMMD":
            continue
        size = struct.unpack(">L", smaf_data[4:8])[0]
        with open(f"{args.out_folder}/{i}.mmf", "wb") as f:
            f.write(smaf_data[:size+8])

    tbl_fd.close()
    font_fd.close()

