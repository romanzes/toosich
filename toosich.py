from xled_plus.samples.sample_setup import *

import colorsys

from pydub import AudioSegment

import numpy as np

from scipy.io.wavfile import read, write

import simpleaudio

import math

audio_path = "./monsters.mp3"
num_intervals = 10

class MusicEffect(Effect):
    def __init__(self, ctr, audio):
        super(MusicEffect, self).__init__(ctr)
        self.frame = 0
        self.calc_magnitudes(audio)

    def reset(self, numframes):
        self.pattern = self.ctr.make_solid_pattern(hsl_color(0.0, 1.0, 0.0))

    def getnext(self):
        pat = ctr.copy_pattern(self.pattern)
        for i in range(0, num_intervals):
            magnitude = self.magnitudes[self.frame, i]
            if magnitude <= 0:
                continue
            loudness = math.sqrt(magnitude) / math.sqrt(self.max_magnitude)
            if i == 0:
                print(loudness)
            for j in range(0, 21):
                index = i * 21 + j
                if j / 21 < loudness:
                    ctr.modify_pattern(pat, index, (255, 0, 0))
                else:
                    ctr.modify_pattern(pat, index, (0, 0, 255))
        self.frame += 1
        return pat

    def calc_magnitudes(self, audio):
        # Convert the audio data to a wave file
        audio.export('audio.wav', format='wav')

        # Read in the wave file using scipy.io.wavfile
        Fs, data = read('audio.wav')

        # Convert the audio data to a NumPy array
        audio = np.array(data, dtype=float)

        # Get the length of the audio data
        N = len(audio)

        # Perform the FFT on the audio data
        fft_out = np.fft.fft(audio)

        # Calculate the frequencies for each element in the FFT output
        frequencies = np.fft.fftfreq(N, 1/Fs)

        # Calculate the length of the audio in frames
        audio_length = len(audio) / Fs * self.preferred_fps

        # Generate equal frequency intervals from 0 Hz to the maximum frequency
        max_freq = np.max(frequencies)
        intervals = np.linspace(0, max_freq, num_intervals+1)

        # Calculate the maximum magnitude
        self.max_magnitude = np.max(np.abs(fft_out))

        # Initialize the 2D array with zeros
        magnitudes = np.zeros((int(audio_length), num_intervals))

        Ff = Fs / self.preferred_fps

        # Iterate over the time intervals
        for i in range(int(audio_length)):
            # Select the audio data for the current time interval
            interval_data = audio[int(i*Ff):int((i+1)*Ff)]

            # Perform the FFT on the interval data
            interval_fft = np.fft.fft(interval_data)

            # Recalculate the frequencies for the interval data
            interval_freqs = np.fft.fftfreq(len(interval_data), 1/Fs)

            # Iterate over the frequency intervals and calculate the average magnitude
            for j in range(num_intervals):
                low_freq = intervals[j]
                high_freq = intervals[j+1]
                selected_mags = np.abs(interval_fft[(interval_freqs >= low_freq) & (interval_freqs <= high_freq)])
                magnitudes[i, j] = np.mean(selected_mags)
        self.magnitudes = magnitudes

if __name__ == '__main__': 
    # Load the audio file
    audio = AudioSegment.from_mp3(audio_path)
    ctr = setup_control()
    ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
    eff = MusicEffect(ctr, audio)
    oldmode = ctr.get_mode()["mode"]
    eff.launch_rt()
    simpleaudio.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )
    print("Started continuous effect - press Return to stop it")
    input()
    eff.stop_rt()
    ctr.set_mode(oldmode)