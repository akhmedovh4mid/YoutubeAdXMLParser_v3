from uiautomator2 import Device


class YoutubeApp:
    PACKAGE_NAME: str = "com.google.android.youtube"
    
    def __init__(self, device: Device) -> None:
        self.device = device

    def start(self) -> None:
        self.device.app_start(package_name=self.PACKAGE_NAME)

    def close(self) -> None:
        self.device.app_stop(package_name=self.PACKAGE_NAME)

    def open_link(self, link: str) -> None:
        self.device.shell(f'am start -a android.intent.action.VIEW -d "{link}"')
