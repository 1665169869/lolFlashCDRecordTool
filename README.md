# lol Flash CD Record Tool

用于快捷方便的记录lol闪现CD，不涉及游戏进程的计时器。

使用说明可见软件内。

文件说明：

file|desc
-|-
./icon.ico|多帧icon
./icon.png|icon原图
./icon.psd|iconPS素材
./main.py|代码 后续将分割成若干个文件
./images/|图片资源
./bat/|bat/bash脚本 用于结束热键监控进程 脚本会在代码中自动生成
./error_log/|错误日志
./release/|封装好的可运行文件下载

目前已知bug:

1. 热键绑定失败或其他bug导致软件异常退出时，窗体不会被销毁，但是仍然会产生错误日志
