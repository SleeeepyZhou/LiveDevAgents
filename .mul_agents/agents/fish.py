from camel.models import FishAudioModel

import os
os.environ["FISHAUDIO_API_KEY"] = "***REMOVED***"

audio_models = FishAudioModel()

import pyaudio
import wave
import time
import threading

def s2t(audio_file_path: str):
    return audio_models.speech_to_text(audio_file_path)

def record_audio(RECORD_SECONDS=3, WAVE_OUTPUT_FILENAME="temp.mp3"):
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    # 记录指定的秒数
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

        # 检测空闲，这里简单模拟，实际应用中需要更复杂的算法
        if not data:
            print("检测到空闲，停止录音...")
            break

    print("录音结束。")

    # 停止录音
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return s2t(WAVE_OUTPUT_FILENAME)

# 启动录音线程
thread = threading.Thread(target=record_audio)
thread.start()
thread.join()