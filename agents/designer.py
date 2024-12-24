from camel.configs import QwenConfig
from camel.models import ModelFactory, FishAudioModel
from camel.types import ModelPlatformType

qwen_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-32B-Instruct",
    api_key="***REMOVED***",
    url="https://api-inference.modelscope.cn/v1",
    model_config_dict=QwenConfig(temperature=0.5).as_dict(),
)

sys_msg = '''
- Role: 游戏策划师
- Background: 你已经是一个资深的游戏策划师了，你需要用最简洁的语言去输出游戏策划方案。
- Profile: 作为游戏策划师，你负责设计和平衡游戏的属性、规则和机制，确保游戏既有趣也有挑战性。
- Skills: 游戏设计、系统规划、规则编写、平衡调整。
- Goals: 设计一套完整的游戏属性和规则。
- Constrains: 设计的规则应既简单易懂，又具有足够的深度和复杂性，以保持玩家的兴趣和投入。
- OutputFormat: 游戏设计文档、规则手册、流程图、属性表。
- Workflow:
  1. 初步设计时一定要勤用搜索工具，准确了解用户需求
  2. 根据用户给予的游戏题材去制定相应的方案。
  3. 根据用户测试反馈，调整属性和规则的平衡性，优化游戏体验。
  4. 方案的具体元素有 具体基础操作形式 具体表现形式 具体基础属性 具体基础规则 具体基础元素等
'''

from camel.agents import ChatAgent
from camel.toolkits import MathToolkit, SearchToolkit, FunctionTool

audio_models = FishAudioModel()

designer = ChatAgent(
    system_message=sys_msg,
    model = qwen_model,
    tools = [
        *MathToolkit().get_tools(),
        FunctionTool(SearchToolkit().search_duckduckgo),
    ],
    message_window_size=20, # [Optional] the length for chat memory
    output_language = 'Chinese'
)

def ask_designer(prompt : str):
    response = designer.step(prompt)
    return response.msgs[0].content