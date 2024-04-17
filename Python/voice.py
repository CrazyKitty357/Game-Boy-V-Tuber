import pyaudio
import numpy as np
import struct
import noisereduce as nr
from pynput.keyboard import Key, Controller

keyboard = Controller()
key_to_press = 'z'  # Specify the key to press and hold

# Define variables for pressed and released numbers
pressed_threshold = 50
released_threshold = 5

def main():
    chunk = 1024 * 4  # Increased chunk size for better noise profile
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    device_index = 1  # Replace with the correct device ID for your microphone

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True,
                    frames_per_buffer=chunk, input_device_index=device_index)

    key_is_pressed = False
    # Record a few seconds of noise to calculate a noise profile
    noise_frames = []
    for i in range(0, int(rate / chunk * 2)):  # Adjust this for longer noise profile
        noise_data = stream.read(chunk)
        noise_frames.append(np.frombuffer(noise_data, dtype=np.int16))

    noise_profile = np.concatenate(noise_frames)

    try:
        while True:
            data = stream.read(chunk)
            audio_data = np.frombuffer(data, dtype=np.int16)
            # Reduce noise
            reduced_noise = nr.reduce_noise(y=audio_data, sr=rate, stationary=True, y_noise=noise_profile)

            volume = np.linalg.norm(reduced_noise) / np.sqrt(chunk)
            print(f"Volume: {volume:.2f}")

            if volume > pressed_threshold and not key_is_pressed:
                keyboard.press(key_to_press)
                key_is_pressed = True
                print("Key pressed")
            elif volume <= released_threshold and key_is_pressed:
                keyboard.release(key_to_press)
                key_is_pressed = False
                print("Key released")
    except KeyboardInterrupt:
        pass
    finally:
        if key_is_pressed:
            keyboard.release(key_to_press)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == '__main__':
    main()
