# 直播中控

由Godot构建，使用 [BliveChat](https://github.com/xfgryujk/blivechat) on GitHub。

## BliveChat 的弹幕转发插件

### 功能说明

用于处理和转发B站弹幕，把收到的消息转为特定格式后转发至ws://127.0.0.1:8848/dm/{user}。你也可以自己实现B站弹幕的处理转发。

### 使用方法

将插件文件夹`relay_plugin`放入BliveChat项目下的`data/plugins/`目录中。