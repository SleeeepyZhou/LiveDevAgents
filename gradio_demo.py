from agents.worker import push_task
from agents.fish import start_recording, convert_to_text

import requests
def send_command(command : str):
    payload = {'command': command}
    try:
        response = requests.post('http://127.0.0.1:5000/execute', json=payload)
        response.raise_for_status()
        return f"正在完成{command}喵~"
    except requests.exceptions.RequestException as e:
        return f"出错了喵~: {e}"

todo_list = []
current_index = 0

def a_meeting(command):
    global current_index, todo_list
    todo_list = push_task(command)
    current_index = 0
    return todo_list

def process_task():
    global current_index, todo_list
    if current_index < len(todo_list):
        result = send_command(todo_list[current_index])
        current_index += 1
        return result
    else:
        return "已经干完了喵~"

import gradio as gr
with gr.Blocks() as demo:
    with gr.Column():
        task_input = gr.Textbox(label="输入讨论主题")
        task_button = gr.Button("开会讨论")
        task_output = gr.JSON(label="讨论结果")
    task_button.click(a_meeting, inputs=task_input, outputs=task_output)
    
    with gr.Column():
        command_input = gr.Textbox(label="Input")
        command_button = gr.Button("程序干活")
        list_button = gr.Button("工作表")
        command_output = gr.Textbox(label="Out")
    command_button.click(send_command, inputs=command_input, outputs=command_output)
    list_button.click(process_task,outputs=command_output)


if __name__ == "__main__":
    demo.launch()