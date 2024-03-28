from pydantic import Field, BaseModel


class ClientInfo(BaseModel):
    host: str = "localhost"
    """服务端的地址"""
    port: int
    """服务端的端口"""
    account: str
    """bot 登录的账号"""
    ticket: str
    """bot 登录的凭证/密码"""


class Config(BaseModel):
    kritor_clients: list[ClientInfo] = Field(default_factory=list)
    """client 配置"""
    kritor_skip_auth: bool = False
    """是否跳过认证"""
