# adapter-kritor
NoneBot2 Kritor 协议适配器 / Kritor Protocol adapter for nonebot2

> [!NOTE]
> Kritor 项目目前处于开发阶段, 所定义的 proto api 可能会有较大变动
> 
> 若出现异常情况请确定本仓库使用的 kritor api 与所对接的协议端使用的 kritor api 是否相同

## 配置

修改 NoneBot 配置文件 `.env` 或者 `.env.*`。

### Driver

因本适配器基于 `gRPC`，Nonebot 没有现有的相关驱动器，所以驱动请直接写 `none`:


```dotenv
DRIVER=~none
```

### KRITOR_CLIENTS

配置机器人帐号，如：

```dotenv
KRITOR_CLIENTS='
[
  {
    "host": "xxx",
    "port": "xxx",
    "account": "xxx",
    "ticket": "xxx"
  }
]
'
```

其中，

- `host`: 服务端的地址，默认为 localhost
- `port`: 服务端的端口
- `account`: bot 登录的账号
- `ticket`: bot 登录用的凭证/密码


## 克隆

因为该仓库包含一个 submodule, 请使用以下命令克隆本仓库：

```bash
git clone --recursive https://github.com/nonebot/adapter-kritor.git
```
