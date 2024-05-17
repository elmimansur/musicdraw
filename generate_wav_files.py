import numpy as np
from scipy.io.wavfile import write
import os

# Define the sample rate and duration of the sound
sample_rate = 44100
duration = 1.0  # seconds

# Frequencies for the notes C, D, E, F, G, A, B (in Hz)
frequencies = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

def generate_sine_wave(frequency, sample_rate, duration):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

def save_wave(note, frequency):
    wave = generate_sine_wave(frequency, sample_rate, duration)
    # Ensure the sounds directory exists
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    # Save as a .wav file
    write(f"sounds/{note}.wav", sample_rate, wave.astype(np.float32))
    print(f"Saved {note}.wav")

for note, freq in frequencies.items():
    save_wave(note, freq)
