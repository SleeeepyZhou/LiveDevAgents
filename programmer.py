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

import json
with open('key.json', 'r') as f:
    config = json.load(f)
qwen_key = config['qwen_api_key']

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYGAME_FILE = os.path.join(CURRENT_DIR, 'pygame_current.py')

def create_agent():
    """创建一个新的agent实例"""
    model = ModelFactory.create(
        model_platform=ModelPlatformType.QWEN,
        model_type=ModelType.QWEN_TURBO,
        api_key = qwen_key,
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
    elif sys.platform == 'win32':  # Windows
        os.system("taskkill /F /FI \"IMAGENAME eq python.exe\" /FI \"WINDOWTITLE eq pygame_current.py\"")

class MyInterpreter(SubprocessInterpreter):
    def __init__(self):
        super().__init__(require_confirm=False, print_stdout=True, print_stderr=True)
        self.initial_code = """
# 初始化pygame
pygame.init()

# 创建窗口
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame Window")

# 初始化时钟
clock = pygame.time.Clock()
FPS = 60

# 游戏主循环
running = True
while running:
    # 控制帧率
    clock.tick(FPS)
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 在这里添加游戏逻辑

    # 更新显示
    pygame.display.flip()

# 退出游戏
pygame.quit()
"""
        # 如果pygame文件存在，读取它的内容作为stored_code
        if os.path.exists(PYGAME_FILE):
            with open(PYGAME_FILE, 'r', encoding='utf-8') as f:
                self.stored_code = f.read()
        else:
            self.stored_code = self.initial_code
            
        self.current_process = None
        
    def run(self, code: str, code_type: str):
        if 'pygame' in code:
            try:
                # 先终止所有现有的pygame进程
                kill_pygame()
                
                # 如果有正在运行的进程，先终止它
                if self.current_process is not None:
                    self.current_process.terminate()
                    self.current_process.join()
                
                # 将新代码添加到存储的代码中
                self.stored_code = code
                
                # 创建固定位置的文件来运行pygame代码
                with open(PYGAME_FILE, 'w', encoding='utf-8') as f:
                    # 写入基础框架代码
                    f.write("""
# -*- coding: utf-8 -*-
import pygame
import sys
import random

# 初始化pygame
pygame.init()

# 设置窗口大小
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Window")

# 初始化时钟
clock = pygame.time.Clock()
FPS = 60

try:
    # 用户的游戏代码
""")
                    # 添加用户的代码，确保缩进正确
                    user_code_lines = self.stored_code.split('\n')
                    indented_code = '\n'.join(['    ' + line if line.strip() else line for line in user_code_lines])
                    f.write(indented_code)
                    
                    # 添加错误处理和清理代码
                    f.write("""

except Exception as e:
    error_msg = f"Pygame错误: {str(e)}"
    print(error_msg)
    pygame.quit()
    sys.exit(1)

finally:
    pygame.quit()
    sys.exit()
""")
                
                # 启动新进程运行pygame代码
                self.current_process = multiprocessing.Process(target=run_pygame_file, args=(PYGAME_FILE,))
                self.current_process.start()
                
                # 等待一小段时间检查进程是否正常启动
                import time
                time.sleep(0.5)

                if not self.current_process.is_alive():
                    # 如果进程已经结束，说明出现了错误
                    return "ERROR: 代码执行失败，需要重新生成代码"
                
                return "SUCCESS: Pygame程序已在新进程中启动"
                
            except Exception as e:
                error_msg = f"ERROR: {str(e)}"
                return error_msg
        else:
            try:
                result = super().run(code, code_type)
                return result
            except Exception as e:
                error_msg = f"ERROR: {str(e)}"

                return error_msg


from flask import Flask, request, jsonify
from queue import Queue

input_queue = Queue()

is_running = False
app = Flask(__name__)
@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.json
    user_input = data.get('command')
    if not user_input:
        return jsonify({"error": "No command provided"}), 400
    input_queue.put(user_input)
    return jsonify({"message": "Command received"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    global is_running
    if is_running:
        return 'System Status: OK', 200
    else:
        return 'System Status: NO', 500

import threading

def main():
    global is_running
    # 创建interpreter实例来保存代码历史
    interpreter = MyInterpreter()
    while True:
        try:
            is_running = False
            user_input = input_queue.get()
            is_running = True

            if user_input.lower() == 'quit':
                break

            # 每次都创建新的agent
            agent = create_agent()
            
            # 构建包含历史代码的消息
            message = ""
            if os.path.exists(PYGAME_FILE):
                with open(PYGAME_FILE, 'r', encoding='utf-8') as f:
                    current_code = f.read()
                    # 提取主要代码部分（去掉import和事件循环部分）
                    code_lines = current_code.split('\n')
                    main_code = []
                    for line in code_lines:
                        if not line.strip().startswith(('import', 'running =', 'clock =', 'while', 'for event', 'pygame.display.flip()', 'clock.tick', '# 清理', 'pygame.quit()')):
                            main_code.append(line)
                    message = "以下是之前的代码:\n```python\n" + '\n'.join(main_code) + "\n```\n\n"
                    message += "请在这个代码基础上,所有的移动速度都要保持帧率稳定.如果需要图像资源,其在./res/文件夹下.不破坏之前的功能前提下.增加以下需求:\n"
            message += user_input
            
            #print(message)
            #print("以上是历史代码==========")
            
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
    server_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})
    server_thread.daemon = True
    server_thread.start()

    main()
