# pylint: skip-file

from pydantic_settings import BaseSettings

from fastcrawler.engine import ProxySetting


class Setting(BaseSettings):
    server: str
    port: int
    username: str
    password: str

    class Config:
        env_file = ".env"


setting = Setting()


def get_proxy_setting():
    return ProxySetting(
        protocol="http://",
        server=setting.server,
        port=setting.port,
        username=setting.username,
        password=setting.password
    )


def get_cookies():
    return [
        {
            "name": "cookie_name_1",
            "value": "cookie_value_1",
            "domain": "example.com",
            "path": "/",
            "expires": -1,
            "httpOnly": False,
            "secure": False,
        }
    ]
