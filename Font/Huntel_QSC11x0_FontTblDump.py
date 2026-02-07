import struct
import os
import sys
from PIL import Image

def convert_to_pil_image_1bpp(img_data, wdt, hgt):
    rows = (hgt + 7) // 8  # This is equivalent to ceil(hgt/8)
    img = Image.new('1', (wdt, hgt))
    pixels = img.load()

    for x in range(wdt):
        for y in range(rows):
            byte = img_data[wdt * y + x]
            for bit in range(8):
                y_pos = y*8+(7-bit)
                if y_pos < hgt :
                    pixels[x, y_pos] = ((byte >> bit) & 1) == 0

    return img

if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    f.seek(int(sys.argv[2], 16))
    
    entry_map = []
    
    for a in range(int(sys.argv[3])):
        unicode, c_bmp = struct.unpack("<LL", f.read(0x8))

        entry_map.append([unicode, c_bmp])
    
    if not (os.path.exists(sys.argv[1] + "_ext_font")):  os.mkdir(sys.argv[1] + "_ext_font")  
    
    for a in range(len(entry_map)):
        f.seek(entry_map[a][1])
        w,h = struct.unpack("<BB", f.read(0x2))
        bmp = f.read()
        convert_to_pil_image_1bpp(bmp,w,h).save(f"{sys.argv[1]}_ext_font/char_{hex(entry_map[a][0])}.png")
        