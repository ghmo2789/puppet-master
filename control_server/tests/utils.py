from typing import Optional

from control_server.src.web_settings import WebSettings


class TestSettings:
    def __init__(self):
        self.web_settings: Optional[WebSettings] = None
        self.initialized = False

    def init(self):
        if self.initialized:
            return

        self.initialized = True
        self.web_settings = WebSettings().read()


test_settings = TestSettings()


def get_prefix():
    test_settings.init()
    return test_settings.web_settings.prefix
