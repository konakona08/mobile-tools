import os
import binascii
from Modules import MTKLZMA, GFH, VIVA
import subprocess

SynthInfo = [
    ["WT600K", 0xc89f817c, 0xac658],
    ["WT150K", 0x7d7977c6, 0x271e8],
    ["WT70K", 0x4eb89574, 0x11ac8],
    ["WT20K", 0x518b42d6, 0x5420],
    ["WT20K (Ultra Slim)", 0x008c097d, 0x2cc0]
]

##determine next path char
if os.name == "nt":
    next_path_char = "\\"
else:
    next_path_char = "/"

syn_header = open(os.path.join(os.path.dirname(__file__), "MTK_SynHeader"), "rb").read()

def decompress_zimage(file_path, buffer):
    #########try decompressing alice then zimage
    alice_offset = buffer.find(b"ALICE_")
    found = False
    zimage_data = None
    while True:
        if buffer[alice_offset:alice_offset+6] == b"ALICE_":
            print("Decompressing alice...")
            found = True
            abs_path = os.path.abspath(file_path)
            dir_path = os.path.dirname(abs_path)
            offset = f"{alice_offset:08x}"
            unalice_path = os.path.join(os.path.dirname(__file__), "unalice.py")
            alice_path = os.path.join(dir_path, "~alice_temp_dec.bin")
            
            subprocess.call(f"python {unalice_path} {abs_path} {alice_path} {offset}", shell=True)

            zImageDict = open(alice_path, "rb").read()[:0x400000]
            gfs = GFH.findGFH(open(abs_path, "rb").read())
            for f in gfs:
                fileinfo, filedata = f
                if fileinfo.info_type == 0x108:
                    VIVAHead = VIVA.VIVA.parse(filedata[fileinfo.info_content_offset:])    
                    
                    zImage = VIVA.zPartition.parse(filedata[VIVAHead.zimage:])           
                    
                    zimage_data = []

                    for part in zImage.partitions:                
                        try:
                            if part.compression_type == 3: # 3 = LZMA with Train from ALICE
                                zimage_data.append(MTKLZMA.transformProcess(MTKLZMA.decompress(part.data, zImageDict)))
                            else: # 0 = LZMA, 1 = LZMA with callback, 2 = Same as 0
                                zimage_data.append(MTKLZMA.transformProcess(MTKLZMA.decompress(part.data))) 
                        except Exception as e:
                            print(f"Fail to decompress ZIMAGE -> {e}")
                            sys.exit(1)
                    
                    zimage_data = b"".join(zimage_data)
                    ### delete file
                    os.remove(alice_path)
        else:
            alice_offset = buffer.find(b"ALICE_", alice_offset + 6)
        
        if found:
            break
        if alice_offset == -1:
            break
    
    return zimage_data

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Not enough arguments! usage: {sys.argv[0]} <.bin file>", file=sys.stderr)
        sys.exit(1)
    fd = open(sys.argv[1], "rb")

    ftmp = fd.read()
    
    offset = ftmp.find(syn_header)
    found = False
    while True:
        if ftmp[offset:offset+len(syn_header)] == syn_header:
            print(f"Found header at {offset:08x}")
            for synth in SynthInfo:
                data = ftmp[offset:offset+synth[2]]
                if binascii.crc32(data) == synth[1]:
                    found = True
                    print(f"{synth[0]}")
        else:
            offset = ftmp.find(syn_header, offset+len(syn_header))
        
        if found:
            break
        if offset == -1:
            break
    
    if not found:
        print("WTSyn not found in ROM, decompressing zimage...")
        ftmp = decompress_zimage(sys.argv[1], ftmp)
        if ftmp == None:
            print("Failed decompressing zimage")
            sys.exit(1)
        offset = ftmp.find(syn_header)
        found = False

        while True:
            if ftmp[offset:offset+len(syn_header)] == syn_header:
                print(f"Found header at {offset:08x}")
                for synth in SynthInfo:
                    data = ftmp[offset:offset+synth[2]]
                    if binascii.crc32(data) == synth[1]:
                        found = True
                        print(f"{synth[0]}")
            else:
                offset = ftmp.find(syn_header, offset+len(syn_header))
            
            if found:
                break
            if offset == -1:
                break

        if not found:
            print("Failed finding WTSyn")