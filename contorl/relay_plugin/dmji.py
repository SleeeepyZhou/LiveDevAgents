import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from uvicorn import Config, Server

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, root_dir)

import blcsdk
from blcsdk.api import set_msg_handler, send_text
from blcsdk.handlers import BaseHandler

app = FastAPI()
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)
    async def send_inf(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    async def send_dm(self, message):
        for connection in self.active_connections:
            await connection.send_json(message,"binary")

manager = ConnectionManager()
@app.websocket("/dm/{user}")
async def websocket_endpoint(websocket: WebSocket):
    global DM_package
    await manager.connect(websocket)
    await manager.send_inf("来了！")
    try:
        while True:
            await websocket.receive_text()
            await manager.send_dm(DM_package)
            DM_package.clear()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.send_inf("用户离开")

DM_package = []
class DMtransmit(BaseHandler):
    def _on_add_text(self, client, message, extra):
        author = [
            message.privilege_type,
            message.medal_level,
            message.medal_name,
            message.author_name,
        ]

        content = [
            message.content,
            message.author_type
        ]

        to_control = {
            "type" : 0,
            "author" : author,
            "content" : content,
            "price" : 0,
        }
        DM_package.append(to_control)
        # print(to_control)
        """收到弹幕"""
    def _on_add_gift(self, client, message, extra):
        author = [
            message.privilege_type,
            message.medal_level,
            message.medal_name,
            message.author_name,
        ]
        content = [
            message.gift_name,
            message.num,
        ]

        to_control = {
            "type" : 2,
            "author" : author,
            "content" : content,
            "price" : message.total_coin,
        }
        DM_package.append(to_control)
        # print(to_control)
        """有人送礼"""
    def _on_add_member(self, client, message, extra):
        author = [
            message.privilege_type,
            message.medal_level,
            message.medal_name,
            message.author_name,
        ]
        content = [
            message.privilege_type,
            message.num,
            message.unit,
        ]

        to_control = {
            "type" : 3,
            "author" : author,
            "content" : content,
            "price" : message.total_coin,
        }
        DM_package.append(to_control)
        # print(to_control)
        """有人上舰"""
    def _on_add_super_chat(self, client, message, extra):
        author = [
            message.privilege_type,
            message.medal_level,
            message.medal_name,
            message.author_name,
        ]
        content = [
            message.content,
        ]

        to_control = {
            "type" : 1,
            "author" : author,
            "content" : content,
            "price" : message.price * 1000,
        }
        DM_package.append(to_control)
        # print(to_control)
        """醒目留言"""
    def on_client_stopped(self, client, exception):
        print("Client stopped.")

async def init_bclsdk():
    try:
        await blcsdk.init()
        set_msg_handler(DMtransmit())
        await manager.send_dm("Test~Test!!")
        
        # 关闭信号
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await blcsdk.shut_down()

async def main():
    task_bclsdk = asyncio.create_task(init_bclsdk())
    server = Server(Config(app, host="127.0.0.1", port=8848))
    task_fastapi = asyncio.create_task(server.serve())
    await asyncio.gather(task_bclsdk, task_fastapi)

if __name__ == "__main__":
    asyncio.run(main())