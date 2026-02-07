import struct
import sys
import os
from io import BytesIO
from PIL import Image

def decompress_data(data, size, bpp):
	if isinstance(data, bytearray) or isinstance(data, bytes):
		data = BytesIO(data)
		
	result = bytearray()
	while data.tell() < size:
		p = struct.unpack("<B", data.read(1))[0]
		is_packed = p&0x80
		cnt = p&0x7f
		if is_packed:
			pel = data.read(bpp)
			for i in range(cnt+2):
				result += pel
		else:
			pel = data.read((cnt+1)*bpp)
			result += pel
				
	return result

def convert_to_pil_image_1bpp(img_data, wdt, hgt):
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

def convert_to_pil_image_2bpp(img_data, wdt, hgt):
	palette = [255, 85, 170, 0]
	rows = (hgt + 3) // 4  # ceil(hgt/4)
	img = Image.new('L', (wdt, hgt))
	pixels = img.load()
	
	stride = wdt * rows
	
	for x in range(wdt):
		for y in range(rows):
			byte1 = img_data[(wdt*2) * y + (x*2)]
			byte2 = img_data[(wdt*2) * y + (x*2) + 1]
			
			for bit in range(8):
				y_pos = y*8 + bit
				if y_pos < hgt:
					bit1 = (byte1 >> bit) & 1
					bit2 = (byte2 >> bit) & 1
					value = (bit2 << 1) | bit1
					pixels[x, y_pos] = palette[value]

	return img

def read_tbl_info(file_path, start_offset, count):
	with open(file_path, 'rb') as f:
		f.seek(start_offset)
		
		for i in range(count):
			width, height = struct.unpack('<HH', f.read(4))
			
			params = struct.unpack('<I', f.read(4))[0]
			bitcount = (params >> 8) & 0xF
			is_present = (params >> 15) & 1
			frames = (params >> 16) & 0xFF
			speed = (params >> 24) & 0xFF
			
			offset, size, unknown = struct.unpack('<III', f.read(12))
			
			name = f.read(52).decode('utf-16-le').rstrip('\0')
			p_off = f.tell()
			name = f"{file_path}_{i}"
			
			if offset and size:
				f.seek(offset)
				for a in range(frames):
					size = struct.unpack("<H", f.read(2))[0]
					data = decompress_data(f.read(size), size, bitcount)
					try:
						if bitcount == 2:
							image = convert_to_pil_image_2bpp(data, width, height)
						else:
							image = convert_to_pil_image_1bpp(data, width, height)
						image.save(f"{name}_{a}.png")
					except:
						open(f"{name}_{a}.bin", "wb").write(data)
				f.seek(p_off)

file_path = sys.argv[1]
offset = int(sys.argv[2], 16)
count = int(sys.argv[3])
	
try:
	read_tbl_info(file_path, offset, count)
except Exception as e:
	print(f"Error: {str(e)}")