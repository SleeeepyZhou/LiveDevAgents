from camel.models import FishAudioModel

import os
import json
with open('key.json', 'r') as f:
    config = json.load(f)
os.environ["FISHAUDIO_API_KEY"] = config['fish_key']

audio_models = FishAudioModel()
def s2t(audio_file_path: str):
    return audio_models.speech_to_text(audio_file_path)

import pyaudio
import wave
import threading

FORMAT = pyaudio.paInt16  # 采样位数
CHANNELS = 1              # 单声道
RATE = 44100              # 采样率
CHUNK = 1024              # 数据块大小
RECORD_SECONDS = 5        # 录音时长（秒）
WAVE_OUTPUT_FILENAME = "output.wav"

recording = False
frames = []

def record_audio():
    global recording, frames
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    
    print("开始录音...")
    recording = True
    
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("结束录音")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def start_recording():
    global recording, frames
    recording = False
    frames = []
    threading.Thread(target=record_audio).start()

def convert_to_text():
    global recording
    recording = False
    
    while len(threading.enumerate()) > 1:
        pass
    
    text = s2t(WAVE_OUTPUT_FILENAME)
    return text

# if __name__ == "__main__":
#     start_recording()
#     import time
#     time.sleep(RECORD_SECONDS)
#     text = convert_to_text()
#     print(text)