# Agent 弹幕游戏开发引擎

本项目使用[CAMEL](https://github.com/camel-ai/camel)构建。为2024.12 CAMEL-AI Hackathon项目。
Developers: Rex, SleeeepyZhou, Stargaze

## Start

克隆仓库
`git clone https://github.com/SleeeepyZhou/LiveDevAgents.git`

请将此json文件内容对应键值改为自己的apikey，并将文件改名为key.json
![](./assets/key_example.png)

#### Gradio demo
![](./assets/gradio_demo.png)

配置好环境后，先启动`programmer.py`，再启动`gradio_demo.py`。

#### Blive

直播中控由Godot构建，使用[BliveChat](https://github.com/xfgryujk/blivechat)项目抓取弹幕。BliveChat 的弹幕转发插件，位于`./contorl/relay_plugin`，详细请见[直播中控](./contorl/readme.md)。

##### 仍在开发中

![](./assets/live.png)