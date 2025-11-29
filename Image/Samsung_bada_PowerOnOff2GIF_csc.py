import lxml.etree
from Ctypes import compresslz
import os
import sys
from PIL import Image
import lxml.etree

FPS_MS = 83

if len(sys.argv) < 3:
	print(f"Not enough arguments! usage: {sys.argv[0]} xml_file csc_folder", file=sys.stderr)
	sys.exit(1)

cscsfs = sys.argv[2]
config = lxml.etree.parse(sys.argv[1]).getroot()
clz_lib = compresslz.CompressLZ()
basepath = os.path.dirname(sys.argv[1])
on_ani_main_frames = int(config.xpath('//CustomerData/Settings/Main/Display')[0].find('NbPowerOnAnim').text)
off_ani_main_frames = int(config.xpath('//CustomerData/Settings/Main/Display')[0].find('NbPowerOffAnim').text)

if on_ani_main_frames+off_ani_main_frames > 0:
	on_ani_frames = config.xpath('//CustomerData/Settings/Main/Display/PowerOnAnim')
	off_ani_frames = config.xpath('//CustomerData/Settings/Main/Display/PowerOffAnim')
	width_main = int(on_ani_frames[0].get('width'))
	height_main = int(on_ani_frames[0].get('height'))
	print(f"Size:{width_main}x{height_main}")
	if on_ani_main_frames > 0:
		print(f"On animation frames:{on_ani_main_frames}")
		on_ani_main_frames_dec = []
		for t in range(int(on_ani_main_frames)):
			on_ani_main_fn = on_ani_frames[t].get('src').replace("bmp", "img")
			data_size = os.path.getsize(f"{cscsfs}\\{on_ani_main_fn}")
			data = open(f"{cscsfs}\\{on_ani_main_fn}", "rb").read()
			fsz = os.path.getsize(f"{cscsfs}\\{on_ani_main_fn}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_main,height_main), bytes(unp_data),"raw", "BGR;16")
				on_ani_main_frames_dec.append(im)
			else:
				on_ani_main_frames_dec.append(on_ani_main_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {on_ani_main_frames} (duration={FPS_MS}ms)")
			print(f"{basepath}\\Image\\{on_ani_main_fn}{t}")
		on_ani_main_frames_dec[0].save(f"{basepath}\\poweron.gif", save_all=True, append_images=on_ani_main_frames_dec[1:], optimize=False, duration=FPS_MS, loop=0, disposal=False)
		print(f"On animation exported to {basepath}\\poweron.gif")
		
	if off_ani_main_frames > 0:
		print(f"Off animation frames:{off_ani_main_frames}")
		off_ani_main_frames_dec = []
		for t in range(int(off_ani_main_frames)):
			off_ani_main_fn = off_ani_frames[t].get('src').replace("bmp", "img")
			data_size = os.path.getsize(f"{cscsfs}\\{off_ani_main_fn}")
			data = open(f"{cscsfs}\\{off_ani_main_fn}", "rb").read()
			fsz = os.path.getsize(f"{cscsfs}\\{off_ani_main_fn}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_main,height_main), bytes(unp_data),"raw", "BGR;16")
				off_ani_main_frames_dec.append(im)
			else:
				off_ani_main_frames_dec.append(off_ani_main_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {off_ani_main_frames} (duration={FPS_MS}ms)")
		off_ani_main_frames_dec[0].save(f"{basepath}\\poweroff.gif", save_all=True, append_images=off_ani_main_frames_dec[1:], optimize=False, duration=FPS_MS, loop=0, disposal=False)
		print(f"Off animation exported to {basepath}\\poweroff.gif")