import wave
import math
import struct
import os

def create_sound(filename, frequency, duration, volume=0.5, fade_out=True):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            val = math.sin(2 * math.pi * frequency * t)
            
            # Simple fade out
            if fade_out:
                val *= (1 - i / n_samples)
            
            # Scale to 16-bit integer
            val = int(val * volume * 32767)
            wav_file.writeframes(struct.pack('h', val))

def create_move_sound():
    # Short "thock" sound
    create_sound('assets/sounds/move.wav', 200, 0.1, volume=0.6)

def create_win_sound():
    # Victory arpeggio-ish
    create_sound('assets/sounds/win.wav', 440, 0.5, volume=0.5)

def create_flip_sound():
    # Higher pitched "swish"
    create_sound('assets/sounds/flip.wav', 600, 0.05, volume=0.3)

if __name__ == "__main__":
    if not os.path.exists('assets/sounds'):
        os.makedirs('assets/sounds')
    create_move_sound()
    create_win_sound()
    create_flip_sound()
    print("Sounds generated in assets/sounds/")
