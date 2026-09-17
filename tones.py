"""Finite, peak-limited mono PCM alarm sounds. Strong tones sustain their envelope."""
import math
import struct

RATE = 22050


def synthesize(tone, volume):
    volume = max(0, min(100, volume)) / 100
    strong = tone in ('Bip tegas', 'Bel nyaring', 'Sirene')
    notes = {'Lembut': [523.25, 659.25, 523.25],
             'Ceria': [523.25, 659.25, 783.99, 659.25],
             'Bip tegas': [880, 880, 1174.66],
             'Bel nyaring': [1046.5, 1318.51, 1567.98],
             'Sirene': [750, 750, 750]}[tone]
    duration = .65 if strong else .32
    output = bytearray()
    for _ in range(3 if strong else 2):
        for hz in notes:
            for i in range(int(RATE * duration)):
                t = i / RATE
                edge = min(1, t / .015, (duration - t) / .025)
                if tone == 'Sirene':
                    phase = 2 * math.pi * (750 * t + 450 * t * t / (2 * duration))
                else:
                    phase = 2 * math.pi * hz * t
                value = math.sin(phase)
                if strong:
                    value = .8 * value + .2 * math.sin(3 * phase)
                    envelope = edge * (math.exp(-t * 1.5) if tone == 'Bel nyaring' else 1)
                else:
                    envelope = edge * max(0, 1 - t / duration) ** 2
                amplitude = 30000 if strong else 16000
                output.extend(struct.pack('<h', int(amplitude * volume * envelope * value)))
            output.extend(b'\x00\x00' * int(RATE * .09))
    return bytes(output)
