from typing import Optional

from control_server.src.web_settings import WebSettings


class TestSettings:
    """
    Test-specific settings. Used to, for example, give tests a way of finding
    what the endpoint prefix is by reading the WebSettings.
    """

    def __init__(self):
        self.web_settings: Optional[WebSettings] = None
        self.initialized = False

    def init(self):
        if self.initialized:
            return

        self.initialized = True
        self.web_settings = WebSettings().read()


# Load test settings once
test_settings = TestSettings()


def get_prefix():
    """
    Gets the prefix from the loaded test settings
    :return: The control server endpoint prefix
    """
    test_settings.init()
    return test_settings.web_settings.prefix
