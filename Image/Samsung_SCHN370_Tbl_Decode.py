from construct import *
from PIL import Image
import os
import sys

def convert_to_pil_image(img_data, wdt, hgt):
	rows = (hgt + 7) // 8  # This is equivalent to ceil(hgt/8)
	img = Image.new('1', (wdt, hgt))
	pixels = img.load()

	for x in range(wdt):
		for y in range(rows):
			byte = img_data[wdt * y + x]
			for bit in range(8):
				y_pos = y*8+bit
				if y_pos < hgt :
					pixels[x, y_pos] = ((byte >> bit) & 1) == 0

	return img

TableEntry = Struct(
    "width" / Int8ul,
    "height" / Int8ul,
    "unk1" / Int16ul, 
    "unk2" / Int32ul,
    "offset" / Int32ul
)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Not enough arguments! usage: {sys.argv[0]} file offs cnt", file=sys.stderr)
        sys.exit(1)

    fd = open(sys.argv[1], "rb")
    if not (os.path.exists(sys.argv[1] + "_ext")):	os.mkdir(sys.argv[1] + "_ext")
    fd.seek(int(sys.argv[2], 16))

    table_entries = []

    for i in range(int(sys.argv[3])):
        table_entries.append(TableEntry.parse(fd.read(TableEntry.sizeof())))

    for i, entry in enumerate(table_entries):
        try:
            fd.seek(entry.offset)
            img_data = fd.read(entry.width * ((entry.height+7) // 8))
            convert_to_pil_image(img_data, entry.width, entry.height).save(f"{sys.argv[1]}_ext/{i}.png")
        except Exception as e:
            print(f"Error at {i}: {e}")
            pass