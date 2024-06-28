# 主要功能

* 根据缺少的角色进行更新
* 检测缺少的汉化文件更新
* 可使用游戏token进行更新

# 使用说明
---

运行前新建一个`update_server.ini`文件, 添加以下内容

```ini
[github]
repo = yuyumoko/OtogiFrontierResources
branch = main
token = 
```

# 使用代理

如果下载太慢, 可以修改 `update_config.ini` 文件中的 `http_proxy` 来指定代理

例如:

```ini
[config]
http_proxy = http://127.0.0.1:1080

```