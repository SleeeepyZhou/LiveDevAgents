# 直播中控

由[Godot](https://github.com/godotengine/godot)构建，使用 [BliveChat](https://github.com/xfgryujk/blivechat) 获取弹幕信息。

仍在开发，暂时不提供应用程序，建议使用Godot4.3打开此project。

## BliveChat 的弹幕转发插件

### 功能说明

用于处理和转发B站弹幕，把收到的消息转为特定格式后转发至ws://127.0.0.1:8848/dm/{user}。你也可以自己实现B站弹幕的处理转发。

### 使用方法

将插件文件夹`relay_plugin`放入BliveChat项目下的`data/plugins/`目录中。