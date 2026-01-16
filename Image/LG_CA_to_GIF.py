import lxml.etree
import os
import sys
from PIL import Image
import lxml.etree
import datetime

end_tag = "</PowerAnimationParameters>"

if len(sys.argv) < 3:
	print(f"Not enough arguments! usage: {sys.argv[0]} xml_file ani_folder", file=sys.stderr)
	sys.exit(1)

ani_folder = sys.argv[2]
# exclude other things than poweranimparameters, other stuff is useless
ani_data = open(sys.argv[1], 'r').read()
end_index = ani_data.find(end_tag)
assert end_index != -1, "Invalid XML, did you provide an LG CAInfo XML?"
our_stuff = ani_data[0:end_index+len(end_tag)]
our_stuff += "\r\n</CAInfo>"
# There's no way to get root of xml by fromstring, so create a tempfile
temp_filename = ani_folder + "/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S_temp.xml")
open(temp_filename, 'w').write(our_stuff)
config = lxml.etree.parse(temp_filename).getroot()
os.remove(temp_filename)
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