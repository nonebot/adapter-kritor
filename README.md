<div align="center">

# NoneBot-Adapter-Kritor

_✨ NoneBot2 Kritor Protocol适配器 / Kritor Protocol Adapter for NoneBot2 ✨_

</div>

> [!NOTE]
> Kritor 项目目前处于开发阶段, 所定义的 proto api 可能会有较大变动
> 
> 若出现异常情况请确定本仓库使用的 kritor api 与所对接的协议端使用的 kritor api 是否相同

## 协议介绍

[Kritor Protocol](https://github.com/KarinJS/kritor)

### 协议端

目前提供了 `kritor` 协议实现的有：
- [Lagrange.Kritor](https://github.com/LagrangeDev/Lagrange.Kritor)
- Shamrock


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
    "port": xxx,
    "account": "xxx",
    "ticket": "xxx"
  }
]
'
KRITOR_SKIP_AUTH=false
```

其中，

- `host`: 服务端的地址，默认为 localhost
- `port`: 服务端的端口
- `account`: bot 登录的账号
- `ticket`: bot 登录用的凭证/密码
- `KRITOR_SKIP_AUTH`: 若协议端未启用鉴权功能，则启用此配置项。此时 `ticket` 留空即可。

### 以对接 Lagrange.Kritor 为例

首先按照 [Lagrange.Kritor](https://github.com/LagrangeDev/Lagrange.Kritor) 的 README 进行配置。进行下一步前你应当已经创建好了 `appsettings.json`:

```json5
// appsettings.json
{
    "Logging": {
        "LogLevel": {
            // Log level, please modify to `Trace` when providing feedback on issues
            "Default": "Information"
        }
    },
    "Core": {
        "Protocol": {
            // Protocol platform, please modify according to the Signer version
            // Type: String ("Windows", "MacOs", "Linux")
            // Default: "Linux"
            "Platform": "Linux",
            "Signer": {
                // Signer server url
                // Type: String (HTTP URL, HTTPS URL)
                "Url": "",
                // Signer server proxy
                // Type: String (HTTP URL)
                "Proxy": ""
            }
        },
        "Server": {
            // Whether to automatically reconnect to the TX server
            // Type: bool
            // Default: false
            "AutoReconnect": true,
            // Whether to get optimum server
            // Type: bool
            // Default: false
            "GetOptimumServer": true
        }
    },
    "Kritor": {
        "Network": {
            // Address of the Kritor service binding
            // Type: String (ip)
            "Address": "0.0.0.0",
            // Port of the Kritor service binding
            // Type: Number ([1-65535])
            "Port": 9000
        },
        "Authentication": {
            // Whether to enable authentication
            // Type: bool
            "Enabled": false,
            // Ticket with maximum privileges
            // Type: String
            "SuperTicket": "",
            // Ticket list
            // Type: String[]
            "Tickets": []
        },
        "Message": {
            // Whether to ignore your own messages
            // Type: bool
            "IgnoreSelf": false
        }
    }
}
```

对于配置项:
- `host` 与 `Kritor.Network.Address` 一致
- `port` 与 `Kritor.Network.Port` 一致
- 若 `Kritor.Authentication.Enabled` 为 true, 则 `ticket` 应存在于 `.SuperTicket` 或 `.Tickets` 中
- `account` 为你登录的账号


## 克隆

因为该仓库包含一个 submodule, 请使用以下命令克隆本仓库：

```bash
git clone --recursive https://github.com/nonebot/adapter-kritor.git
```

## 示例

```python
from nonebot import on_command
from nonebot.adapters.kritor import Bot
from nonebot.adapters.kritor.message import MessageSegment
from nonebot.adapters.kritor.permission import PRIVATE


matcher = on_command("test", permission=PRIVATE)

@matcher.handle()
async def handle_receive(bot: Bot):
    await bot.send(event, MessageSegment.text("Hello, world!"))
```
