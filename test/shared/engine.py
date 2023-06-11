# pylint: skip-file

from fastcrawler.engine import ProxySetting


def get_proxy_setting():
    return ProxySetting(
        protocol="http://",
        server="185.199.229.156",
        port=7492,
        username="lovqqcio",
        password="81adfjrlwdoo"
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
