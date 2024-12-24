from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType

import json
with open('key.json', 'r') as f:
    config = json.load(f)

qwen_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-32B-Instruct",
    api_key=config['modelscope_apikey'],
    url="https://api-inference.modelscope.cn/v1",
    model_config_dict=QwenConfig(temperature=0.2).as_dict(),
)

sys_msg = '''
- Role: 产品经理
- Background: 你被指派负责将游戏设计师提供的游戏规则和框架转化为具体的编程方案。游戏引擎默认使用pygame
- Profile: 你是一名在游戏开发领域拥有深厚经验的产品经理。你对游戏开发流程有着深入的理解，确保程序员能明确的理解每一个编程任务的具体规则。
- Goals: 根据游戏设计文档，识别关键功能和需求，制定详细的技术实现方案，确保程序员能明确的理解每一个编程任务的具体规则。
- Constrains: 编程方案需遵循最佳实践，确保代码的可维护性和可扩展性。同时，必须在预算和时间范围内完成任务。
- OutputFormat: 技术具体编译方案。
- Workflow:
1. 与游戏策划师会面，详细理解游戏规则和设计理念。
2. 制定技术规格说明书，包括功能细节和优先级排序。
3. 输出程序应该做的编程任务列表，
4. 根据编程顺序只将这些具体编程任务按照用数组包装输出。输出应格式化为符合以下数组的格式。例如["创建角色类:实现角色类，可以通过方向键移动。"]
'''

from camel.agents import ChatAgent

manager = ChatAgent(
    system_message=sys_msg,
    model = qwen_model,
    message_window_size=10, # [Optional] the length for chat memory
    output_language = 'Chinese'
)