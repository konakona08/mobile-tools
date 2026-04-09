import struct
import sys
import os
from io import BytesIO
from PIL import Image

start_marker = "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
end_marker = "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x6e\0\x75\0\x6c\0\x6c\0\x2d\0\x69\0\x6d\0\x67\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
def decompress_data(data, size, bpp, w , h):
	if isinstance(data, bytearray) or isinstance(data, bytes):
		data = BytesIO(data)
		
	result = bytearray(w*h)
	idx = 0
	while data.tell() < size:
		p = struct.unpack("<B", data.read(1))[0]
		is_packed = p&0x80
		cnt = p&0x7f
		if is_packed:
			pel = data.read(bpp)
			for i in range(cnt+2):
				result[idx:idx+bpp] = pel
				idx += bpp
		else:
			pel = data.read((cnt+1)*bpp)
			result[idx:idx+(cnt+1)*bpp] = pel
			idx += (cnt+1)*bpp
				
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

def read_tbl_info(file_path, start_offset, count, out_folder):
	if not os.path.exists(out_folder):
		os.makedirs(out_folder)
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
			
			name_alt = f.read(52).decode('utf-16-le').rstrip('\0')
			p_off = f.tell()
			file_name = os.path.basename(file_path)
			name = f"{file_name}_{i}"
			
			if offset and size:
				f.seek(offset)
				for a in range(frames):
					size = struct.unpack("<H", f.read(2))[0]
					data = decompress_data(f.read(size), size, bitcount, width, height)
					try:
						if bitcount == 2:
							image = convert_to_pil_image_2bpp(data, width, height)
						else:
							image = convert_to_pil_image_1bpp(data, width, height)
						image.save(f"{out_folder}/{name}_{a}.png")
					except Exception as e:
						print(f"Error: {str(e)}")
				f.seek(p_off)

file_path = sys.argv[1]
if len(sys.argv) > 2:
	out_folder = sys.argv[2]
else:
	out_folder = os.path.dirname(file_path)
#find start_marker in file
with open(file_path, 'rb') as f:
	fdata = f.read()
	start_offset = fdata.find(bytes(start_marker, 'utf-8'))+72
	end_offset = fdata.find(bytes(end_marker, 'utf-8'))
	count = (end_offset - start_offset) // 72
	print(f"Found {count} images")
	f.close()

try:
	read_tbl_info(file_path, start_offset, count, out_folder)
except Exception as e:
	print(f"Error: {str(e)}")