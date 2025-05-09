from tones import SINE_WAVE, SAWTOOTH_WAVE
from tones.mixer import Mixer
import enum
import os
import sys
import struct

# Beep converter
# multimedia\audio\avs\src\snd.h
SND_SILENCE = 0
SND_CALLBACK_SILENCE = 1
SND_STOP = 2
SND_RPT = 3
SND_RPT1 = 4
SND_RPT_NOCALLBACK = 5
SND_LOOP_BACK2 = 6
SND_LABEL = 7
SND_BACK_TO_LABEL = 8
SND_VOL_SCALE = 9
SND_LAST_CONTROL_TONE = 10
# to save py file space, use a predef table
tdb_file = open(os.path.join(os.path.dirname(__file__), "qcm_tdb"), "rb")

def mono_2_wav(fd):
	mixer = Mixer(44100, 0.5)
	mixer.create_track(0, SINE_WAVE, attack=0.0009, decay=0.0009) #DTMF Freq 1
	mixer.create_track(1, SINE_WAVE, attack=0.0009, decay=0.0009) #DTMF Freq 2

	loop_offs = 0
	looper_cnt = 0
	looper_entries = 0
	is_looped = False
	stop = False #SND_STOP, SND_RPT1, SND_RPT and SND_RPT_NOCALLBACK will trigger this
	loop_ending_offs = 0 
	while stop == False:
		if is_looped == False:
			looper_cnt = 1
			looper_entries = 1
		for p in range(looper_cnt):
			if is_looped == True:
				fd.seek(loop_offs)
			for q in range(looper_entries):
				val = struct.unpack('<H', fd.read(2))[0]
				ms = struct.unpack('<H', fd.read(2))[0]
				if val == SND_STOP or val == SND_RPT or val == SND_RPT_NOCALLBACK: # we won't repeat the tones
					stop = True
					break
				#ditto (value in range SND_LAST_CONTROL_TONE -> SND_FIRST_TONE or val over SND_LAST_TONE)
				if (val >= 10 and val <= 1000) or val >= 1089: 
					stop = True
					break
				if val == SND_LABEL:
					loop_offs = fd.tell()
				if val == SND_BACK_TO_LABEL:
					looper_entries = int(((fd.tell() - loop_offs)/4))-1
					loop_ending_offs = fd.tell()
					looper_cnt = ms
					is_looped = True
				if val == SND_LOOP_BACK2: #Loop back 2 items
					looper_entries = 2
					loop_offs = fd.tell() - 12
					loop_ending_offs = fd.tell()
					looper_cnt = ms
					is_looped = True
				if val == SND_SILENCE or val == SND_CALLBACK_SILENCE:
					mixer.add_silence(0, duration=ms/1000)
					mixer.add_silence(1, duration=ms/1000)
				if val >= 1001: # SND_0
					tdb_file.seek((val-1001)*4)
					frq1 = struct.unpack('<H', tdb_file.read(2))[0]
					frq2 = struct.unpack('<H', tdb_file.read(2))[0]
					mixer.add_tone(0, frequency=frq1, duration=ms/1000)
					mixer.add_tone(1, frequency=frq2, duration=ms/1000)
		if looper_cnt > 1 and p == looper_cnt-1:
			is_looped = False
			fd.seek(loop_ending_offs)
		if is_looped == True and looper_cnt == 1:
			is_looped = False
			fd.seek(loop_ending_offs) 
	return mixer

def calc_midi_sz(fd):
	sz = 0
	if fd.read(4) == b"MThd":
		sz += 14
		fd.read(10)
		while fd.read(4) == b"MTrk":
			tsz = struct.unpack(">L", fd.read(4))[0]
			fd.read(tsz)
			sz += tsz+8
	
	return sz

if len(sys.argv) < 2:
	print(f"Not enough arguments! usage: {sys.argv[0]} file offs cnt", file=sys.stderr)
	sys.exit(1)

fd = open(sys.argv[1], "rb")
sz = os.path.getsize(sys.argv[1])
offs = int(sys.argv[2], 16)
cnt = int(sys.argv[3], 10)
fd.seek(offs)
if not (os.path.exists(sys.argv[1] + "_ext")):	os.mkdir(sys.argv[1] + "_ext")	
for i in range(cnt):
	fd.seek(offs+(4*i))
	offset = struct.unpack("<L", fd.read(4))[0]
	print(f"tbl item {i}: offs: {hex(offset)}")
	if offset != 0:
		fd.seek(offset)
		ring_type, r_offs = struct.unpack("<LL", fd.read(8))
		print(f"ring type: {ring_type}, offs: {hex(r_offs)}")
		if (r_offs < sz):
			if ring_type == 0:
				fd.seek(r_offs)
				mono_2_wav(fd).write_wav(f"{sys.argv[1]}_ext/{i}.wav")
			if ring_type == 2:
				fd.seek(r_offs)
				d_sz = calc_midi_sz(fd)
				fd.seek(r_offs)
				open(f"{sys.argv[1]}_ext/{i}.mid", "wb").write(fd.read(d_sz))
		else:
			continue