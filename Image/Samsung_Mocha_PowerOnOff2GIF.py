from Modules import INIReader
from Ctypes import compresslz
import os
import sys
from PIL import Image

if len(sys.argv) < 2:
	print(f"Not enough arguments! usage: {sys.argv[0]} file", file=sys.stderr)
	sys.exit(1)
	
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
	assert(config.has_element("PowerOnOffAniInit","PowerOnAniDelay") == True)
	assert(config.has_element("PowerOnOffAniInit","PowerOffAniDelay") == True)
	on_ani_delay = config.get_value("PowerOnOffAniInit","PowerOnAniDelay")
	off_ani_delay = config.get_value("PowerOnOffAniInit","PowerOffAniDelay")
	#SGH-U900 (O2UK)
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
		on_ani_main_fn = config.get_value("PowerOnOffAniInit","PowerOnAniPrefix")[0]
		for t in range(int(on_ani_main_frames)):
			data_size = os.path.getsize(f"{basepath}\\Image\\{on_ani_main_fn}{t}")
			data = open(f"{basepath}\\Image\\{on_ani_main_fn}{t}", "rb").read()
			fsz = os.path.getsize(f"{basepath}\\Image\\{on_ani_main_fn}{t}")
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
		off_ani_main_fn = config.get_value("PowerOnOffAniInit","PowerOffAniPrefix")[0]
		for t in range(int(off_ani_main_frames)):
			data_size = os.path.getsize(f"{basepath}\\Image\\{off_ani_main_fn}{t}")
			data = open(f"{basepath}\\Image\\{off_ani_main_fn}{t}", "rb").read()
			fsz = os.path.getsize(f"{basepath}\\Image\\{off_ani_main_fn}{t}")
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
		on_ani_sub_fn = config.get_value("PowerOnOffAniInit","PowerOffSubAniPrefix")[0]
		for t in range(int(on_ani_sub_frames)):
			data_size = os.path.getsize(f"{basepath}\\Image\\{on_ani_sub_fn}{t}")
			data = open(f"{basepath}\\Image\\{on_ani_sub_fn}{t}", "rb").read()
			fsz = os.path.getsize(f"{basepath}\\Image\\{on_ani_sub_fn}{t}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_sub,height_sub), bytes(unp_data),"raw", "BGR;16")
				on_ani_sub_frames_dec.append(im)
			else:
				on_ani_sub_frames_dec.append(on_ani_sub_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {on_ani_sub_frames} (duration={int(on_ani_delay[t])}ms)")
		on_ani_sub_frames_dec[0].save(f"{basepath}\\subpoweron.gif", save_all=True, append_images=on_ani_sub_frames_dec[1:], optimize=False, duration=on_ani_delay, loop=0, disposal=False)
		print(f"On animation exported to {basepath}\\subpoweron.gif")
	
	if off_ani_sub_frames > 0:
		print(f"Off animation frames:{off_ani_sub_frames}")
		off_ani_sub_frames_dec = []
		off_ani_sub_fn = config.get_value("PowerOnOffAniInit","PowerOffSubAniPrefix")[0]
		for t in range(int(off_ani_sub_frames)):
			data_size = os.path.getsize(f"{basepath}\\Image\\{off_ani_sub_fn}{t}")
			data = open(f"{basepath}\\Image\\{off_ani_sub_fn}{t}", "rb").read()
			fsz = os.path.getsize(f"{basepath}\\Image\\{off_ani_sub_fn}{t}")
			if fsz > 0:
				unp_data = clz_lib.unpack(data,data_size,False)
				im = Image.frombytes("RGB", (width_sub,height_sub), bytes(unp_data),"raw", "BGR;16")
				off_ani_sub_frames_dec.append(im)
			else:
				off_ani_sub_frames_dec.append(off_ani_sub_frames_dec[t-1])
			print(f"Decoded frame {t+1} out of {off_ani_sub_frames} (duration={int(off_ani_delay[t])}ms)")
		off_ani_sub_frames_dec[0].save(f"{basepath}\\subpoweroff.gif", save_all=True, append_images=off_ani_sub_frames_dec[1:], optimize=False, duration=on_ani_delay, loop=0, disposal=False)
		print(f"Off animation exported to {basepath}\\subpoweroff.gif")