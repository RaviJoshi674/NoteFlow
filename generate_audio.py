import wave
import math
import struct

def generate_sine_wave_file(filename="test_audio_valid.wav", duration=1.0, freq=440.0):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    amplitude = 16000
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)
            
    print(f"Generated valid audio file: {filename}")

if __name__ == "__main__":
    generate_sine_wave_file()
