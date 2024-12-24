from camel.agents import EmbodiedAgent
from camel.generators import SystemMessageGenerator as sys_msg_gen
from camel.interpreters import SubprocessInterpreter
from camel.messages import BaseMessage as bm
from camel.types import RoleType
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import QwenConfig
import os
import sys
import pygame
import multiprocessing

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYGAME_FILE = os.path.join(CURRENT_DIR, 'pygame_current.py')

def create_agent():
    """创建一个新的agent实例"""
    model = ModelFactory.create(
        model_platform=ModelPlatformType.QWEN,
        model_type=ModelType.QWEN_TURBO,
        api_key = "sk-e3fbfded802a4cda95d8d9d1dbaea8a8",
        url = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    )

    role = 'Programmer'
    task = 'Writing and executing codes with Python and pygame.'

    meta_dict = dict(role=role, task=task)
    role_tuple = (role, RoleType.EMBODIMENT)

    sys_msg = sys_msg_gen().from_dict(meta_dict=meta_dict, role_tuple=role_tuple)
    interpreter = MyInterpreter()
    
    return EmbodiedAgent(
        system_message=sys_msg,
        tool_agents=None,
        model=model,
        code_interpreter=interpreter,
        verbose=0
    )

def run_pygame_file(file_path):
    """在独立进程中运行pygame文件"""
    python = sys.executable
    os.system(f'{python} {file_path}')

def kill_pygame():
    """终止所有pygame相关的进程"""
    if sys.platform == 'darwin':  # macOS
        os.system("pkill -f pygame_current.py")

class MyInterpreter(SubprocessInterpreter):
    def __init__(self):
        super().__init__(require_confirm=False, print_stdout=True, print_stderr=True)
        self.initial_code = """
# 初始化pygame
pygame.init()

# 创建窗口（添加NOFRAME标志使窗口始终在最前面）
screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
pygame.display.set_caption("Pygame Window")

# 添加拖动功能变量
dragging = False
drag_offset_x = 0
drag_offset_y = 0
"""
        # 如果pygame文件存在，读取它的内容作为stored_code
        if os.path.exists(PYGAME_FILE):
            with open(PYGAME_FILE, 'r') as f:
                self.stored_code = f.read()
        else:
            self.stored_code = self.initial_code
            
        self.current_process = None
        
    def run(self, code: str, code_type: str):
        if 'pygame' in code:
            # 先终止所有现有的pygame进程
            kill_pygame()
            
            # 如果有正在运行的进程，先终止它
            if self.current_process is not None:
                self.current_process.terminate()
                self.current_process.join()
            
            # 将新代码添加到存储的代码中
            self.stored_code = code
            
            # 创建固定位置的文件来运行pygame代码
            with open(PYGAME_FILE, 'w') as f:
                f.write("""
import pygame
import sys
import os

""" + self.stored_code + """

# 添加事件处理
running = True
clock = pygame.time.Clock()
dragging = False
drag_offset_x = 0
drag_offset_y = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                dragging = True
                mouse_x, mouse_y = event.pos
                window_x, window_y = pygame.display.get_window_position()
                drag_offset_x = window_x - mouse_x
                drag_offset_y = window_y - mouse_y
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:  # 如果正在拖动
                mouse_x, mouse_y = event.pos
                new_x = mouse_x + drag_offset_x
                new_y = mouse_y + drag_offset_y
                os.environ['SDL_VIDEO_WINDOW_POS'] = f"{new_x},{new_y}"
                pygame.display.set_mode((800, 600), pygame.NOFRAME)  # 重新创建窗口以更新位置
    
    # 更新屏幕
    pygame.display.flip()
    clock.tick(60)

# 清理
pygame.quit()
""")
            
            # 在新进程中运行pygame代码
            self.current_process = multiprocessing.Process(
                target=run_pygame_file,
                args=(PYGAME_FILE,)
            )
            self.current_process.start()
            return f"Pygame程序已在新进程中启动"
        else:
            return super().run(code, code_type)

def main():
    # 创建interpreter实例来保存代码历史
    interpreter = MyInterpreter()
    
    while True:
        try:
            user_input = input("\n请输入您的指令 (输入'quit'退出): ")
            if user_input.lower() == 'quit':
                break

            # 每次都创建新的agent
            agent = create_agent()
            
            # 构建包含历史代码的消息
            message = ""
            if os.path.exists(PYGAME_FILE):
                with open(PYGAME_FILE, 'r') as f:
                    current_code = f.read()
                    # 提取主要代码部分（去掉import和事件循环部分）
                    code_lines = current_code.split('\n')
                    main_code = []
                    for line in code_lines:
                        if not line.strip().startswith(('import', 'running =', 'clock =', 'while', 'for event', 'pygame.display.flip()', 'clock.tick', '# 清理', 'pygame.quit()')):
                            main_code.append(line)
                    message = "以下是之前的代码:\n```python\n" + '\n'.join(main_code) + "\n```\n\n"
                    message += "请在这个代码基础上,不破坏之前的功能前提下.增加以下需求:\n"
            message += user_input
            
            print(message)
            print("以上是历史代码==========")
            
            # 创建消息并获取响应
            usr_msg = bm.make_user_message(
                role_name='user',
                content=message)

            response = agent.step(usr_msg)
            print("\n助手回复:")
            print(response.msg.content)
                
        except KeyboardInterrupt:
            print("\n程序已终止")
            break

if __name__ == '__main__':
    main()
