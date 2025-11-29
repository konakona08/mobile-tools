from Modules import INIReader
from Ctypes import compresslz
import os
import sys
from PIL import Image

if len(sys.argv) < 3:
	print(f"Not enough arguments! usage: {sys.argv[0]} file CSCsfs_folder", file=sys.stderr)
	sys.exit(1)

cscsfs = sys.argv[2]
config = INIReader.RegistryReader(sys.argv[1])
clz_lib = compresslz.CompressLZ()
basepath = os.path.dirname(sys.argv[1])
assert(config.has_category("Version") == True)
assert(config.get_value("Version", "Version")[0] >= 1)
assert(config.has_category("PlayAnimationType") == True)
assert(config.get_value("PlayAnimationType", "AnimationType")[0] == 'bmp')
assert(config.has_category("PowerOnOffAniInit") == True)
on_ani_main_frames = int(config.get_value("PowerOnOffAniInit","PowerOnAniFrame")[0])
off_ani_main_frames = int(config.get_value("PowerOnOffAniInit","PowerOffAniFrame")[0])
on_ani_sub_frames = int(config.get_value("PowerOnOffAniInit","PowerOnSubFrame")[0])
off_ani_sub_frames = int(config.get_value("PowerOnOffAniInit","PowerOffSubFrame")[0])
if on_ani_main_frames+off_ani_main_frames+on_ani_sub_frames+off_ani_sub_frames>0:
	on_ani_delay = []
	off_ani_delay = []
	for a in range(on_ani_main_frames):
		on_ani_delay.append(int(config.get_value("PowerOnOffAniInit",f"PowerOnAniDelay{a}")[0]))
	for a in range(off_ani_main_frames):
		off_ani_delay.append(int(config.get_value("PowerOnOffAniInit",f"PowerOffAniDelay{a}")[0]))

	if on_ani_main_frames > on_ani_sub_frames:
		for _ in range (on_ani_main_frames-on_ani_sub_frames):
			on_ani_delay.append(on_ani_delay[on_ani_sub_frames-1])
	if off_ani_main_frames > off_ani_sub_frames:
		for _ in range (off_ani_main_frames-off_ani_sub_frames):
			off_ani_delay.append(on_ani_delay[off_ani_sub_frames-1])

	if on_ani_sub_frames > on_ani_main_frames:
		for _ in range (on_ani_sub_frames-on_ani_main_frames):
			on_ani_delay.append(on_ani_delay[on_ani_main_frames-1])
	if off_ani_sub_frames > off_ani_main_frames:
		for _ in range (off_ani_sub_frames-off_ani_main_frames):
			off_ani_delay.append(on_ani_delay[off_ani_main_frames-1])

