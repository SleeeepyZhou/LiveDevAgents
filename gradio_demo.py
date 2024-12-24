from agents.worker import push_task
from agents.fish import start_recording, convert_to_text

import requests
def send_command(command):
    payload = {'command': command}
    try:
        response = requests.post('http://127.0.0.1:5000/execute', json=payload)
        response.raise_for_status()
        return "Push OK! "
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


import gradio as gr

global_task_output = []
with gr.Blocks() as demo:
    with gr.Column():
        task_input = gr.Textbox(label="输入讨论主题")
        task_button = gr.Button("开会讨论")
        task_output = gr.Textbox(label="讨论结果", value="等待输入...")
    task_button.click(push_task, inputs=task_input, outputs=task_output)
    
    with gr.Column():
        command_input = gr.Textbox(label="Input")
        command_button = gr.Button("程序干活")
        command_output = gr.Textbox(label="Out")
    command_button.click(send_command, inputs=command_input, outputs=command_output)


if __name__ == "__main__":
    demo.launch()
    # command = '显示helloworld'
    # result = send_command(command)
    # print(result)