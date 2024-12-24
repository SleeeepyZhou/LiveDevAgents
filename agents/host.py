from camel.configs import QwenConfig
from camel.models import ModelFactory, FishAudioModel
from camel.types import ModelPlatformType

import json
with open('key.json', 'r') as f:
    config = json.load(f)

qwen_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-32B-Instruct",
    api_key= config['modelscope_apikey'],
    url="https://api-inference.modelscope.cn/v1",
    model_config_dict=QwenConfig(temperature=0.5).as_dict(),
)

from camel.agents import ChatAgent
from camel.toolkits import SearchToolkit, FunctionTool

sys_msg = '''


'''

def call_programmer():
    pass

audio_models = FishAudioModel()

host = ChatAgent(
    system_message=sys_msg,
    model = qwen_model,
    tools = [
        FunctionTool(SearchToolkit().search_duckduckgo),
        FunctionTool(call_programmer),
    ],
    message_window_size=50, # [Optional] the length for chat memory
    output_language = 'Chinese'
)


import librosa
import time
import pygame
import numpy as np

from gradio_client import Client
client = Client("http://127.0.0.1:8120")

def my_tts(text):
    result = client.predict(text=text,api_name="/tts_fn")
    if result[0] == "Success":
        return result[1]
    else:
        return False

def tts_and_play_audio(text):
    tmp_audio_path = my_tts(text)
    if not tmp_audio_path:
        return
    pygame.mixer.init()
    pygame.mixer.music.load(tmp_audio_path)  
    pygame.mixer.music.set_volume(0.8) 

    x , sr = librosa.load(tmp_audio_path, sr=8000)

    x = x  - min(x)
    x = x  / max(x)
    x= np.log(x) + 1
    x = x  / max(x) * 1.2

    pygame.mixer.music.play()
    s_time = time.time()
    try:
        for _ in range(int(len(x) / 800)):
            it = x[int((time.time() - s_time) * 8000)+1]
            # print(it)
            if it < 0:
                it = 0
            with open("tmp.txt", "w") as f:
                f.write(str(float(it)))
            time.sleep(0.1)
    except:
        pass

    time.sleep(0.1)
    with open("tmp.txt", "w") as f:
        f.write("0")