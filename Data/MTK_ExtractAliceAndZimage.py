import os
import binascii
from Modules import MTKLZMA, GFH, VIVA
import subprocess

##determine next path char
if os.name == "nt":
    next_path_char = "\\"
else:
    next_path_char = "/"

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
            filename = os.path.basename(abs_path)
            offset = f"{alice_offset:08x}"
            unalice_path = os.path.join(os.path.dirname(__file__), "unalice.py")
            alice_path = os.path.join(dir_path, f"~{filename}_alice.bin")
            
            subprocess.call(f"python {unalice_path} {abs_path} {alice_path} {offset}", shell=True)

            zImageDict = open(alice_path, "rb").read()[:0x400000]
            gfs = GFH.findGFH(open(abs_path, "rb").read())

            zimage_file = os.path.join(dir_path, f"~{filename}_zimage.bin")

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
                    
                    with open(zimage_file, "wb") as f:
                        f.write(b"".join(zimage_data))
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
    
    decompress_zimage(sys.argv[1], ftmp)