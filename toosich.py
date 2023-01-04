from xled_plus.samples.sample_setup import *

import colorsys

from pydub import AudioSegment
from pydub.scipy_effects import band_pass_filter

from playsound import playsound

audio_path = "./monsters.mp3"

# Load the audio file
audio = AudioSegment.from_mp3(audio_path)

bands = []

class MusicEffect(Effect):
    def __init__(self, ctr):
        super(MusicEffect, self).__init__(ctr)
        self.time = 0

    def reset(self, numframes):
        self.pattern = self.ctr.make_solid_pattern(hsl_color(0.0, 1.0, 0.0))

    def update_band(self, pat, time_start, time_end, index):
        slice = bands[index][time_start:time_end]
        loudness = slice.max / bands[index].max_possible_amplitude
        r, g, b = colorsys.hsv_to_rgb(loudness, 1.0, 1.0)
        for i in range(index * 21, (index + 1) * 21):
            ctr.modify_pattern(pat, i, (int(r * 255), int(g * 255), int(b * 255)))

    def getnext(self):
        time_elapsed = 1000.0 / self.preferred_fps
        pat = ctr.copy_pattern(self.pattern)
        time_start = self.time
        time_end = self.time + time_elapsed
        self.update_band(pat, time_start, time_end, 0)
        self.update_band(pat, time_start, time_end, 1)
        self.update_band(pat, time_start, time_end, 2)
        self.update_band(pat, time_start, time_end, 3)
        self.update_band(pat, time_start, time_end, 4)
        self.update_band(pat, time_start, time_end, 5)
        self.update_band(pat, time_start, time_end, 6)
        self.update_band(pat, time_start, time_end, 7)
        self.update_band(pat, time_start, time_end, 8)
        self.update_band(pat, time_start, time_end, 9)
        self.time += time_elapsed
        return pat

def init_bands():
    print("Filtering band 1")
    bands.append(audio.band_pass_filter(20, 2000))
    print("Filtering band 2")
    bands.append(audio.band_pass_filter(2000, 4000))
    print("Filtering band 3")
    bands.append(audio.band_pass_filter(4000, 6000))
    print("Filtering band 4")
    bands.append(audio.band_pass_filter(6000, 8000))
    print("Filtering band 5")
    bands.append(audio.band_pass_filter(8000, 10000))
    print("Filtering band 6")
    bands.append(audio.band_pass_filter(10000, 12000))
    print("Filtering band 7")
    bands.append(audio.band_pass_filter(12000, 14000))
    print("Filtering band 8")
    bands.append(audio.band_pass_filter(14000, 16000))
    print("Filtering band 9")
    bands.append(audio.band_pass_filter(16000, 18000))
    print("Filtering band 10")
    bands.append(audio.band_pass_filter(18000, 20000))

if __name__ == '__main__':
    init_bands()
    ctr = setup_control()
    ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
    eff = MusicEffect(ctr)
    oldmode = ctr.get_mode()["mode"]
    eff.launch_rt()
    playsound(sound = audio_path, block = False)
    print("Started continuous effect - press Return to stop it")
    input()
    eff.stop_rt()
    ctr.set_mode(oldmode)