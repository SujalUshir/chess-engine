import wave
import struct
import math
import os

os.makedirs("sounds", exist_ok=True)

def generate_tone(filename, freq, duration=0.2):
    sample_rate = 44100
    amplitude = 16000

    wav_file = wave.open(filename, "w")
    wav_file.setparams((1, 2, sample_rate, 0, "NONE", "not compressed"))

    for i in range(int(sample_rate * duration)):
        value = int(amplitude * math.sin(2 * math.pi * freq * (i / sample_rate)))
        data = struct.pack("<h", value)
        wav_file.writeframesraw(data)

    wav_file.close()

generate_tone("sounds/move.wav", 600)
generate_tone("sounds/capture.wav", 300)
generate_tone("sounds/check.wav", 900)

print("Sound files created in sounds folder!")