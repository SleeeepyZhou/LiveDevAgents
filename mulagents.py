from agents.worker import push_task
from agents.fish import start_recording, convert_to_text

from fastapi import FastAPI, BackgroundTasks
from typing import Dict
import uuid
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class CommandRequest(BaseModel):
    command: str

meetings: Dict[str, list] = {}
def meeting(res: str, task_id: str):
    todo_list = push_task(res)
    meetings[task_id] = todo_list
@app.post("/meeting")
async def ping(Re:CommandRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(meeting, Re.command, task_id)
    return task_id
@app.get("/check")
async def check_task(task_id: str):
    return meetings.get(task_id, False)

@app.get("/listen")
async def listen():
    start_recording()
convert_list = []
def converting(task_id):
    text = convert_to_text()
@app.get("/convert")
async def convert(background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(converting, task_id)
    return task_id

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8120)