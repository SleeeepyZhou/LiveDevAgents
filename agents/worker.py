from agents.designer import designer
from agents.manager import manager

from camel.models import ModelFactory, FishAudioModel

audio_models = FishAudioModel()

from camel.agents import ChatAgent
from camel.configs import QwenConfig
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.tasks import Task
from camel.toolkits import FunctionTool, SearchToolkit
from camel.types import ModelPlatformType, ModelType
from camel.societies.workforce import Workforce

import json
with open('key.json', 'r') as f:
    config = json.load(f)

coordinator_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-32B-Instruct",
    api_key=config['modelscope_apikey'],
    url="https://api-inference.modelscope.cn/v1",
    model_config_dict=QwenConfig(temperature=0.2).as_dict(),
)

task_agent_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-32B-Instruct",
    api_key=config['modelscope_apikey'],
    url="https://api-inference.modelscope.cn/v1",
    model_config_dict=QwenConfig(temperature=0.2).as_dict(),
)

function_list = [
    *SearchToolkit().get_tools(),
]

new_agent_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-32B-Instruct",
    api_key=config['modelscope_apikey'],
    url="https://api-inference.modelscope.cn/v1",
    model_config_dict=QwenConfig(temperature=0.2).as_dict(),
)

workforce = Workforce(
    'Game development company',
    coordinator_agent_kwargs={"model": coordinator_model},
    task_agent_kwargs={"model": task_agent_model},
    new_worker_agent_kwargs={"model": new_agent_model, "tools": function_list},
)

workforce.add_single_agent_worker(
    '资深单机游戏策划师，负责游戏属性和机制设计平衡，依游戏题材制定方案，据玩家反馈调整，含多种元素，可写低成本优化方案。',
    worker=designer,
).add_single_agent_worker(
    '游戏开发领域拥有深厚经验的产品经理，负责将游戏策划师提供的游戏规则和框架转化为具体的编程方案',
    worker=manager,
)

import json

def push_task(text, proj_content = "") -> list:
    task = Task(
        content=text+ "最后仅输出产品经理给出的任务表数组。",
        additional_info=proj_content,
        id="0",
    )

    task = workforce.process_task(task)

    answer = task.result
    start_index = answer.find('[')
    end_index = answer.find(']', start_index)
    json_array_str = answer[start_index:end_index + 1]
    task_list = json.loads(json_array_str)

    return task_list

