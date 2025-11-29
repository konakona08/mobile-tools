import lxml.etree
import os
import sys
from PIL import Image
import lxml.etree

if len(sys.argv) < 3:
	print(f"Not enough arguments! usage: {sys.argv[0]} xml_file ani_folder", file=sys.stderr)
	sys.exit(1)

ani_folder = sys.argv[2]
config = lxml.etree.parse(sys.argv[1]).getroot()
basepath = os.path.dirname(sys.argv[1])

'''
<CAInfo>
  <PowerAnimationParameters>
    <PowerAnim description="PowerOn" width="240" height="320" num_frames="20" frame_delay="100" />
    <PowerAnim description="PowerOff" width="240" height="320" num_frames="9" frame_delay="100" />
  </PowerAnimationParameters>
</CAInfo>
'''

powerani_parms = config.xpath('//CAInfo/PowerAnimationParameters')[0]
for powerani in powerani_parms:
  if powerani.get('description') == 'PowerOn':
    filename = "poweron.gif"
    src = "LG_poweron.bin"
  elif powerani.get('description') == 'PowerOff':
    filename = "poweroff.gif"
    src = "LG_poweroff.bin"
  else:
    continue

  wdt = int(powerani.get('width'))
  hgt = int(powerani.get('height'))
  num_frames = int(powerani.get('num_frames'))
  frame_delay = int(powerani.get('frame_delay'))

  frames = []
  frames_file = ani_folder + "/" + src
  try:
    ff = open(frames_file, "rb")
    for i in range(num_frames):
      fdata = ff.read(wdt*hgt*2)
      frame = Image.frombytes("RGB", (wdt,hgt), bytes(fdata),"raw", "BGR;16")
      frames.append(frame)
    ff.close()
    #create gif
    frames[0].save(f"{ani_folder}/{filename}", save_all=True, append_images=frames[1:], optimize=False, duration=frame_delay, loop=None, disposal=False)
  except:
    print(f"Failed to open {frames_file}", file=sys.stderr)
    continue