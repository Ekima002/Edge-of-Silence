# This program estimates a person’s hearing threshold by playing tones at different frequencies 
# and volumes. The user listens and responds to each sound, and their hearing sensitivity is 
# recorded for each frequency. Results are saved in a CSV file with a timestamp.
# Note: Because different devices may produce slightly different sounds, these results are best 
# used to track how one person's hearing changes over time — not to compare between people or systems.

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from datetime import datetime
import csv

# Frequency setup
f_raw = np.array([
    0.0063, 0.0079, 0.0100, 0.0126, 0.0158, 0.0199, 0.0251, 0.0315, 0.0397,
    0.0500, 0.0629, 0.0792, 0.0998, 0.1256, 0.1581, 0.1991, 0.2506, 0.3155, 0.3972,
    0.5000, 0.6295, 0.7924, 0.9976, 1.2559, 1.5811, 1.6, 1.7
])
frequency = 1e4 * f_raw
num_freqs = len(frequency)

# Amplitude setup
decades_a = np.arange(np.log10(0.0001), np.log10(10)+0.001, 0.333)
amplitude = 10 ** decades_a

amp_curve = np.zeros_like(frequency)
fs = 44100
duration = 10  # seconds
t = np.linspace(0, duration, int(fs * duration))

# Randomized frequency sweep
freq_order = np.random.permutation(num_freqs)

for idx, f_idx in enumerate(freq_order):
    f = frequency[f_idx]
    print(f"\nNow playing random frequency {idx+1}/{num_freqs}")

    for a in amplitude:
        y = a * np.sin(2 * np.pi * f * t)
        sd.play(y, fs, blocking=False)

        while True:
            userinput = input('Press "n" if you don’t hear anything, "y" if you do: ').strip().lower()
            if userinput == 'n':
                sd.stop()
                break  # Try next amplitude
            elif userinput == 'y':
                sd.stop()
                amp_curve[f_idx] = a
                break  # Move to next frequency
            else:
                print("Invalid input. Please press 'n' or 'y'. Sound continues...")

        if amp_curve[f_idx] > 0:
            break # Move to next frequency

power_curve = amp_curve ** 2

# Plotting
plt.figure()
plt.loglog(frequency, power_curve, 'o-')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power (Amplitude²)')
plt.title('Threshold Power vs Frequency')
plt.grid(True)
plt.tight_layout()
plt.show()

# Save to CSV file
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"HearingThreshold_{timestamp}.csv"
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Frequency_Hz", "Threshold_Power"])
    for f, p in zip(frequency, power_curve):
        writer.writerow([f, p])

print(f"Results saved to {filename}")