if on_ani_main_frames+off_ani_main_frames > 0:
	print("Main display:")
	assert(config.has_element("PowerOnOffAniInit","MainLCDWidth") == True)
	assert(config.has_element("PowerOnOffAniInit","MainLCDHeight") == True)
	width_main = int(config.get_value("PowerOnOffAniInit","MainLCDWidth")[0])
	height_main = int(config.get_value("PowerOnOffAniInit","MainLCDHeight")[0])
	print(f"Size:{width_main}x{height_main}")
	if on_ani_main_frames > 0:
		print(f"On animation frames:{on_ani_main_frames}")
		on_ani_main_frames_dec = []
		for t in range(int(on_ani_main_frames)):
			on_ani_main_fn = config.get_value("PowerOnOffAniInit",f"PowerOnAniImage{t}")[0]
			data_size = os.path.getsize(f"{cscsfs}\\{on_ani_main_fn}")
			data = open(f"{cscsfs}\\{on_ani_main_fn}", "rb").read()
			fsz = os.path.getsize(f"{cscsfs}\\{on_ani_main_fn}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_main,height_main), bytes(unp_data),"raw", "BGR;16")
				on_ani_main_frames_dec.append(im)
			else:
				on_ani_main_frames_dec.append(on_ani_main_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {on_ani_main_frames} (duration={int(on_ani_delay[t])}ms)")
			print(f"{basepath}\\Image\\{on_ani_main_fn}{t}")
		on_ani_main_frames_dec[0].save(f"{basepath}\\poweron.gif", save_all=True, append_images=on_ani_main_frames_dec[1:], optimize=False, duration=on_ani_delay, loop=0, disposal=False)
		print(f"On animation exported to {basepath}\\poweron.gif")
		
	if off_ani_main_frames > 0:
		print(f"Off animation frames:{off_ani_main_frames}")
		off_ani_main_frames_dec = []
		for t in range(int(off_ani_main_frames)):
			off_ani_main_fn = config.get_value("PowerOnOffAniInit",f"PowerOffAniImage{t}")[0]
			data_size = os.path.getsize(f"{cscsfs}\\{off_ani_main_fn}")
			data = open(f"{cscsfs}\\{off_ani_main_fn}", "rb").read()
			fsz = os.path.getsize(f"{cscsfs}\\{off_ani_main_fn}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_main,height_main), bytes(unp_data),"raw", "BGR;16")
				off_ani_main_frames_dec.append(im)
			else:
				off_ani_main_frames_dec.append(off_ani_main_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {off_ani_main_frames} (duration={int(off_ani_delay[t])}ms)")
		off_ani_main_frames_dec[0].save(f"{basepath}\\poweroff.gif", save_all=True, append_images=off_ani_main_frames_dec[1:], optimize=False, duration=on_ani_delay, loop=0, disposal=False)
		print(f"Off animation exported to {basepath}\\poweroff.gif")
		
if on_ani_sub_frames+off_ani_sub_frames > 0:
	print("Sub display:")
	assert(config.has_element("PowerOnOffAniInit","SubLCDWidth") == True)
	assert(config.has_element("PowerOnOffAniInit","SubLCDHeight") == True)
	width_sub = int(config.get_value("PowerOnOffAniInit","SubLCDWidth")[0])
	height_sub = int(config.get_value("PowerOnOffAniInit","SubLCDHeight")[0])
	print(f"Size:{width_sub}x{height_sub}")
	if on_ani_sub_frames > 0:
		print(f"On animation frames:{on_ani_sub_frames}")
		on_ani_sub_frames_dec = []
		for t in range(int(on_ani_sub_frames)):
			on_ani_sub_fn = config.get_value("PowerOnOffAniInit",f"PowerOnAniSubImage{t}")[0]
			data_size = os.path.getsize(f"{cscsfs}\\{on_ani_sub_fn}")
			data = open(f"{cscsfs}\\{on_ani_sub_fn}", "rb").read()
			fsz = os.path.getsize(f"{cscsfs}\\{on_ani_sub_fn}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_sub,height_sub), bytes(unp_data),"raw", "BGR;16")
				on_ani_sub_frames_dec.append(im)
			else:
				on_ani_sub_frames_dec.append(on_ani_sub_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {on_ani_sub_frames} (duration={int(on_ani_delay[t])}ms)")
		on_ani_sub_frames_dec[t].save(f"{basepath}\subpoweron.gif", save_all=True, append_images=on_ani_sub_frames_dec[1:], optimize=False, duration=on_ani_delay, loop=0, disposal=False)
	
	if off_ani_sub_frames > 0:
		print(f"Off animation frames:{off_ani_sub_frames}")
		off_ani_sub_frames_dec = []
		for t in range(int(off_ani_sub_frames)):
			off_ani_sub_fn = config.get_value("PowerOnOffAniInit",f"PowerOffAniSubImage{t}")[0]
			data_size = os.path.getsize(f"{cscsfs}\\{off_ani_sub_fn}")
			data = open(f"{cscsfs}\\{off_ani_sub_fn}", "rb").read()
			fsz = os.path.getsize(f"{cscsfs}\\{off_ani_sub_fn}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_sub,height_sub), bytes(unp_data),"raw", "BGR;16")
				off_ani_sub_frames_dec.append(im)
			else:
				off_ani_sub_frames_dec.append(off_ani_sub_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {off_ani_sub_frames} (duration={int(off_ani_delay[t])}ms)")
		off_ani_sub_frames_dec[0].save(f"{basepath}\\subpoweroff.gif", save_all=True, append_images=off_ani_sub_frames_dec[1:], optimize=False, duration=on_ani_delay, loop=0, disposal=False)
		print(f"Off animation exported to {basepath}\\subpoweroff.gif")